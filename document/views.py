# from django.shortcuts import render
from document.docx_handler import *
from django.shortcuts import render, redirect, reverse
from document.models import DocxInit, ContentStorage, SignatureStorage
import os
from django.http import HttpResponse
import datetime
from pytz import timezone as pytz_timezone
import json
import math
from urllib import parse
from django.utils import timezone
from ManagementSystem.settings import TIME_ZONE
from user.views import check_authority, check_is_touch_capable, check_accessible
# from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.views.decorators.csrf import csrf_exempt
import zipfile
import pandas as pd
import numpy as np
import base64
import hashlib
from Cryptodome.Cipher import AES
from team.models import Team
from django.db.models import Q
from django.utils.safestring import mark_safe


time_zone = pytz_timezone(TIME_ZONE)


def document(request):
    return render(request, "paperless.html")


def introduce_docx(request):
    return render(request, "introduce_docx.html")


def error_docx_closed(request):
    return render(request, "error_docx_closed.html")


def error_docx_opened(request):
    return render(request, "error_docx_opened.html")


def error_docx_missing(request):
    return render(request, "error_docx_missing.html")


def check_datetime_closed(close_timezone, now_timezone):
    return True if close_timezone <= now_timezone else False


def translate_words(request, error=''):
    if request.method == "GET":
        translate_dict = json.load(open(translate_path, "r"))
        return render(request, "translate_words.html", {"translate_dict": translate_dict, "error": error})
    else:
        if request.user.is_superuser:
            translate_before = request.POST.get("translate_before", "")
            translate_after = request.POST.get("translate_after", "")
            if translate_before == "" or translate_after == "":
                return redirect(reverse("translate_words", args=["输入为空"]))
            if not re.search(r'^[_a-zA-Z0-9\u4e00-\u9fa5]+$', translate_before) or not re.search(r'^[_a-zA-Z0-9\u4e00-\u9fa5]+$', translate_after):
                return redirect(reverse("translate_words", args=["输入含有空格或特殊字符"]))
            translate_dict = json.load(open(translate_path, "r"))
            translate_dict[translate_before] = translate_after
            json.dump(translate_dict, open(translate_path, "w"))
            return redirect(reverse("translate_words"))
        else:
            return render(request, "error_400.html", status=400)


def delete_translate_words(request):
    if request.method == "GET":
        if request.user.is_superuser:
            word = request.GET.get("word", "")
            if word == "":
                return render(request, "error_400.html", status=400)
            translate_dict = json.load(open(translate_path, "r"))
            try:
                del(translate_dict[word])
                json.dump(translate_dict, open(translate_path, "w"))
                return redirect(reverse("translate_words"))
            except:
                return render(request, "error_400.html", status=400)
        else:
            return render(request, "error_400.html", status=400)
    else:
        return render(request, "error_400.html", status=400)


@check_authority
def select_template(request, info=''):
    if request.method == "GET":
        templates_list = os.listdir(source_dir)
        templates_list = [file_name.split(".")[0] for file_name in templates_list]
        return render(request, "select_template.html", {"templates_list": templates_list, "info": info})
    else:
        return render(request, "error_400.html", status=400)


@check_authority
def delete_template(request):
    if request.method == "POST":
        template_name = request.POST.get("delete_template", "")
        if template_name == "":
            return render(request, "error_403.html", status=403)
        source_path = os.path.join(source_dir, template_name + ".docx")
        template_path = os.path.join(templates_dir, template_name + ".docx")
        for path in [source_path, template_path]:
            os.remove(path)
        return redirect(reverse("select_template", args=["删除 %s 成功" % template_name]))
    else:
        return render(request, "error_400.html", status=400)


@check_authority
def init_docx(request):
    if request.method == "POST":
        template_name = request.POST.get("select_template", "")
        if template_name == "":
            return render(request, "error_403.html", status=403)
        source_path = source_dir + template_name + '.docx'
        document_handler_docx, _ = create_docx_handler(source_path, 'python-docx')
        document_handler_template, _ = create_docx_handler(templates_dir + template_name + '.docx', 'python-docx')
        variable_dict = get_variable_list(document_handler_template, '_', -1, r'[a-z0-9]+_i[a-z]_')
        docx_html = docx_to_html(source_path)
        if not request.user.is_superuser:
            team_id = str(request.user.team.id)
            team_list = list(Team.objects.filter(related_parent__in=team_id).values("id", "name", "parent__name"))
        else:
            team_list = list(Team.objects.all().values("id", "name", "parent__name"))
        return render(request, "init_docx.html", {"template_name": template_name, "docx_html": docx_html, "variable_dict": variable_dict, "team_list": team_list})
    else:
        return render(request, "error_400.html", status=400)


