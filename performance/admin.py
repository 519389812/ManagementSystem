from django.contrib import admin
from performance.models import Level, Rule, PositionType, Position, SkillType, Skill, RewardType, Reward, ShiftType, Shift, WorkloadRecord, ReferenceType, Reference, RewardRecord
from team.models import Team
from django.contrib.admin import widgets
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from django.db.models import Count, Sum, DateTimeField, DateField, Min, Max
from django.db.models.functions import Trunc


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
    list_display = ('name', 'condition')

    def get_condition_reference(self, obj):
        return ' '.join([i.reference for i in obj.rule.all()])
    get_condition_reference.short_description = "参考字段"

    def get_condition_symbol(self, obj):
        return ' '.join([i.symbol for i in obj.rule.all()])
    get_condition_symbol.short_description = "符号"

    def get_condition_case(self, obj):
        return ' '.join([i.case for i in obj.rule.all()])
    get_condition_case.short_description = "条件"

    def get_form(self, request, obj=None, **kwargs):
        help_texts = {
            'condition': '案例：如需要规定某个差错，30天内重复两次以上双倍扣罚的规则，则条件设为：“日期|<=90day|*2“',
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
        return super(RewardAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ShiftTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey(request, db_field, kwargs, 'team', Team)
        return super(ShiftTypeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_model_perms(self, request):
        return return_get_model_perms(self, request)


class ShiftAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'score', 'workload', 'bonus')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey(request, db_field, kwargs, 'team', Team)
        return super(ShiftAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ReferenceTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey(request, db_field, kwargs, 'team', Team)
        return super(ReferenceTypeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_model_perms(self, request):
        return return_get_model_perms(self, request)


class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('type', 'name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = return_formfield_for_foreignkey(request, db_field, kwargs, 'team', Team)
        return super(ReferenceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class RewardRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'reward', 'get_reference', 'title', 'level')
    list_display_links = ('reward',)
    filter_horizontal = ('reference',)
    list_filter = (
        ('date', DateRangeFilter), 'user__team'
    )
    change_list_template = 'admin/reward_summary_change_list.html'

    def get_reference(self, obj):
        return ' '.join([i.name for i in obj.reference.all()])
    get_reference.short_description = "影响"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            try:
                team_id = request.user.team.id
                if db_field.name == 'reference':
                    kwargs["queryset"] = Reference.objects.filter(team__related_parent__iregex=r'\D%s\D' % str(team_id))
            except:
                pass
        return super(RewardRecordAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ["created_user", ]
        else:
            return []

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            if not request.user.is_superuser:
                obj.created_user = request.user
                super().save_model(request, obj, form, change)
            else:
                super().save_model(request, obj, form, change)


class WorkloadRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'shift', 'position', 'start_datetime', 'end_datetime', 'assigned_team')

    list_filter = (
        ('start_datetime', DateTimeRangeFilter),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = return_get_queryset(request, qs)
        return qs

# Article._meta.get_field('title').verbose_name


admin.site.register(Rule, RuleAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(PositionType, PositionTypeAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(SkillType, SkillTypeAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(RewardType, RewardTypeAdmin)
admin.site.register(Reward, RewardAdmin)
admin.site.register(ShiftType, ShiftTypeAdmin)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(ReferenceType, ReferenceTypeAdmin)
admin.site.register(Reference, ReferenceAdmin)
admin.site.register(RewardRecord, RewardRecordAdmin)
admin.site.register(WorkloadRecord, WorkloadRecordAdmin)
