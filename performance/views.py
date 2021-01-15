from django.http import HttpResponse
from django.shortcuts import render, reverse, redirect
from django.conf import settings
from django.core.paginator import Paginator
from performance.models import Position, RewardRecord, WorkloadRecord
from team.models import Team
from user.views import check_authority
from ManagementSystem.views import parse_url_param
from django.utils import timezone
import pandas as pd
import numpy as np
import datetime
from django.contrib import messages
from io import BytesIO

from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("{}/templates/pyecharts".format(settings.BASE_DIR)))

from pyecharts import options as opts
from pyecharts.charts import Bar, Line
from pyecharts.globals import ThemeType


def make_date_list(start_date, end_date):
    date_list = []
    day_delta = (end_date - start_date).days + 1
    for days in range(day_delta):
        the_date = (start_date + datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        date_list.append(the_date)
    return date_list


def get_queryset(url_params, object_):
    if len(url_params) > 0:
        filter_str = ''
        for key, value in url_params.items():
            if "date" in key:
                print(key)
                filter_str += key.replace("__range", "") + '="' + value[0].replace("/", "-") + '", '
            elif "id" in key:
                filter_str += key + '=' + value[0] + ', '
            else:
                filter_str += key + '="' + value[0] + '", '
        command_str = '%s.objects.filter(%s)' % (object_, filter_str)
        queryset = eval(command_str)
    else:
        queryset = eval('%s.objects.all()' % object_)
    return queryset


@check_authority
def reward_bar_summary(request):
    url = request.META.get("HTTP_REFERER", "")
    if url == "":
        return render(request, "error_400.html", status=400)
    url_params = parse_url_param(url)
    queryset = get_queryset(url_params, 'RewardRecord')
    if queryset.count() == 0:
        messages.error(request, "筛选数据为空")
        return redirect(url)
    data = pd.DataFrame(queryset.values("user__last_name", "user__first_name", "reward__name"))
    data['name'] = data['user__last_name'] + data['user__first_name']
    data = data[['name', 'reward__name']]
    data = data.rename(columns={"name": '姓名', "reward__name": '奖惩名称'})
    data['次数'] = data['姓名']
    data = pd.pivot_table(data, values=["次数"], index=["奖惩名称"], aggfunc=np.count_nonzero)
    bar = Bar(init_opts=opts.InitOpts()).set_global_opts(title_opts=opts.TitleOpts(title="奖惩统计", subtitle="总体"))
    bar.add_xaxis(data.index.values.tolist())
    bar.add_yaxis("奖惩类型", data["次数"].values.tolist())
    c = (
        bar
         )
    return HttpResponse(c.render_embed())


@check_authority
def reward_bar_by_(request):
    url = request.META.get("HTTP_REFERER", "")
    if url == "":
        return render(request, "error_400.html", status=400)
    url_params = parse_url_param(url)
    queryset = get_queryset(url_params, 'RewardRecord')
    if queryset.count() == 0:
        messages.error(request, "筛选数据为空")
        return redirect(url)
    data = pd.DataFrame(queryset.values("user__last_name", "user__first_name", "reward__name"))
    data['name'] = data['user__last_name'] + data['user__first_name']
    data = data[['name', 'reward__name']]
    data = data.rename(columns={"name": '姓名', "reward__name": '奖惩名称'})
    data['次数'] = data['姓名']
    data = pd.pivot_table(data, values=["次数"], index=["姓名", "奖惩名称"], aggfunc=np.count_nonzero)
    first_list, second_list = zip(*data.index.values)
    first_list, second_list = set(first_list), set(second_list)
    bar = Bar(init_opts=opts.InitOpts()).set_global_opts(title_opts=opts.TitleOpts(title="奖惩统计", subtitle="按姓名"))
    bar.add_xaxis(second_list)
    for value in first_list:
        bar.add_yaxis(value, data.loc[value]["次数"].values.tolist())
    b = (
        bar
         )
    return HttpResponse(b.render_embed())


@check_authority
def reward_bar_by_name(request):
    url = request.META.get("HTTP_REFERER", "")
    if url == "":
        return render(request, "error_400.html", status=400)
    url_params = parse_url_param(url)
    queryset = get_queryset(url_params, 'RewardRecord')
    if queryset.count() == 0:
        messages.error(request, "筛选数据为空")
        return redirect(url)
    data = pd.DataFrame(queryset.values("user__last_name", "user__first_name", "reward__name"))
    data['name'] = data['user__last_name'] + data['user__first_name']
    data = data[['name', 'reward__name']]
    data = data.rename(columns={"name": '姓名', "reward__name": '奖惩名称'})
    data['次数'] = data['姓名']
    data = pd.pivot_table(data, values=["次数"], index=["姓名", "奖惩名称"], aggfunc=np.count_nonzero)
    first_list, second_list = zip(*data.index.values)
    first_list, second_list = set(first_list), set(second_list)
    bar = Bar(init_opts=opts.InitOpts()).set_global_opts(title_opts=opts.TitleOpts(title="奖惩统计", subtitle="按姓名"))
    bar.add_xaxis(second_list)
    for value in first_list:
        bar.add_yaxis(value, data.loc[value]["次数"].values.tolist())
    b = (
        bar
         )
    return HttpResponse(b.render_embed())


@check_authority
def reward_line(request):
    url = request.META.get("HTTP_REFERER", "")
    if url == "":
        return render(request, "error_400.html", status=400)
    url_params = parse_url_param(url)
    queryset = get_queryset(url_params, 'RewardRecord')
    if queryset.count() == 0:
        messages.error(request, "筛选数据为空")
        return redirect(url)
    date_range = list(queryset.values_list("date", flat=True).order_by('date'))
    start_date, end_date = date_range[0], date_range[-1]
    date_list = make_date_list(start_date, end_date)
    data = pd.DataFrame(date_list, columns=["日期"])
    data_db = pd.DataFrame(queryset.values("user__last_name", "user__first_name", "reward__name", "date"))
    data_db['name'] = data_db['user__last_name'] + data_db['user__first_name']
    data_db = data_db[['name', 'reward__name', 'date']]
    data_db = data_db.rename(columns={"name": '姓名', "reward__name": '奖惩名称', "date": "日期"})
    data_db["日期"] = data_db["日期"].apply(lambda x: x.strftime('%Y-%m-%d'))
    data = pd.merge(data, data_db, on="日期", how="outer")
    data["次数"] = data["奖惩名称"]
    data = pd.pivot_table(data, values=["次数"], index=["日期"], columns=["奖惩名称"], aggfunc=np.count_nonzero)
    data = data.fillna(0)
    _, second_list = zip(*data.columns.tolist())
    second_list = set(second_list)
    line = Line(init_opts=opts.InitOpts()).set_global_opts(title_opts=opts.TitleOpts(title="奖惩趋势", subtitle="总体"))
    line.add_xaxis(data.index.values.tolist())
    for value in second_list:
        line.add_yaxis(value, data["次数"][value], symbol_size=10, is_smooth=True)
    l = (
        line
    )
    return HttpResponse(l.render_embed())


def workload_summary_export(request):
    url = request.META.get("HTTP_REFERER", "")
    if url == "":
        return render(request, "error_400.html", status=400)
    url_params = parse_url_param(url)
    queryset = get_queryset(url_params, 'WorkloadRecord')
    if queryset.count() == 0:
        messages.error(request, "筛选数据为空")
        return redirect(url)
    print(queryset)
    return
    outfile = BytesIO()
    data = pd.DataFrame(queryset.values("user__last_name", "user__first_name", "reward__name"))
    data = data.rename(columns={'id': '序号', 'employee_name_id': '员工姓名', 'position_name_id': '岗位',
                                'position_score': '岗位基础分', 'shifts': '早晚班', 'score': '评分',
                                'penalty_details': '奖惩', 'total_score': '总分', 'date': '日期', "remark": "备注"})
    data = data[["序号", "员工姓名", "岗位", "岗位基础分", "早晚班", "评分", "奖惩", "总分", "日期", "备注"]]
    data = data.sort_values(by=["员工姓名"], ascending=True)
    data = data.fillna("")
    data = pd.pivot_table(data, values=["总分"], index=["员工姓名"], aggfunc=np.sum)
    filename = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename="{}"'.format(
        "Export pivot by score " + filename + ".xlsx")
    data.to_excel(outfile)
    response.write(outfile.getvalue())
    return response