@check_authority
def write_init_docx(request, template_name):
    if request.method == "POST":
        params = request.POST.dict()
        docx_name = params["docx_name"]
        close_datetime = params['close_datetime']
        close_datetime = time_zone.localize(datetime.datetime.strptime(close_datetime, "%Y-%m-%dT%H:%M"))
        team_id_list = request.POST.getlist("team")
        del(params['docx_name'])
        del(params['csrfmiddlewaretoken'])
        del(params['close_datetime'])
        if len(team_id_list) > 0:
            del(params['team'])
        content = json.dumps(params)
        docx_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        docx_init_object = DocxInit.objects.create(id=docx_id, user=request.user, template_name=template_name, docx_name=docx_name, content=content, close_datetime=close_datetime)
        if len(team_id_list) > 0:
            team_id_list = [int(i) for i in team_id_list]
            for team_id in team_id_list:
                team_object = Team.objects.get(id=team_id)
                docx_init_object.team.add(team_object)
        return redirect(reverse("view_docx", args=[docx_id]))
    else:
        return render(request, "error_400.html", status=400)


@check_authority
def view_docx_list(request):
    if request.method == "GET":
        docx_list = DocxInit.objects.values("id", "user__last_name", "user__first_name", "template_name", "docx_name", "version", "create_datetime", "edit_datetime", "close_datetime").order_by('-id')[:12]
        return render(request, "view_docx_list.html", {"docx_list": docx_list})
    else:
        return render(request, "error_400.html", status=400)


def split_list_by_n(list_collection, n):
    for i in range(0, len(list_collection), n):
        yield list_collection[i: i + n]


@check_authority
@check_accessible(DocxInit)
def view_docx(request, docx_id, info=""):
    if request.method == "GET":
        docx_object = DocxInit.objects.filter(id=docx_id)
        if len(docx_object) == 0:
            return render(request, "error_403.html", status=403)
        docx_dict = docx_object.values("id", "user__last_name", "user__first_name", "template_name", "docx_name", "content", "version", "create_datetime", "edit_datetime", "close_datetime")[0]
        closed = check_datetime_closed(timezone.localtime(docx_dict["close_datetime"]), timezone.localtime(timezone.now()))
        document_handler, document_template_handler = create_docx_handler(templates_dir + docx_dict["template_name"] + ".docx", "")
        content_variable_dict = get_variable_list(document_handler, '_', -1, r'[a-z0-9]+_n[a-z]_\d+')
        supervisor_variable_dict = get_variable_list(document_handler, '_', -1, r'[a-z0-9]+_s[a-z]_')
        docx_signature_queryset = SignatureStorage.objects.filter(docx__id=docx_id)
        docx_signature_list = list(docx_signature_queryset.values("content", "signature"))
        for content in docx_signature_list:
            if content['content'].split("_")[0] in supervisor_variable_dict.keys():
                del(supervisor_variable_dict[content['content'].split("_")[0]])
        if len(content_variable_dict) == 0:
            return render(request, "error_403.html", status=403)
        need_signature = content_variable_dict.__contains__("signature")
        docx_content_queryset = ContentStorage.objects.filter(docx__id=docx_id)
        if docx_content_queryset.filter(user__id=request.user.id).count() > 0:
            filled = True
            signed = True if docx_content_queryset.filter(user__id=request.user.id)[0].signature != "" else False
        else:
            filled, signed = False, False
        if need_signature:
            del(content_variable_dict["signature"])
        return render(request, "view_docx.html", {"docx_dict": docx_dict, "content_variable_dict": content_variable_dict, "need_signature": need_signature, "filled": filled, "signed": signed, "closed": closed, "supervisor_variable_dict": supervisor_variable_dict, "info": info})
    else:
        return render(request, "error_400.html", status=400)


