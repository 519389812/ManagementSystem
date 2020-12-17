from django.contrib import admin
from team.models import Team
from user.models import User
import json


class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "related_parent_name", )
    list_display_links = ("name", )
    search_fields = ("name", )
    fields = ("name", "parent", "related_parent", "related_parent_name", )
    readonly_fields = ("related_parent", "related_parent_name", )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(related_parent=request.user.team.related_parent)

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

    def related_parent_name(self, obj):
        related_parent_id_list = json.loads(obj.related_parent)
        related_parent_name = '-->'.join([Team.objects.get(id=id).name for id in related_parent_id_list])
        return related_parent_name
    related_parent_name.short_description = "组织关系"

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

    def get_related_parent(self, parent, related_parent):
        while True:
            try:
                related_parent.insert(0, parent.id)
                parent = parent.parent
            except:
                return related_parent

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            if not change:
                super().save_model(request, obj, form, change)
                related_parent = [obj.id]
                if form.cleaned_data["parent"]:
                    parent = form.cleaned_data["parent"]
                    related_parent = self.get_related_parent(parent, related_parent)
                obj.related_parent = json.dumps(related_parent)
            else:
                if obj.parent != form.cleaned_data["parent"]:
                    if not obj.parent:
                        related_parent = [obj.id]
                        parent = form.cleaned_data["parent"]
                        related_parent = self.get_related_parent(parent, related_parent)
                    elif not form.cleaned_data["parent"]:
                        pass
                    else:
                        pass
            super().save_model(request, obj, form, change)


admin.site.register(Team, TeamAdmin)
