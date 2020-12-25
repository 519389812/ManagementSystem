from django.shortcuts import render, reverse, redirect
from django.conf import settings
from django.core.paginator import Paginator
from performance.models import Level, RuleCondition, Rule, PositionType, Position, SkillType, Skill, RewardType, Reward, ShiftType, Shift, AddWorkload, ReferenceType, Reference, AddReward
from team.models import Team
from user.views import check_authority


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
    return render(request, "addworkload_approval.html",{'addinfos_list':addinfos_list_obj})


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
