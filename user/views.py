from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from user.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import login as login_admin
from django.contrib.auth import logout as logout_admin
from django.contrib.auth import authenticate
from django.utils.datastructures import MultiValueDictKeyError
import re
from user_agents import parse
import json
from urllib.parse import urlparse
import uuid
# from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
# from django.utils import timezone
from django.http import Http404


def check_authority(func):
    def wrapper(*args, **kwargs):
        if not args[0].user.is_authenticated:
            args[0].session["path"] = args[0].path
            return redirect(reverse("login"))
        return func(*args, **kwargs)
    return wrapper


def check_is_touch_capable(func):
    def wrapper(*args, **kwargs):
        user_agent = parse(args[0].META.get('HTTP_USER_AGENT'))
        if not user_agent.is_touch_capable:
            if args[0].META.get("HTTP_REFERER"):
                return redirect(args[0].META.get("HTTP_REFERER")+"请使用触屏设备签名")
            else:
                return redirect("/")
        return func(*args, **kwargs)
    return wrapper


# 仅适用于嵌套在第一个参数是requests,第二个参数是object_id的函数上
def check_accessible(model_object):
    def func_wrapper(func):
        def args_wrapper(*args, **kwargs):
            try:
                obj = model_object.objects.get(id=args[1])
            except:
                return redirect('/error_404')
            if args[0].user.is_superuser:
                return func(*args, **kwargs)
            accessible_team_id = list(obj.team.all().values_list("id", flat=True))
            if len(accessible_team_id) == 0:
                return func(*args, **kwargs)
            else:
                for team_id in accessible_team_id:
                    if team_id in json.loads(args[0].user.team.related_parent):
                        return func(*args, **kwargs)
            return redirect('/error_not_accessible')
        return args_wrapper
    return func_wrapper


def home(request):
    return render(request, "home.html")


def register(request, error=''):
    if request.method == "POST":
        if not check_register_valudate(request, check_username_validate, check_password_validate, check_lastname_validate,
                                       check_firstname_validate):
            return redirect(reverse("register", args=["存在未按规定要求的字段!"]))
        username = request.POST.get("username")
        password = request.POST.get("password")
        last_name = request.POST.get("lastname")
        first_name = request.POST.get("firstname")
        try:
            User.objects.create(username=username, password=make_password(password), last_name=last_name,
                                first_name=first_name, is_active=False)
            return redirect(reverse("login", args=["注册成功，请等待管理员审核！"]))
        except:
            return redirect(reverse("register", args=["注册失败，出现未知错误，请联系管理员"]))
    else:
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return render(request, "register.html", {"error": error})


def login(request, error=""):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user:
            if request.META.get('HTTP_X_FORWARDED_FOR'):
                ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR').split(',')[0]
            user_agent = parse(request.META.get('HTTP_USER_AGENT'))
            if user_agent.is_touch_capable is True:
                if User.objects.filter(ip_address=ip).exclude(username=username).count() > 0:
                    return redirect(reverse("login", args=["当前IP(%s)地址与他人IP地址相同，您是否使用了他人设备登录？若是，请使用自己设备登录；如果系统判断失误，请联系管理员！" % ip]))
                user.ip_address = ip
                user.save()
            login_admin(request, user)
            path = request.session.get("path", "")
            if path != "":
                return redirect(path)
            else:
                return redirect('/')
        else:
            try:
                user = User.objects.get(username=username)
                if check_password(password, user.password):
                    if user.is_active:
                        return redirect(reverse("login", args=["登录出错，请管理员!"]))
                    else:
                        return redirect(reverse("login", args=["用户未认证，请联系管理员审核!"]))
                else:
                    return redirect(reverse("login", args=["用户名或密码错误!"]))
            except:
                return redirect(reverse("login", args=["用户名或密码错误!"]))
    else:
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return render(request, "login.html", {"error": error})


def logout(request):
    logout_admin(request)
    return redirect(reverse("home"))


def check_username_validate(request):
    try:
        username = request.GET["username"]
    except MultiValueDictKeyError:
        username = request.POST.get("username")
    if username == "":
        return HttpResponse('用户名不能为空')
    if len(username) < 4 or len(username) > 16:
        return HttpResponse('用户名不能少于4个字符或超过16个字符')
    if not re.search(r'^[_a-zA-Z0-9]+$', username):
        return HttpResponse("用户名包含非法字符(!,@,#,$,%...)")
    if User.objects.filter(username=username).count() != 0:
        return HttpResponse('用户名已存在')
    return HttpResponse('')


def check_password_validate(request):
    try:
        password = request.GET["password"]
    except MultiValueDictKeyError:
        password = request.POST.get("password")
    if password == "":
        return HttpResponse('密码不能为空')
    if len(password) < 6 or len(password) > 16:
        return HttpResponse('密码不能少于6个字符或超过16个字符')
    if not re.search(r'^\S+$', password):
        return HttpResponse("密码包含非法字符(‘ ’)")
    return HttpResponse('')


def check_lastname_validate(request):
    try:
        lastname = request.GET["lastname"]
    except MultiValueDictKeyError:
        lastname = request.POST.get("lastname")
    if lastname == "":
        return HttpResponse('姓氏不能为空')
    if len(lastname) > 50:
        return HttpResponse('姓氏不能超过50个字符')
    if not re.search(r'^[_a-zA-Z0-9\u4e00-\u9fa5]+$', lastname):
        return HttpResponse("姓氏包含非法字符(!,@,#,$,%...)")
    return HttpResponse('')


def check_firstname_validate(request):
    try:
        firstname = request.GET["firstname"]
    except MultiValueDictKeyError:
        firstname = request.POST.get("firstname")
    if firstname == "":
        return HttpResponse('名字不能为空')
    if len(firstname) > 50:
        return HttpResponse('名字不能超过50个字符')
    if not re.search(r'^[_a-zA-Z0-9\u4e00-\u9fa5]+$', firstname):
        return HttpResponse("名字包含非法字符(!,@,#,$,%...)")
    return HttpResponse('')


def check_register_valudate(request, *args):
    check_method = args
    for method in check_method:
        if method(request).content != b'':
            return False
    return True
