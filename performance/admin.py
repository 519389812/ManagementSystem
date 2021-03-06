from django.contrib import admin
from performance.models import Level, Rule, PositionType, Position, SkillType, Skill, RewardType, Reward, Shift, RewardRecord, RewardSummary, WorkloadRecord, WorkloadSummary
from team.models import Team
from django.contrib.admin import widgets
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from django.db.models import Count, Sum, DateTimeField, DateField, Min, Max, Avg, F, ExpressionWrapper, fields, Value, Func
from django.db.models.functions import Trunc
from django.apps import apps
from django.utils import timezone
import re
from django.contrib import messages
import datetime


def return_get_queryset(request, qs):
    if not request.user.is_superuser:
        try:
            team_id = request.user.team.id
            qs = qs.filter(team__related_parent__iregex=r'\D%s\D' % str(team_id))
        except:
            pass
    return qs


def return_formfield_for_foreignkey(request, db_field, kwargs, db_field_name, obj):
    if not request.user.is_superuser:
        try:
            team_id = request.user.team.id
            if db_field.name == db_field_name:
                kwargs["queryset"] = obj.objects.filter(related_parent__iregex=r'\D%s\D' % str(team_id))
        except:
            pass
    return kwargs


def return_formfield_for_foreignkey_rule(request, db_field, kwargs, db_field_name, obj, model_name):
    if db_field.name == db_field_name:
        kwargs["queryset"] = obj.objects.filter(effect=model_name)
    return kwargs


def return_get_model_perms(self, request):
    if request.user.is_superuser:
         model_perms = {
            'add': self.has_add_permission(request),
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request),
            'view': self.has_view_permission(request)}
    else:
        model_perms = {}
    return model_perms


class RuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'effect', 'date_condition', 'condition', 'score', 'workload', 'bonus')

    def get_form(self, request, obj=None, **kwargs):
        help_texts = {
            'date_condition': '如需要规定90天内重复某个差错，则时间条件设为：“<=90“',
            'condition': '如需要规定数量2次以上，则条件设为：“>=2“',
            'score': '如需设置双倍分数奖罚，则设为：“*2“',
            'workload': '如需设置扣20工作量，则设为：“-20“',
            'bonus': '如需设置奖金减半，则设为：“/2“',
        }
        kwargs.update({'help_texts': help_texts})
        return super(RuleAdmin, self).get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey(request, db_field, kwargs, 'team', Team)
        return super(RuleAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

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


    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     """
    #     Get a form Field for a ManyToManyField.
    #     """
    #     # db_field.name 本模型下的字段名称
    #     if db_field.name == "condition":
    #         # 过滤
    #         kwargs["queryset"] = RuleCondition.objects.filter(team__in=request.user.team.all())
    #         # filter_horizontal 保持横向展示
    #         kwargs['widget'] = widgets.FilteredSelectMultiple(
    #             db_field.verbose_name,
    #             db_field.name in self.filter_vertical
    #         )
    #     if db_field.name == "team":
    #         # 过滤
    #         kwargs["queryset"] = request.user.team.all()
    #         # filter_horizontal 保持横向展示
    #         kwargs['widget'] = widgets.FilteredSelectMultiple(
    #             db_field.verbose_name,
    #             db_field.name in self.filter_vertical
    #         )
    #     return super(RuleAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class LevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rule')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey(request, db_field, kwargs, 'team', Team)
        kwargs = return_formfield_for_foreignkey_rule(request, db_field, kwargs, 'rule', Rule, 'level')
        return super(LevelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class PositionTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey(request, db_field, kwargs, 'team', Team)
        return super(PositionTypeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_model_perms(self, request):
        return return_get_model_perms(self, request)


class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'score', 'workload', 'bonus')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey(request, db_field, kwargs, 'team', Team)
        return super(PositionAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class SkillTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey(request, db_field, kwargs, 'team', Team)
        return super(SkillTypeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_model_perms(self, request):
        return return_get_model_perms(self, request)


class SkillAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'score', 'workload', 'bonus', 'rule')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey(request, db_field, kwargs, 'team', Team)
        kwargs = return_formfield_for_foreignkey_rule(request, db_field, kwargs, 'rule', Rule, 'skill')
        return super(SkillAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class RewardTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey(request, db_field, kwargs, 'team', Team)
        return super(RewardTypeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_model_perms(self, request):
        return return_get_model_perms(self, request)


class RewardAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'score', 'workload', 'bonus', 'rule')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey(request, db_field, kwargs, 'team', Team)
        kwargs = return_formfield_for_foreignkey_rule(request, db_field, kwargs, 'rule', Rule, 'reward')
        return super(RewardAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'score', 'workload', 'bonus')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey(request, db_field, kwargs, 'team', Team)
        return super(ShiftAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


# class ReferenceTypeAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name')
#
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         qs = return_get_queryset(request, qs)
#         return qs
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         kwargs = return_formfield_for_foreignkey(request, db_field, kwargs, 'team', Team)
#         return super(ReferenceTypeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
#
#     def get_model_perms(self, request):
#         return return_get_model_perms(self, request)
#
#
# class ReferenceAdmin(admin.ModelAdmin):
#     list_display = ('type', 'name')
#
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         qs = return_get_queryset(request, qs)
#         return qs
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         kwargs = return_formfield_for_foreignkey(request, db_field, kwargs, 'team', Team)
#         return super(ReferenceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class RewardRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'reward', 'level', 'title', 'score', 'workload', 'bonus')
    fields = ('user', 'date', 'reward', 'get_reward_rule', 'level', 'get_level_rule', 'title', 'content', 'score', 'workload', 'bonus', 'created_datetime', 'created_user')
    list_display_links = ('user',)
    # filter_horizontal = ('reference',)
    readonly_fields = ('get_reward_rule', 'get_level_rule', 'created_datetime', 'created_user', 'score', 'workload', 'bonus')
    list_filter = (
        ('date', DateRangeFilter), 'user__team'
    )

    def get_reward_rule(self, obj):
        return obj.reward.rule if obj.reward.rule else "无"
    get_reward_rule.short_description = "奖惩规则"

    # def get_reference(self, obj):
    #     return ' '.join([i.name for i in obj.reference.all()])
    # get_reference.short_description = "影响"

    def get_level_rule(self, obj):
        return obj.level.rule if obj.level.rule else "无"
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
        if obj.level.rule:
            string = 'obj.level.rule.%s' % column_name
            return_column = eval('%s %s' % (return_column, eval(string))) if eval(string) else return_column
        return return_column

    def get_weight_score(self, obj):
        return self.get_weight_column(obj, 'score')
    get_weight_score.short_description = "分数"

    def get_weight_workload(self, obj):
        return self.get_weight_column(obj, 'workload')
    get_weight_score.short_description = "工作量"

    def get_weight_bonus(self, obj):
        return self.get_weight_column(obj, 'bonus')
    get_weight_score.short_description = "奖金"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     if not request.user.is_superuser:
    #         try:
    #             team_id = request.user.team.id
    #             if db_field.name == 'reference':
    #                 kwargs["queryset"] = Reference.objects.filter(team__related_parent__iregex=r'\D%s\D' % str(team_id))
    #         except:
    #             pass
    #     return super(RewardRecordAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            obj.score = self.get_weight_column(obj, 'score')
            obj.workload = self.get_weight_column(obj, 'workload')
            obj.bonus = self.get_weight_column(obj, 'bonus')
            obj.created_user = request.user
            super().save_model(request, obj, form, change)


class RewardSummaryAdmin(admin.ModelAdmin):
    change_list_template = "admin/reward_summary_change_list.html"

    list_filter = (
        ('date', DateTimeRangeFilter), 'user__team__name'
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
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
    list_display = ('user', 'shift', 'position', 'start_datetime', 'end_datetime', 'assigned_team', 'working_time', 'get_initial_score', 'get_initial_workload', 'get_initial_bonus', 'verified')
    list_editable = ('verified',)
    fields = ('user', 'shift', 'position', 'start_datetime', 'end_datetime', 'assigned_team', 'remark', 'working_time', 'get_initial_score', 'get_initial_workload', 'get_initial_bonus', 'verified', 'created_datetime', 'verified_user', 'verified_datetime')
    readonly_fields = ('created_datetime', 'working_time', 'get_initial_score', 'get_initial_workload', 'get_initial_bonus', 'verified_user', 'verified_datetime')
    list_filter = (
        ('start_datetime', DateTimeRangeFilter), 'user__team__name',
    )

    def get_form(self, request, obj=None, **kwargs):
        help_texts = {
            'working_time': '注意：工作时长超过24小时判定为无效!',
        }
        kwargs.update({'help_texts': help_texts})
        return super(WorkloadRecordAdmin, self).get_form(request, obj, **kwargs)

    def get_initial_score(self, obj):
        return (obj.shift.score + obj.position.score) * obj.working_time
    get_initial_score.short_description = "分值"

    def get_initial_workload(self, obj):
        return (obj.shift.workload + obj.position.workload) * obj.working_time
    get_initial_workload.short_description = "工作量"

    def get_initial_bonus(self, obj):
        return obj.shift.bonus + obj.position.bonus
    get_initial_bonus.short_description = "奖金"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            working_time = round((timezone.localtime(obj.end_datetime) - timezone.localtime(obj.start_datetime)).total_seconds() / 3600, 2)
            if working_time > 24:
                messages.error(request, "保存失败！工作时长超过最大限制24小时！")
                messages.set_level(request, messages.ERROR)
                return
            if not change:
                super().save_model(request, obj, form, change)
            obj.working_time = working_time
            verified_before = WorkloadRecord.objects.get(id=obj.id).verified
            verified_after = form.cleaned_data["verified"]
            if verified_before != verified_after and verified_after is True:
                obj.verified_user = request.user
                obj.verified_datetime = timezone.localtime(timezone.now())
            super().save_model(request, obj, form, change)


class WorkloadSummaryAdmin(admin.ModelAdmin):
    change_list_template = "admin/workload_summary_change_list.html"

    list_filter = (
        ('start_datetime', DateTimeRangeFilter),
        'position', 'user__team__name',
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        metrics = {
            'count': Count('user'),
            'shift_score': Sum(F('shift__score') * F('working_time')),
            'shift_workload': Sum(F('shift__workload') * F('working_time')),
            'shift_bonus': Sum('shift__bonus'),
            'position_score': Sum(F('position__score') * F('working_time')),
            'position_workload': Sum(F('position__workload') * F('working_time')),
            'position_bonus': Sum('position__bonus'),
            'total_score': Sum(F('shift__score') * F('working_time')) + Sum(F('position__score') * F('working_time')),
            'total_workload': Sum(F('shift__workload') * F('working_time')) + Sum(F('position__workload') * F('working_time')),
            'total_bonus': Sum('shift__bonus') + Sum('position__bonus'),
        }
        response.context_data['summary'] = list(
            qs.filter(verified=True).values("user__last_name", "user__first_name").annotate(**metrics).order_by('-total_workload')
        )
        return response


admin.site.register(Rule, RuleAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(PositionType, PositionTypeAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(SkillType, SkillTypeAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(RewardType, RewardTypeAdmin)
admin.site.register(Reward, RewardAdmin)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(RewardRecord, RewardRecordAdmin)
admin.site.register(RewardSummary, RewardSummaryAdmin)
admin.site.register(WorkloadRecord, WorkloadRecordAdmin)
admin.site.register(WorkloadSummary, WorkloadSummaryAdmin)