@check_authority
def show_docx_html(request):
    docx_id = request.GET['docx_id']
    docx_object = DocxInit.objects.filter(id=docx_id)
    if len(docx_object) == 0:
        return
    docx_dict = docx_object.values("template_name", "content")[0]
    document_handler, document_template_handler = create_docx_handler(templates_dir + docx_dict["template_name"] + ".docx", "")
    count_variable_dict = get_variable_list(document_handler, '_', -1, r'[a-z0-9]+_a[a-z]_')
    docx_signature_queryset = SignatureStorage.objects.filter(docx__id=docx_id)
    docx_signature_list = list(docx_signature_queryset.values("content", "signature"))
    docx_signature_list = None if len(docx_signature_list) == 0 else docx_signature_list
    content_variable_dict = get_variable_list(document_handler, '_', -1, r'[a-z0-9]+_n[a-z]_\d+')
    maximum = int(content_variable_dict[list(content_variable_dict.keys())[0]]["maximum"]) + 1
    docx_content_queryset = ContentStorage.objects.filter(docx__id=docx_id)
    content_count = docx_content_queryset.values().count()
    docx_path = storage_dir + docx_id + "_%s.docx"
    docx_html_list = []
    if docx_content_queryset.filter(user__id=request.user.id).count() > 0:
        filled = True
    else:
        filled = False
    if content_count > 0:
        if len(count_variable_dict) > 0:
            auto_variable_dict = {}
            data = pd.DataFrame([json.loads(i['content']) for i in list(docx_content_queryset.values("content"))])
            data = data[list(count_variable_dict.keys())].apply(pd.to_numeric)
            for key, value in count_variable_dict.items():
                auto_variable_dict[value['origin']] = str(sum(data[key]))
            auto_variable_dict = json.dumps(auto_variable_dict)
        else:
            auto_variable_dict = None
        if maximum == 1:
            if filled:
                user_docx_content_list = docx_content_queryset.filter(user__id=request.user.id).values("content", "signature")
                write(document_template_handler, docx_path % 1, docx_dict["content"], user_docx_content_list, content_variable_dict, auto_variable_dict, docx_signature_list, maximum)
            else:
                write(document_template_handler, docx_path % 1, docx_dict["content"])
            docx_html_list.append(docx_to_html(docx_path % 1))
        docx_content_list = docx_content_queryset.values("content", "signature").order_by('id')
        docx_content_list = split_list_by_n(docx_content_list, maximum)
        page = math.ceil(content_count / maximum) + 1
        for i in range(1, page):
            if page > 2:
                _, document_template_handler = create_docx_handler(templates_dir + docx_dict["template_name"] + ".docx", "python-docx-template")
            write(document_template_handler, docx_path % i, docx_dict["content"], docx_content_list.__next__(), content_variable_dict, auto_variable_dict, docx_signature_list, maximum)
            if maximum != 1:
                docx_html_list.append(docx_to_html(docx_path % i))
        docx_html = ''.join(docx_html_list)
    else:
        write(document_template_handler, docx_path % 1, docx_dict["content"])
        docx_html = docx_to_html(docx_path % 1)
    return HttpResponse(mark_safe(docx_html))


def decrypt(data, key):
    aes = AES.new(key.encode(), AES.MODE_ECB)
    decrypted_text = aes.decrypt(base64.decodebytes(bytes(data, encoding='utf8'))).decode("utf8")
    decrypted_text = decrypted_text[:-ord(decrypted_text[-1])]  # 去除多余补位
    return decrypted_text


@check_authority
@check_is_touch_capable
@check_accessible(DocxInit)
def fill_docx(request, docx_id, need_signature):
    if request.method == "POST":
        try:
            docx_object = DocxInit.objects.get(id=docx_id)
        except:
            return render(request, "error_docx_missing.html", status=403)
        if check_datetime_closed(timezone.localtime(docx_object.close_datetime), timezone.localtime(timezone.now())):
            return render(request, "error_docx_closed.html", status=403)
        params = request.POST.dict()
        del(params["csrfmiddlewaretoken"])
        exist_content = ContentStorage.objects.filter(docx__id=docx_id, user__id=request.user.id)
        if exist_content.count() > 0:
            content_id = exist_content[0].id
        else:
            content = json.dumps(params)
            content_id = docx_id + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            ContentStorage.objects.create(id=content_id, docx=docx_object, user=request.user, content=content)
        if need_signature:
            return render(request, "signature.html", {"docx_id": content_id[:14], "content_id": content_id[15:], "signature_key": ""})
        else:
            return redirect(reverse("view_docx", args=[docx_id]))
    else:
        return render(request, "error_400.html", status=400)


