from django.http import HttpResponse
from django.shortcuts import render, reverse, redirect
from django.conf import settings
from django.core.paginator import Paginator
from performance.models import Position, RewardRecord, WorkloadRecord, Level, Shift
from team.models import Team
from user.views import check_authority
from ManagementSystem.views import parse_url_param
from django.utils import timezone
import pandas as pd
import numpy as np
import datetime
from django.contrib import messages
from io import BytesIO
from django.utils.datastructures import MultiValueDictKeyError
from django.core.paginator import Paginator


from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("{}/templates/pyecharts".format(settings.BASE_DIR)))

from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Grid
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
def reward_grid(request):
    url = request.META.get("HTTP_REFERER", "")
    if url == "":
        return render(request, "error_400.html", status=400)
    url_params = parse_url_param(url)
    queryset = get_queryset(url_params, 'RewardRecord')
    if queryset.count() == 0:
        messages.error(request, "筛选数据为空")
        return redirect(url)

    # summary_line
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
    reward_summary_line = (
        line
    )

    # summary_bar
    data = pd.DataFrame(queryset.values("", "reward__type"))
    data['name'] = data['user__last_name'] + data['user__first_name']
    data = data[['name', 'reward__name']]
    data = data.rename(columns={"name": '姓名', "reward__name": '奖惩名称'})
    data['次数'] = data['姓名']
    data = pd.pivot_table(data, values=["次数"], index=["奖惩名称"], aggfunc=np.count_nonzero)
    bar = Bar(init_opts=opts.InitOpts()).set_global_opts(title_opts=opts.TitleOpts(title="奖惩统计", subtitle="总体"))
    bar.add_xaxis(data.index.values.tolist())
    bar.add_yaxis("奖惩类型", data["次数"].values.tolist())
    reward_summary_bar = (
        bar
    )

    # summary_bar
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
    reward_summary_by_name_bar = (
        bar
    )

    #
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
    return HttpResponse(reward_summary_bar.render_embed())


def workload_summary_export(request):
    url = request.META.get("HTTP_REFERER", "")
    if url == "":
        return render(request, "error_400.html", status=400)
    url_params = parse_url_param(url)
    queryset = get_queryset(url_params, 'WorkloadRecord')
    if queryset.count() == 0:
        messages.error(request, "筛选数据为空")
        return redirect(url)
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
    response['Content-Disposition'] = 'attachment;filename="{}"'.format("Export pivot by score " + filename + ".xlsx")
    data.to_excel(outfile)
    response.write(outfile.getvalue())
    return response


def performance(request):
    return render(request, "performance.html")


def return_formfield_for_foreignkey(request, db_field, kwargs, db_field_name, obj):
    if not request.user.is_superuser:
        try:
            team_id = request.user.team.id
            if db_field.name == db_field_name:
                kwargs["queryset"] = obj.objects.filter(related_parent__iregex=r'\D%s\D' % str(team_id))
        except:
            pass
    return kwargs


@check_authority
def add_workload(request):
    shift_list = list(Shift.objects.all().values("id", "name"))
    position_list = list(Position.objects.all().values("id", "name"))
    level_list = list(Level.objects.filter(type__name='工作量').values('id', 'name'))
    if not request.user.is_superuser:
        team_id = request.user.team.parent.id
        team_list = list(Team.objects.filter(related_parent__iregex=r'\D%s\D' % str(team_id)))
    else:
        team_list = list(Team.objects.all())
    team_list = [{'id': team.id, 'name': team.get_related_parent_name()} for team in team_list]
    if request.method == "POST":
        shift_id = request.POST.get("shift", "")
        position_id = request.POST.get("position", "")
        level_id = request.POST.get("level", "")
        start_datetime = request.POST.get("start_datetime", "")
        end_datetime = request.POST.get("end_datetime", "")
        assigned_team_id = request.POST.get("assigned_team", "")
        remark = request.POST.get("remark", "")
        if not all([shift_id, position_id, start_datetime, end_datetime, assigned_team_id]):
            return render(request, "error_500.html", status=500)
        # try:
        start_datetime = timezone.datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M")
        end_datetime = timezone.datetime.strptime(end_datetime, "%Y-%m-%dT%H:%M")
        working_time = round((end_datetime - start_datetime).seconds / 60 / 60, 2)
        shift = Shift.objects.get(id=int(shift_id))
        position = Position.objects.get(id=int(position_id))
        level = Level.objects.get(id=int(level_id)) if level_id != "" else None
        assigned_team = Team.objects.get(id=int(assigned_team_id))
        WorkloadRecord.objects.create(user=request.user, shift=shift, position=position, level=level,
                                      start_datetime=start_datetime, end_datetime=end_datetime,
                                      working_time=working_time, assigned_team=assigned_team, remark=remark)
        msg = "登记成功！您可以继续登记下一条记录！"
        return render(request, "add_workload.html",
                      {"shift_list": shift_list, "position_list": position_list, "team_list": team_list,
                       "level_list": level_list, "shift_name": shift.name, "position_name": position.name,
                       "assigned_team_name": assigned_team.name, "msg": msg})
        # except:
        #     return render(request, "error_500.html", status=500)
    else:
        return render(request, "add_workload.html", {"shift_list": shift_list, "position_list": position_list,
                                                     "team_list": team_list, 'level_list': level_list})


@check_authority
def view_workload(request):
    if request.method == "GET":
        page = request.GET.get("page", '1')
        create_datetime = timezone.localtime(timezone.now()) - timezone.timedelta(days=41)
        workload_list = WorkloadRecord.objects.filter(user=request.user, created_datetime__gte=create_datetime)
        paginator = Paginator(workload_list, 20)
        page_workload_list = paginator.get_page(int(page))
        render(request, "view_workload.html", {"page_workload_list": page_workload_list,
                                               "total_workload": paginator.count, "total_page": paginator.num_pages,
                                               "page": page})
    else:
        return render(request, "error_500.html", status=500)
