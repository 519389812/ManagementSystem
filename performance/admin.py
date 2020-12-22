from django.contrib import admin
import pandas as pd
from performance.models import Rule


class RuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'range', 'condition', 'calculation')

    def get_form(self, request, obj=None, **kwargs):
        help_texts = {'range': '仅在类别为频率时需填写，内容为天数，表示在多少天范围内发生的频率'}
        kwargs.update({'help_texts': help_texts})
        return super(RuleAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, *args, **kwargs):
        if db_field.name == 'parent_comment':
            try:
                obj_id = request.resolver_match.args[0]  # 这里获取当前对象id，非常重要
                kwargs['queryset'] = Comment.objects.filter(parent_comment=None).exclude(id=int(obj_id))  # 添加过滤条件
            except:
                kwargs['queryset'] = Comment.objects.filter(parent_comment=None)
        return super(CommentAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class AddWorkloadAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'worktime', 'department', 'created_time', 'remark', 'updated_time')


class ScoreAdmin(admin.ModelAdmin):
    search_fields = ['employee_id__id', 'po_score', 'date', 'penalty_score', 'skill_score ', 'total_score', ]
    list_display = ('id', 'employee_id', 'skill_score', 'penalty_score', 'po_score', 'date', 'remark', 'total_score')

    # def get_skill_score(self):
    #     return self.skill_score
    #
    # get_skill_score.short_description = "技能分数"
    #
    # def get_penalty_score(self):
    #     return self.penalty_score
    #
    # get_penalty_score.short_description = "奖惩分数"
    #
    # def get_po_score(self):
    #     return self.po_score
    #
    # get_po_score.short_description = "岗位分数"
    #
    # # 创建或保存评价时，自动获取新的岗位分数和总分
    # def save(self, *args, **kwargs):
    #     po_score = self.get_po_score()
    #     self.po_score = po_score
    #
    #     skill_score = self.get_skill_score()
    #     self.skill_score = skill_score
    #
    #     penalty_score = self.get_penalty_score()
    #     self.penalty_score = penalty_score
    #
    #     self.total_score = po_score + self.skill_score + self.penalty_score
    #     super(Score, self).save(*args, **kwargs)
    #
    # def get_total_score(self, obj):
    #     self.total_score = self.skill_score + self.penalty_score + self.po_score
    #     data = Score.objects.filter()
    #     data = pd.DataFrame(data)
    #     data = pd.pivot_table()
    #     return obj.total_score
    #
    # get_total_score.short_description = "总分"


class SkillAdmin(admin.ModelAdmin):
    list_filter = ('name',)  # 过滤器
    search_fields = ['name', ]  # 设置搜索栏范围，如果有外键，要注明外键的哪个字段，双下划线
    list_display = ('id', 'name', 'type', 'score')  # 在页面上显示的字段，若不设置则显示 models.py 中 __unicode__(self) 中所返回的值
    list_display_links = ('id', 'name', 'type', 'score',)  # 设置页面上哪个字段可单击进入详细页面


class ShiftAdmin(admin.ModelAdmin):
    list_filter = ('name',)  # 过滤器
    search_fields = ['name', ]  # 设置搜索栏范围，如果有外键，要注明外键的哪个字段，双下划线
    list_display = ('id', 'name',)  # 在页面上显示的字段，若不设置则显示 models.py 中 __unicode__(self) 中所返回的值
    list_display_links = ('id', 'name',)


class PositionAdmin(admin.ModelAdmin):
    list_filter = ('name',)  # 过滤器
    search_fields = ['name', 'po_score', 'staff_score']  # 设置搜索栏范围，如果有外键，要注明外键的哪个字段，加双下划线，如employee_name__name
    list_display = ('id', 'name', 'po_score', 'staff_score')  # 在页面上显示的字段，若不设置则显示 models.py 中 __unicode__(self) 中所返回的值
    list_display_links = ('id', 'name', 'po_score', 'staff_score')  # 设置页面上哪个字段可单击进入详细页面
    # list_editable = ['name', 'score']  # 直接编辑字段
    # fields = ('category', 'book')  # 设置添加/修改详细信息时，哪些字段显示，在这里 remark 字段将不显示


class PenaltyAdmin(admin.ModelAdmin):
    list_filter = ('type', 'name',)  # 过滤器
    search_fields = ['name', 'type', ]  # 设置搜索栏范围，如果有外键，要注明外键的哪个字段，双下划线
    list_display = ('id', 'type', 'name', 'score')  # 在页面上显示的字段，若不设置则显示 models.py 中 __unicode__(self) 中所返回的值
    list_display_links = ('id', 'type', 'name', 'score',)  # 设置页面上哪个字段可单击进入详细页面
    # list_editable = ['name', 'sex', 'staff_id']  # 直接编辑字段
    # fields = ('category', 'book')  # 设置添加/修改详细信息时，哪些字段显示，在这里 remark 字段将不显示


def


admin.site.register(Shift, ShiftAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Penalty, PenaltyAdmin)
admin.site.register(Skill, SkillAdmin)


admin.site.register(AddWorkload, AddWorkloadAdmin)
admin.site.register(Score, ScoreAdmin)
