from django.contrib import admin
from performance.models import LevelType, Level, Rule, PositionType, Position, RewardType, Reward, Shift, RewardRecord, RewardSummary, WorkloadRecord, WorkloadSummary, OutputType, Output, OutputRecord, OutputSummary
from team.models import Team
from user.models import User
from django.contrib.admin import widgets
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from django.db.models import Count, Sum, DateTimeField, DateField, Min, Max, Avg, F, ExpressionWrapper, fields, Value, Func
from django.db.models.functions import Trunc
from django.apps import apps
from django.utils import timezone
import re
from django.contrib import messages
import math
from ManagementSystem.admin import return_get_queryset_by_team, return_get_queryset_by_parent_team, return_get_queryset_by_related_team, return_get_queryset_by_parent_team_foreignkey


def return_formfield_for_manytomany_parent_team(self, request, db_field, kwargs, db_field_name, obj):
    if not request.user.is_superuser:
        try:
            if db_field.name == db_field_name:
                if request.user.team.parent:
                    team_id = request.user.team.parent.id
                else:
                    team_id = request.user.team.id
                kwargs["queryset"] = obj.objects.filter(related_parent__iregex=r'[^0-9]*%s[^0-9]' % str(team_id))
                kwargs['widget'] = widgets.FilteredSelectMultiple(
                    db_field.verbose_name,
                    db_field.name in self.filter_vertical
                )
        except:
            pass
    return kwargs


def return_formfield_for_foreignkey_parent_rule(request, db_field, kwargs, db_field_name, obj, model_name):
    if db_field.name == db_field_name:
        if request.user.team.parent:
            kwargs["queryset"] = obj.objects.filter(effect=model_name, team__in=[request.user.team.parent])
        else:
            kwargs["queryset"] = obj.objects.filter(effect=model_name, team__in=[request.user.team])
    return kwargs


def return_formfield_for_foreignkey_parent_level(request, db_field, kwargs, db_field_name, obj, model_name):
    if db_field.name == db_field_name:
        if request.user.team.parent:
            kwargs["queryset"] = obj.objects.filter(type__name=model_name, team__in=[request.user.team.parent])
        else:
            kwargs["queryset"] = obj.objects.filter(type__name=model_name, team__in=[request.user.team])
    return kwargs


def return_formfield_for_foreignkey_parent(request, db_field, kwargs, db_field_name, obj):
    if db_field.name == db_field_name:
        if request.user.team.parent:
            kwargs["queryset"] = obj.objects.filter(team__in=[request.user.team.parent])
        else:
            kwargs["queryset"] = obj.objects.filter(team__in=[request.user.team])
    return kwargs


def return_formfield_for_foreignkey_parent_team(request, db_field, kwargs, db_field_name):
    if db_field.name == db_field_name:
        if request.user.team.parent:
            team_id = request.user.team.parent.id
        else:
            team_id = request.user.team.id
        kwargs["queryset"] = Team.objects.filter(related_parent__iregex=r'[^0-9]*%s[^0-9]' % str(team_id)).order_by('name')
    return kwargs


def return_formfield_for_foreignkey_parent_user(request, db_field, kwargs, db_field_name):
    if db_field.name == db_field_name:
        if request.user.team.parent:
            team_id = request.user.team.parent.id
        else:
            team_id = request.user.team.id
        kwargs["queryset"] = User.objects.filter(team__related_parent__iregex=r'[^0-9]*%s[^0-9]' % str(team_id)).order_by('last_name')
    return kwargs


def return_get_model_perms(self, request):
    if request.user.is_superuser:
         model_perms = {
            'add': self.has_add_permission(request),
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request),
            'view': self.has_view_permission(request)
         }
    else:
        model_perms = {}
    return model_perms


def half_ceil(x):
    return math.modf(x)[1] + (0.5 if math.modf(x)[0] < 0.5 else 1)


class RuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'effect', 'date_condition', 'condition', 'score', 'workload', 'bonus', 'man_hours', 'quantity')
    filter_horizontal = ('team',)
    search_fields = ('name',)

    def get_form(self, request, obj=None, **kwargs):
        help_texts = {
            'date_condition': '如需要规定90天内重复某个差错，则时间条件设为：“<=90“，无条件则为空，当规则指向“程度”时，条件无效',
            'condition': '如需要规定数量2次以上，则条件设为：“>=2“，无条件则为空，当规则指向“程度”时，条件无效',
            'score': '如需设置双倍分数奖罚，则设为：“*2“，无权重则为空',
            'workload': '如需设置扣20工作量，则设为：“-20“，无权重则为空',
            'bonus': '如需设置奖金减半，则设为：“/2“，无权重则为空',
            'man_hours': '如需设置工时加成30%，则设为：“*0.3，特别注意：工时仅作用于工作量表“，无权重则为空',
            'quantity': '设置产出的加权，无权重则为空'
        }
        kwargs.update({'help_texts': help_texts})
        return super(RuleAdmin, self).get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset_by_parent_team(request, qs, 'team')
        return qs

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_manytomany_parent_team(self, request, db_field, kwargs, 'team', Team)
        return super(RuleAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            if obj.effect == "level":
                if obj.date_condition:
                    obj.date_condition = None
                    messages.error(request, "注意：当规则作用于程度时，日期条件和数量条件无效！")
                if obj.condition:
                    obj.condition = None
                    messages.error(request, "注意：当规则作用于程度时，日期条件和数量条件无效！")
            elif obj.effect == "skill":
                if obj.date_condition:
                    obj.date_condition = None
                    messages.error(request, "注意：当规则作用于技能时，日期条件无效！")
            super().save_model(request, obj, form, change)


class LevelTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    filter_horizontal = ('team',)
    search_fields = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset_by_parent_team(request, qs, 'team')
        return qs

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_manytomany_parent_team(self, request, db_field, kwargs, 'team', Team)
        return super(LevelTypeAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        help_texts = {
            'name': '如需要设置专用于“新增工作安排”表的程度项，请将名称设置为“工作安排记录”，“产出”同理。',
        }
        kwargs.update({'help_texts': help_texts})
        return super(LevelTypeAdmin, self).get_form(request, obj, **kwargs)

    def get_model_perms(self, request):
        return return_get_model_perms(self, request)


class LevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rule')
    filter_horizontal = ('team',)
    search_fields = ('name',)
    # autocomplete_fields = ['type']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset_by_parent_team(request, qs, 'team')
        return qs

    # 与autocomplete_fields冲突
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey_parent(request, db_field, kwargs, 'type', LevelType)
        kwargs = return_formfield_for_foreignkey_parent_rule(request, db_field, kwargs, 'rule', Rule, 'level')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_manytomany_parent_team(self, request, db_field, kwargs, 'team', Team)
        return super(LevelAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class PositionTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    filter_horizontal = ('team',)
    search_fields = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset_by_parent_team(request, qs, 'team')
        return qs

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_manytomany_parent_team(self, request, db_field, kwargs, 'team', Team)
        return super(PositionTypeAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def get_model_perms(self, request):
        return return_get_model_perms(self, request)


class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'score', 'workload', 'bonus', 'man_hours', 'rule')
    filter_horizontal = ('team',)
    search_fields = ('name',)
    # autocomplete_fields = ['type']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset_by_parent_team(request, qs, 'team')
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey_parent(request, db_field, kwargs, 'type', PositionType)
        kwargs = return_formfield_for_foreignkey_parent_rule(request, db_field, kwargs, 'rule', Rule, 'position')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_manytomany_parent_team(self, request, db_field, kwargs, 'team', Team)
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class RewardTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    filter_horizontal = ('team',)
    search_fields = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset_by_parent_team(request, qs, 'team')
        return qs

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_manytomany_parent_team(self, request, db_field, kwargs, 'team', Team)
        return super(RewardTypeAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def get_model_perms(self, request):
        return return_get_model_perms(self, request)


class RewardAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'score', 'workload', 'bonus', 'rule')
    filter_horizontal = ('team',)
    search_fields = ('name',)
    # autocomplete_fields = ['type']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset_by_parent_team(request, qs, 'team')
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey_parent(request, db_field, kwargs, 'type', RewardType)
        kwargs = return_formfield_for_foreignkey_parent_rule(request, db_field, kwargs, 'rule', Rule, 'reward')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_manytomany_parent_team(self, request, db_field, kwargs, 'team', Team)
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'score', 'workload', 'bonus', 'rule')
    filter_horizontal = ('team',)
    search_fields = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset_by_parent_team(request, qs, 'team')
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey_parent_rule(request, db_field, kwargs, 'rule', Rule, 'shift')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_manytomany_parent_team(self, request, db_field, kwargs, 'team', Team)
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class OutputTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    filter_horizontal = ('team',)
    search_fields = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset_by_parent_team(request, qs, 'team')
        return qs

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_manytomany_parent_team(self, request, db_field, kwargs, 'team', Team)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_model_perms(self, request):
        return return_get_model_perms(self, request)


class OutputAdmin(admin.ModelAdmin):
    list_display = ('name', 'rule')
    filter_horizontal = ('team',)
    search_fields = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset_by_parent_team(request, qs, 'team')
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey_parent(request, db_field, kwargs, 'type', OutputType)
        kwargs = return_formfield_for_foreignkey_parent_rule(request, db_field, kwargs, 'rule', Rule, 'output')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_manytomany_parent_team(self, request, db_field, kwargs, 'team', Team)
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class RewardRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'reward', 'level', 'title', 'score', 'workload', 'bonus')
    fields = ('id', 'user', 'date', 'reward', 'get_reward_rule', 'level', 'get_level_rule', 'title', 'content', 'score', 'workload', 'bonus', 'created_datetime', 'created_user')
    list_display_links = ('user',)
    search_fields = ('user__last_name', 'user__first_name')
    # autocomplete_fields = ['user']
    readonly_fields = ('id', 'get_reward_rule', 'get_level_rule', 'created_datetime', 'created_user', 'score', 'workload', 'bonus')
    list_filter = (
        ('date', DateRangeFilter), 'user__team', 'reward__type', 'reward'
    )

    def get_reward_rule(self, obj):
        return obj.reward.rule if obj.reward.rule else "无"
    get_reward_rule.short_description = "奖惩规则"

    # def get_reference(self, obj):
    #     return ' '.join([i.name for i in obj.reference.all()])
    # get_reference.short_description = "影响"

    def get_level_rule(self, obj):
        return obj.level.rule if obj.level else "无"
    get_level_rule.short_description = "程度规则"

    def get_initial_reward(self, obj):
        return '分数: %s, 工作量: %s, 奖金: %s' % (obj.reward.score, obj.reward.workload, obj.reward.bonus)
    get_initial_reward.short_description = "初始分值"

    def get_weight_column(self, obj, column_name):
        return_column = eval('obj.reward.%s' % column_name)
        if obj.reward.rule:
            if obj.reward.rule.date_condition:
                end_date = obj.date
                date_delta = int(re.findall(r'\d+', obj.reward.rule.date_condition)[0])
                start_date = end_date - timezone.timedelta(date_delta)
                count = RewardRecord.objects.filter(user=obj.user, date__gte=start_date, date__lte=end_date).count()
            else:
                count = RewardRecord.objects.filter(user=obj.user).count()
            if obj.reward.rule.condition:
                match = eval('count %s' % obj.reward.rule.condition)
                if match:
                    string = 'obj.reward.rule.%s' % column_name
                    return_column = eval('%s %s' % (return_column, eval(string))) if eval(string) else return_column
            else:
                if count > 0:
                    string = 'obj.reward.rule.%s' % column_name
                    return_column = eval('%s %s' % (return_column, eval(string))) if eval(string) else return_column
        if obj.level:
            if eval('obj.level.rule.%s' % column_name):
                string = 'obj.level.rule.%s' % column_name
                return_column = eval('%s %s' % (return_column, eval(string))) if eval(string) else return_column
        return return_column

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset_by_parent_team_foreignkey(request, qs, 'user__team')
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey_parent_level(request, db_field, kwargs, 'level', Level, 'rewarkrecord')
        kwargs = return_formfield_for_foreignkey_parent_user(request, db_field, kwargs, 'user')
        kwargs = return_formfield_for_foreignkey_parent(request, db_field, kwargs, 'reward', Reward)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            obj.score = round(self.get_weight_column(obj, 'score'), 2)
            obj.workload = round(self.get_weight_column(obj, 'workload'), 2)
            obj.bonus = round(self.get_weight_column(obj, 'bonus'), 2)
            obj.created_user = request.user
            super().save_model(request, obj, form, change)


class RewardSummaryAdmin(admin.ModelAdmin):
    change_list_template = "admin/reward_summary_change_list.html"

    list_filter = (
        ('date', DateTimeRangeFilter), 'user__team', 'reward__type', 'reward'
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset_by_parent_team(request, qs, 'user__team')
        return qs

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        metrics = {
            'count': Count('user'),
            'score': Sum('score'),
            'workload': Sum('workload'),
            'bonus': Sum('bonus'),
        }
        response.context_data['summary'] = list(
            qs.values("user__last_name", "user__first_name").annotate(**metrics).order_by('-workload')
        )
        return response


class WorkloadRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'position', 'level', 'start_datetime', 'end_datetime', 'assigned_team', 'working_time', 'get_initial_workload', 'score', 'workload', 'bonus', 'man_hours', 'remark', 'created_datetime', 'verified')
    list_editable = ('verified',)
    # autocomplete_fields = ['user', 'position', 'assigned_team']
    search_fields = ('user__last_name', 'user__first_name')
    fields = ('id', 'user', 'position', 'get_position_rule', 'level', 'get_level_rule', 'start_datetime', 'end_datetime', 'assigned_team', 'remark', 'working_time', 'get_initial_workload', 'score', 'workload', 'bonus', 'man_hours', 'verified', 'created_datetime', 'verified_user', 'verified_datetime')
    readonly_fields = ('id', 'user', 'created_datetime', 'working_time', 'get_position_rule', 'get_initial_workload', 'get_level_rule', 'score', 'workload', 'bonus', 'man_hours', 'verified_user', 'verified_datetime')
    list_filter = (
        ('start_datetime', DateTimeRangeFilter), 'assigned_team', 'position__type', 'position', 'verified'
    )

    def get_form(self, request, obj=None, **kwargs):
        help_texts = {
            'working_time': '注意：工作时长超过24小时判定为无效!',
        }
        kwargs.update({'help_texts': help_texts})
        return super(WorkloadRecordAdmin, self).get_form(request, obj, **kwargs)

    def get_initial_workload(self, obj):
        return '分数: %s, 工作量: %s, 奖金: %s, 计算工时: %s' % (
            obj.position.score, obj.position.workload, obj.position.bonus, "是" if obj.position.man_hours else "否")
    get_initial_workload.short_description = "基础分值"

    def get_position_rule(self, obj):
        return obj.position.rule if obj.position.rule else "无"
    get_position_rule.short_description = "岗位规则"

    def get_level_rule(self, obj):
        return obj.level.rule if obj.level else "无"
    get_level_rule.short_description = "程度规则"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset_by_parent_team_foreignkey(request, qs, 'user__team')
        return qs

    def get_weight_column(self, obj, model_name, column_name, working_time):
        is_count_time = False
        return_column = eval('obj.%s.%s' % (model_name, column_name))
        if eval('obj.%s.rule' % model_name):
            if eval('obj.%s.rule.date_condition' % model_name) or eval('obj.%s.rule.condition' % model_name):
                if eval('obj.%s.rule.date_condition' % model_name):
                    end_date = timezone.localtime(obj.start_datetime)
                    date_delta = int(re.findall(r'\d+', eval('obj.%s.rule.date_condition' % model_name))[0])
                    start_date = end_date - timezone.timedelta(date_delta)
                    count = WorkloadRecord.objects.filter(user=obj.user, start_datetime__gte=start_date, end_datetime__lte=end_date).count()
                else:
                    count = WorkloadRecord.objects.filter(user=obj.user).count()
                if eval('obj.%s.rule.condition' % model_name):
                    match = eval('count obj.%s.rule.condition' % model_name)
                    if match:
                        string = 'obj.%s.rule.%s' % (model_name, column_name)
                        return_column = eval('%s * %s %s' % (return_column, working_time, eval(string))) if eval(string) else return_column
                        is_count_time = True
                else:
                    if count > 0:
                        string = 'obj.%s.rule.%s' % (model_name, column_name)
                        return_column = eval('%s * %s %s' % (return_column, working_time, eval(string))) if eval(string) else return_column
                        is_count_time = True
            else:
                if eval('obj.%s.rule.%s' % (model_name, column_name)):
                    string = 'obj.%s.rule.%s' % (model_name, column_name)
                    return_column = eval('%s * %s %s' % (return_column, working_time, eval(string))) if eval(string) else return_column
                    is_count_time = True
        if not is_count_time:
            return_column = eval('%s * %s' % (return_column, working_time))
        if obj.level:
            if eval('obj.level.rule.%s' % column_name):
                string = 'obj.level.rule.%s' % column_name
                return_column = eval('%s %s' % (return_column, eval(string))) if eval(string) else return_column
        return return_column

    def get_weight_man_hours(self, obj, working_time):
        if obj.position.rule:
            if obj.position.rule.man_hours:
                working_time = eval('%s %s' % (working_time, obj.position.rule.man_hours))
        if obj.level:
            if obj.level.rule.man_hours:
                working_time = eval('%s %s' % (working_time, obj.level.rule.man_hours))
        return working_time

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey_parent_level(request, db_field, kwargs, 'level', Level, 'workloadrecord')
        kwargs = return_formfield_for_foreignkey_parent_user(request, db_field, kwargs, 'user')
        kwargs = return_formfield_for_foreignkey_parent(request, db_field, kwargs, 'position', Position)
        kwargs = return_formfield_for_foreignkey_parent_team(request, db_field, kwargs, 'assigned_team')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            if obj.working_time > 24:
                messages.error(request, "保存失败！工作时长超过最大限制24小时！")
                messages.set_level(request, messages.ERROR)
                return
            if not change:
                super().save_model(request, obj, form, change)
            obj.score = round(self.get_weight_column(obj, 'position', 'score', obj.working_time), 2)
            obj.workload = round(self.get_weight_column(obj, 'position', 'workload', obj.working_time), 2)
            obj.bonus = round(self.get_weight_column(obj, 'position', 'bonus', obj.working_time), 2)
            if obj.position.man_hours:
                obj.man_hours = round(self.get_weight_man_hours(obj, obj.working_time), 2)
            else:
                obj.man_hours = 0
            verified_before = WorkloadRecord.objects.get(id=obj.id).verified
            verified_after = form.cleaned_data["verified"]
            if verified_before != verified_after and verified_after is True:
                obj.verified_user = request.user
                obj.verified_datetime = timezone.localtime(timezone.now())
            super().save_model(request, obj, form, change)


class WorkloadSummaryAdmin(admin.ModelAdmin):
    change_list_template = "admin/workload_summary_change_list.html"

    list_filter = (
        ('start_datetime', DateTimeRangeFilter), 'user__team', 'position__type', 'position'
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset_by_parent_team_foreignkey(request, qs, 'user__team')
        return qs

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        metrics = {
            'count': Count('user'),
            'total_score': Sum('score'),
            'total_workload': Sum('workload'),
            'total_bonus': Sum('bonus'),
            'total_man_hours': Sum('man_hours'),
        }
        response.context_data['summary'] = list(
            qs.filter(verified=True).values("user__last_name", "user__first_name").annotate(**metrics).order_by('-total_workload')
        )
        return response


class OutputRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'output', 'get_output_rule', 'level', 'get_level_rule', 'quantity', 'weight_quantity', 'assigned_team', 'remark', 'verified')
    fields = ('id', 'user', 'date', 'output', 'get_output_rule', 'level', 'get_level_rule', 'quantity', 'weight_quantity', 'assigned_team', 'remark', 'created_datetime', 'verified', 'verified_user', 'verified_datetime')
    list_editable = ('verified',)
    list_display_links = ('user',)
    search_fields = ('user__last_name', 'user__first_name')
    readonly_fields = ('id', 'user', 'get_output_rule', 'get_level_rule', 'weight_quantity', 'created_datetime', 'verified_user', 'verified_datetime')
    list_filter = (
        ('date', DateRangeFilter), 'assigned_team', 'output__type', 'output', 'verified'
    )

    def get_output_rule(self, obj):
        return obj.output.rule if obj.output.rule else "无"
    get_output_rule.short_description = "产出规则"

    # 必须加入到readonly_fields内，否则会报错
    def get_level_rule(self, obj):
        return obj.level.rule if obj.level else "无"
    get_level_rule.short_description = "程度规则"

    def get_weight_column(self, obj, column_name):
        return_column = eval('obj.%s' % column_name)
        if obj.output.rule:
            if obj.output.rule.date_condition:
                end_date = obj.date
                date_delta = int(re.findall(r'\d+', obj.output.rule.date_condition)[0])
                start_date = end_date - timezone.timedelta(date_delta)
                count = OutputRecord.objects.filter(user=obj.user, date__gte=start_date, date__lte=end_date).count()
            else:
                count = OutputRecord.objects.filter(user=obj.user).count()
            if obj.output.rule.condition:
                match = eval('count %s' % obj.output.rule.condition)
                if match:
                    string = 'obj.output.rule.%s' % column_name
                    return_column = eval('%s %s' % (return_column, eval(string))) if eval(string) else return_column
            else:
                if count > 0:
                    string = 'obj.output.rule.%s' % column_name
                    return_column = eval('%s %s' % (return_column, eval(string))) if eval(string) else return_column
        if obj.level:
            string = 'obj.level.rule.%s' % column_name
            return_column = eval('%s %s' % (return_column, eval(string))) if eval(string) else return_column
        return return_column

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset_by_parent_team_foreignkey(request, qs, 'user__team')
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey_parent_level(request, db_field, kwargs, 'level', Level, 'outputrecord')
        kwargs = return_formfield_for_foreignkey_parent_user(request, db_field, kwargs, 'user')
        kwargs = return_formfield_for_foreignkey_parent(request, db_field, kwargs, 'output', Output)
        kwargs = return_formfield_for_foreignkey_parent_team(request, db_field, kwargs, 'assigned_team')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            obj.weight_quantity = round(self.get_weight_column(obj, 'quantity'), 2)
            obj.user = request.user
            super().save_model(request, obj, form, change)


class OutputSummaryAdmin(admin.ModelAdmin):
    change_list_template = "admin/output_summary_change_list.html"

    list_filter = (
        ('date', DateTimeRangeFilter), 'user__team', 'output__type', 'output'
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset_by_parent_team_foreignkey(request, qs, 'user__team')
        return qs

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        metrics = {
            'count': Count('user'),
            'weight_quantity': Sum('weight_quantity'),
        }
        response.context_data['summary'] = list(
            qs.filter(verified=True).values("user__last_name", "user__first_name").annotate(**metrics).order_by('-weight_quantity')
        )
        return response


admin.site.register(Rule, RuleAdmin)
admin.site.register(LevelType, LevelTypeAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(PositionType, PositionTypeAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(RewardType, RewardTypeAdmin)
admin.site.register(Reward, RewardAdmin)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(OutputType, OutputTypeAdmin)
admin.site.register(Output, OutputAdmin)
admin.site.register(RewardRecord, RewardRecordAdmin)
admin.site.register(RewardSummary, RewardSummaryAdmin)
admin.site.register(WorkloadRecord, WorkloadRecordAdmin)
admin.site.register(WorkloadSummary, WorkloadSummaryAdmin)
admin.site.register(OutputRecord, OutputRecordAdmin)
admin.site.register(OutputSummary, OutputSummaryAdmin)