@check_authority
def fill_signature(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        try:
            docx_id = request_data["docx_id"]
            docx_object = DocxInit.objects.get(id=docx_id)
        except:
            return render(request, "error_docx_missing.html", status=403)
        if check_datetime_closed(timezone.localtime(docx_object.close_datetime), timezone.localtime(timezone.now())):
            return render(request, "error_docx_closed.html", status=403)
        signature_data = parse.unquote(decrypt(request_data["data"], request_data["key"]))
        # signature_data = parse.unquote(request_data["data"])
        ContentStorage.objects.filter(id=docx_id + '_' + request_data["content_id"]).update(signature=signature_data)
        return redirect(reverse("view_docx", args=[docx_id]))
    else:
        return render(request, "error_400.html", status=400)


@check_authority
@check_is_touch_capable
def supervise_docx(request):
    if request.method == "GET":
        docx_id = request.GET.get("docx_id", "")
        signature_key = request.GET.get("signature_key", "")
        if docx_id == "" or signature_key == "":
            return render(request, "error_403.html", status=403)
        try:
            docx_object = DocxInit.objects.get(id=docx_id)
        except:
            return render(request, "error_docx_missing.html", status=403)
        if not check_datetime_closed(timezone.localtime(docx_object.close_datetime), timezone.localtime(timezone.now())):
            return render(request, "error_docx_opened.html", status=403)
        return render(request, "signature.html", {"docx_id": docx_id, "content_id": "", "signature_key": signature_key})
    else:
        return render(request, "error_400.html", status=400)


@check_authority
def supervisor_signature(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        try:
            docx_id = request_data["docx_id"]
            docx_object = DocxInit.objects.get(id=docx_id)
        except:
            return render(request, "error_docx_missing.html", status=403)
        signature_key = request_data["signature_key"]
        signature_data = parse.unquote(decrypt(request_data["data"], request_data["key"]))
        # signature_data = parse.unquote(request_data["data"])
        signature_content_id = docx_id + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        SignatureStorage.objects.create(id=signature_content_id, docx=docx_object, user=request.user, content=signature_key, signature=signature_data)
        return redirect(reverse("view_docx", args=[docx_id]))
    else:
        return render(request, "error_400.html", status=400)


@check_authority
def close_docx(request, docx_id):
    if request.method == "GET":
        if request.user.is_superuser:
            close_datetime = timezone.localtime(timezone.now()) - datetime.timedelta(minutes=1)
            DocxInit.objects.filter(id=docx_id).update(close_datetime=close_datetime)
            return redirect(reverse("view_docx", args=[docx_id]))
        else:
            return render(request, "error_400.html", status=400)
    else:
        return render(request, "error_400.html", status=400)


@check_authority
def preview_template(request):
    if request.method == "GET":
        template_name = request.GET['template_name']
        try:
            docx_html = docx_to_html(source_dir + template_name + '.docx')
            if len(docx_html) > 0:
                return HttpResponse(docx_html)
            else:
                return HttpResponse('无预览!')
        except:
            return HttpResponse("模板出现问题，无法预览！")
    else:
        return render(request, "error_400.html", status=400)


def zip_docx(files_path_list: list, save_path):
    f = zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED)
    for file_name, file_path in files_path_list:
        f.write(file_path, file_name)
    f.close()


@check_authority
def download_docx(request, docx_id):
    if request.method == "GET":
        docx_list = [(docx, os.path.join(storage_dir, docx)) for docx in os.listdir(storage_dir) if docx.startswith(docx_id)]
        if len(docx_list) > 0:
            datetime_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            zip_path = datetime_now + ".zip"
            zip_docx(docx_list, zip_path)
            with open(zip_path, 'rb') as f:
                response = HttpResponse(f)
                response['Content-Type'] = 'application/octet-stream'  # 设置头信息，告诉浏览器这是个文件
                response['Content-Disposition'] = 'attachment;filename="%s"' % zip_path
            try:
                return response
            finally:
                os.remove(zip_path)
        else:
            return render(request, "error_docx_missing.html")
    else:
        return render(request, "error_400.html", status=400)


@check_authority
def upload_template(request, error=''):
    if request.method == "POST":
        if request.user.is_superuser:
            source = request.FILES.get("source", "")
            template = request.FILES.get("template", "")
            if source == '' or template == '':
                return redirect(reverse("upload_template", args=["请选择上传文档"]))
            if source.name != template.name:
                return redirect(reverse("upload_template", args=["预览文档与模板文档名称必须一致"]))
            if template in os.listdir(templates_dir):
                return redirect(reverse("upload_template", args=["文档已存在，请先删除同名文档"]))
            else:
                try:
                    source_file = open(os.path.join(source_dir, source.name), 'wb+')
                    template_file = open(os.path.join(templates_dir, template.name), 'wb+')
                    for handler, file in [(source, source_file), (template, template_file)]:
                        if handler.multiple_chunks():
                            for chunk in handler:  # 分块写入文件
                                file.write(chunk)
                        else:
                            file.write(handler.read())
                        file.close()
                    return redirect(reverse("upload_template", args=["上传 %s 成功" % template.name]))
                except:
                    return redirect(reverse("upload_template", args=["上传文件时发生错误"]))
        else:
            return render(request, "error_403.html", status=403)
    else:
        return render(request, "upload_template.html", {"error": error})
