from django.contrib import admin
from user.models import User, EmailVerifyRecord
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Team', {'fields': ('team',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'ip_address', 'date_joined')}),
    )
    list_display = ('username', 'last_name', 'first_name', 'last_login', 'ip_address', 'is_active')
    filter_horizontal = ('groups', 'user_permissions', )


class EmailVerifyRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'code', 'type', 'close_datetime')


admin.site.register(User, CustomUserAdmin)
admin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)

admin.site.site_header = '管理系统'
admin.site.site_title = '管理系统'
admin.site.index_title = '管理系统'
