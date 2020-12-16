from django.contrib import admin
from team.models import Team
from user.models import User


class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "get_related_name", )
    list_display_links = ("name", )
    search_fields = ("name", "get_related_name", )
    filter_horizontal = ("user__user", )
    fields = ("name", "user__user",)
    readonly_fields = ("related_parent", )

    def get_head_parent(self, obj):
        if obj.parent != "":
            head_parent = obj.parent
            while True:
                try:
                    head_parent = head_parent.parent
                except:
                    return head_parent
        else:
            return obj

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(parent=request.user.branch_id)

    def get_branch_name(self, obj):
        return obj.branch.branch_id
    get_branch_name.short_description = "成员"

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # db_field.name 本模型下的字段名称
        if db_field.name == "user":
            # 过滤
            kwargs["queryset"] = User.objects.filter(team_id=request.user.branch_id)
            # filter_horizontal 保持横向展示
            from django.contrib.admin import widgets
            kwargs['widget'] = widgets.FilteredSelectMultiple(
                db_field.verbose_name,
                db_field.name in self.filter_vertical
            )
        return super(TeamAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            if change:
                if obj.parent != form.cleaned_data["parent"]:
                    related_parent = [obj.parent.id]
                    if obj.parent:
                        parent = obj.parent
                        while True:
                            try:
                                related_parent.insert(0, parent.id)
                                parent = parent.parent
                            except:
                                break
                        obj.related_parent = str(related_parent)
                super().save_model(request, obj, form, change)


admin.site.register(Team, TeamAdmin)
