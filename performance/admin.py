from django.contrib import admin
from performance.models import Level, RuleCondition, Rule, PositionType, Position, SkillType, Skill, RewardType, Reward, ShiftType, Shift, AddWorkload, ReferenceType, Reference, AddReward
from team.models import Team
from django.contrib.admin import widgets


class RuleConditionAdmin(admin.ModelAdmin):
    list_display = ('id', 'reference', 'symbol', 'case', 'get_team')
    filter_horizontal = ('team',)

    def get_team(self, obj):
        return ' '.join([i.name for i in obj.team.all()])
    get_team.short_description = "目标组"

    def get_form(self, request, obj=None, **kwargs):
        help_texts = {
            'reference': '案例：如需要规定三个月内，同样差错两次以上，进行加倍扣罚的规则，则“参考”填写参考的日期字段date，表示以日期为规则',
            'symbol': '“符号”填写<=，表示多少天内',
            'case': '“条件”填写2，表示两次以上',
        }
        kwargs.update({'help_texts': help_texts})
        return super(RuleConditionAdmin, self).get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team__in=request.user.team.all())

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "team":
            # 过滤
            kwargs["queryset"] = request.user.team.all()
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(RuleConditionAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class RuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_condition_reference', 'get_condition_symbol', 'get_condition_case', 'calculation')
    filter_horizontal = ('condition', 'team')

    def get_condition_reference(self, obj):
        return ' '.join([i.reference for i in obj.rule.all()])
    get_condition_reference.short_description = "参考字段"

    def get_condition_symbol(self, obj):
        return ' '.join([i.symbol for i in obj.rule.all()])
    get_condition_symbol.short_description = "符号"

    def get_condition_case(self, obj):
        return ' '.join([i.case for i in obj.rule.all()])
    get_condition_case.short_description = "条件"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team__in=request.user.team.all())

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "condition":
            # 过滤
            kwargs["queryset"] = RuleCondition.objects.filter(team__in=request.user.team.all())
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        if db_field.name == "team":
            # 过滤
            kwargs["queryset"] = request.user.team.all()
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(RuleAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class LevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    filter_horizontal = ('rule', 'team')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team__in=request.user.team.all())

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "team":
            # 过滤
            kwargs["queryset"] = request.user.team.all()
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(LevelAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class PositionTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    filter_horizontal = ('team',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team__in=request.user.team.all())

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "team":
            # 过滤
            kwargs["queryset"] = request.user.team.all()
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(PositionTypeAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'score', 'workload', 'bonus')
    filter_horizontal = ('team',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team__in=request.user.team.all())

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "condition":
            # 过滤
            kwargs["queryset"] = PositionType.objects.filter(team__in=request.user.team.all())
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        if db_field.name == "team":
            # 过滤
            kwargs["queryset"] = request.user.team.all()
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(PositionAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class SkillTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    filter_horizontal = ('team',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team__in=request.user.team.all())

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "team":
            # 过滤
            kwargs["queryset"] = request.user.team.all()
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(SkillTypeAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class SkillAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'score', 'workload', 'bonus', 'get_rule')
    filter_horizontal = ('rule', 'team')

    def get_rule(self, obj):
        return ' '.join([i.name for i in obj.rule.all()])
    get_rule.short_description = "规则"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team__in=request.user.team.all())

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "condition":
            # 过滤
            kwargs["queryset"] = SkillType.objects.filter(team__in=request.user.team.all())
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        if db_field.name == "team":
            # 过滤
            kwargs["queryset"] = request.user.team.all()
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(SkillAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class RewardTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    filter_horizontal = ('team',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team__in=request.user.team.all())

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "team":
            # 过滤
            kwargs["queryset"] = request.user.team.all()
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(RewardTypeAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class RewardAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'score', 'workload', 'bonus', 'get_rule')
    filter_horizontal = ('rule', 'team')

    def get_rule(self, obj):
        return ' '.join([i.name for i in obj.rule.all()])
    get_rule.short_description = "规则"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team__in=request.user.team.all())

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "condition":
            # 过滤
            kwargs["queryset"] = RewardType.objects.filter(team__in=request.user.team.all())
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        if db_field.name == "team":
            # 过滤
            kwargs["queryset"] = request.user.team.all()
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(RewardAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class ShiftTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    filter_horizontal = ('team',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team__in=request.user.team.all())

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "team":
            # 过滤
            kwargs["queryset"] = request.user.team.all()
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(ShiftTypeAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class ShiftAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'score', 'workload', 'bonus')
    filter_horizontal = ('team',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team__in=request.user.team.all())

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "condition":
            # 过滤
            kwargs["queryset"] = ShiftType.objects.filter(team__in=request.user.team.all())
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        if db_field.name == "team":
            # 过滤
            kwargs["queryset"] = request.user.team.all()
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(ShiftAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class AddWorkloadAdmin(admin.ModelAdmin):
    list_display = ('user', 'shift', 'position', 'start_datetime', 'end_datetime', 'assigned_team')
    filter_horizontal = ('team',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team__in=request.user.team.all())

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "team":
            # 过滤
            kwargs["queryset"] = request.user.team.all()
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(AddWorkloadAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class ReferenceTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    filter_horizontal = ('team',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team__in=request.user.team.all())

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "team":
            # 过滤
            kwargs["queryset"] = request.user.team.all()
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(ReferenceTypeAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('type', 'name')
    filter_horizontal = ('team',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team__in=request.user.team.all())

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "condition":
            # 过滤
            kwargs["queryset"] = ReferenceType.objects.filter(team__in=request.user.team.all())
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        if db_field.name == "team":
            # 过滤
            kwargs["queryset"] = request.user.team.all()
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(ReferenceAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class AddRewardAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'reward', 'get_reference', 'title', 'level')
    filter_horizontal = ('reference', 'team')

    def get_reference(self, obj):
        return ' '.join([i.name for i in obj.reference.all()])
    get_reference.short_description = "规则"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(team__in=request.user.team.all())

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "reference":
            # 过滤
            kwargs["queryset"] = Reference.objects.filter(team__in=request.user.team.all())
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        if db_field.name == "team":
            # 过滤
            kwargs["queryset"] = request.user.team.all()
            # filter_horizontal 保持横向展示
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(AddRewardAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

# Article._meta.get_field('title').verbose_name


admin.site.register(Level, LevelAdmin)
admin.site.register(RuleCondition, RuleConditionAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(PositionType, PositionTypeAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(SkillType, SkillTypeAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(RewardType, RewardTypeAdmin)
admin.site.register(Reward, RewardAdmin)
admin.site.register(ShiftType, ShiftTypeAdmin)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(AddWorkload, AddWorkloadAdmin)
admin.site.register(ReferenceType, ReferenceTypeAdmin)
admin.site.register(Reference, ReferenceAdmin)
admin.site.register(AddReward, AddRewardAdmin)
