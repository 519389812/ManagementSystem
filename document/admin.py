from django.contrib import admin
from document.models import DocxInit, ContentStorage, SignatureStorage
from document.docx_handler import *
import json


class DocxInitAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "template_name", "docx_name", "content", "version", "create_datetime", "edit_datetime")
    list_display_links = ("id",)
    # fields = ()  # 设置添加/修改详细信息时，哪些字段显示，在这里 remark 字段将不显示
    # readonly_fields = ()
    # actions = []
    # search_fields = ()
    # date_hierarchy = 'create_datetime'  # 详细时间分层筛选
    # list_filter = ()
    filter_horizontal = ("team", )  # 设置多对多字段的筛选器

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            if change:
                obj.version = str(int(obj.version) + 1)
                SignatureStorage.objects.filter(docx__id=obj.id).delete()
            super().save_model(request, obj, form, change)


class ContentStorageAdmin(admin.ModelAdmin):
    list_display = ("id", "docx", "user", "content", "signature", "create_datetime", "edit_datetime")
    list_display_links = ("id",)


class SignatureStorageAdmin(admin.ModelAdmin):
    list_display = ("id", "docx", "user", "content", "signature", "create_datetime")
    list_display_links = ("id",)


admin.site.register(DocxInit, DocxInitAdmin)
admin.site.register(ContentStorage, ContentStorageAdmin)
admin.site.register(SignatureStorage, SignatureStorageAdmin)

