from django.contrib import admin
from document.models import DocxInit, ContentStorage, SignatureStorage
from document.docx_handler import *
import json


class DocxInitAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "template_name", "docx_name", "content", "version", "create_datetime", "edit_datetime")
    list_display_links = ("id",)
    filter_horizontal = ("team", )  # 设置多对多字段的筛选器

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            if change:
                obj.version = str(int(obj.version) + 1)
                SignatureStorage.objects.filter(docx__id=obj.id).delete()
            super().save_model(request, obj, form, change)


class ContentStorageAdmin(admin.ModelAdmin):
    list_display = ("id", "docx", "user", "content", "get_signature", "create_datetime", "edit_datetime")
    list_display_links = ("id",)

    def get_signature(self, obj):
        return "是" if len(obj.signature) > 0 else ""
    get_signature.short_description = "是否签名"


class SignatureStorageAdmin(admin.ModelAdmin):
    list_display = ("id", "docx", "user", "content", "get_signature", "create_datetime")
    list_display_links = ("id",)

    def get_signature(self, obj):
        return "是" if len(obj.signature) > 0 else ""
    get_signature.short_description = "是否签名"


admin.site.register(DocxInit, DocxInitAdmin)
admin.site.register(ContentStorage, ContentStorageAdmin)
admin.site.register(SignatureStorage, SignatureStorageAdmin)