@check_authority
def get_addinfo_list_data(request, addinfos_all_list):
    paginator = Paginator(addinfos_all_list, settings.EACH_PAGE_ADDINFOS_NUMBER)
    page_num = request.GET.get('page', 1)  # 获取url的页面参数（GET请求）
    page_of_addinfos = paginator.get_page(page_num)
    currentr_page_num = page_of_addinfos.number  # 获取当前页码
    # 获取当前页码前后各2页的页码范围
    page_range = list(range(max(currentr_page_num - 2, 1), currentr_page_num)) + \
                 list(range(currentr_page_num, min(currentr_page_num + 2, paginator.num_pages) + 1))
    # 加上省略页码标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)
    # 获取日期归档对应的登记数量
    addinfo_dates = addinfo.objects.dates('created_time', 'month', order="DESC")
    addinfo_dates_dict = {}
    for addinfo_date in addinfo_dates:
        addinfo_count = addinfo.objects.filter(created_time__year=addinfo_date.year,
                                               created_time__month=addinfo_date.month).count()
        addinfo_dates_dict[addinfo_date] = addinfo_count

    context = {}
    context['addinfos'] = page_of_addinfos.object_list
    context['page_of_addinfos'] = page_of_addinfos
    context['page_range'] = page_range
    context['addinfo_dates'] = addinfo_dates_dict
    return context


def performance(request):
    return render(request, "performance.html")


@check_authority
def add_workload(request):
    if request.method == "POST":
        position = request.POST.get("position", "")
        position = Position.objects.get(name=position)
        worktime = request.POST['worktime']
        department = request.POST.get('department', "")
        department = Team.objects.get(name=department)
        created_time = request.POST['created_time']
        remark = request.POST['remark']
        AddWorkload.objects.create(user=request.user, position=position, worktime=worktime, department=department, created_time=created_time, remark=remark)
        return redirect(reverse('add_workload'))
    else:
        position_list = list(Position.objects.all().values("id", "name"))
        team_list = list(Team.objects.all().values("id", "name", "parent__name"))
        return render(request, "add_workload.html", {"position_list": position_list, "team_list": team_list})


@check_authority
def add_succeed(request):
    return render(request, "add_succeed.html")


@check_authority
def approval(request):
    addinfos_list_obj = list(AddWorkload.objects.all())
    return render(request, "addworkload_approval.html", {'addinfos_list':addinfos_list_obj})


@check_authority
def addinfo(request):
    addinfos_list_obj = list(AddWorkload.objects.all())
    return render(request, 'addworkload_info.html', {'addinfo_list': addinfos_list_obj})


@check_authority
def addinfos_date(request, year, month):
    addinfos_all_list = addinfo.objects.filter(created_time__year=year, created_time__month=month)
    context = get_addinfo_list_data(request, addinfos_all_list)
    context['addinfos_date'] = '%s年%s月' % (year, month)
    return render(request, 'addinfos_date.html', context)


