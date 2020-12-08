"""ManagementSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from . import views as main_views
from document import views as document_views
from user import views as user_views
from quickcheck import views as quickcheck_views
from django.shortcuts import render
from ManagementSystem.views import error_404, error_400, error_403, error_500


handler404 = error_404
handler400 = error_400
handler403 = error_403
handler500 = error_500


urlpatterns = [
    # main
    path('admin/', admin.site.urls),
    path('', main_views.home, name="home"),
    path('error_404/', main_views.error_404, name="error_404"),
    path('error_400/', main_views.error_400, name="error_400"),
    path('contact/', main_views.contact, name="contact"),
    path('about/', main_views.about, name="about"),

    # user
    path('login/', user_views.login, name="login"),
    path('logout/', user_views.logout, name="logout"),
    path('register/', user_views.register, name="register"),
    path('check_username_validate/', user_views.check_username_validate, name="check_username_validate"),
    path('check_password_validate/', user_views.check_password_validate, name="check_password_validate"),
    path('check_lastname_validate/', user_views.check_lastname_validate, name="check_lastname_validate"),
    path('check_firstname_validate/', user_views.check_firstname_validate, name="check_firstname_validate"),
    path('check_register_valudate/', user_views.check_register_valudate, name="check_register_valudate"),
    re_path('login/(.+)/', user_views.login, name="login"),
    re_path('register/(.+)/', user_views.register, name="register"),

    # document
    path('document/', document_views.document, name="document"),
    path('document/translate_words/', document_views.translate_words, name="translate_words"),
    path('document/delete_translate_words/', document_views.delete_translate_words, name="delete_translate_words"),
    path('error_docx_closed/', document_views.error_docx_closed, name="error_docx_closed"),
    path('error_docx_opened/', document_views.error_docx_opened, name="error_docx_opened"),
    path('error_docx_missing/', document_views.error_docx_missing, name="error_docx_missing"),
    path('document/preview_template/', document_views.preview_template, name="preview_template"),
    path('document/introduce_docx/', document_views.introduce_docx, name="introduce_docx"),
    path('document/select_template/', document_views.select_template, name="select_template"),
    path('document/view_docx_list/', document_views.view_docx_list, name="view_docx_list"),
    path('document/init_docx/', document_views.init_docx, name="init_docx"),
    path('document/upload_template/', document_views.upload_template, name="upload_template"),
    path('document/delete_template/', document_views.delete_template, name="delete_template"),
    path('document/fill_signature/', document_views.fill_signature, name="fill_signature"),
    path('document/supervisor_signature/', document_views.supervisor_signature, name="supervisor_signature"),
    re_path('document/translate_words/(.+)/$', document_views.translate_words, name="translate_words"),
    re_path('document/select_template/(.+)/$', document_views.select_template, name="select_template"),
    re_path('document/upload_template/(.+)/$', document_views.upload_template, name="upload_template"),
    re_path('document/write_init_docx/(.+)/$', document_views.write_init_docx, name="write_init_docx"),
    re_path('document/view_docx/(\d+)/$', document_views.view_docx, name="view_docx"),
    re_path('document/view_docx/(\d+)/(.+)/$', document_views.view_docx, name="view_docx"),
    re_path('document/fill_docx/(.+)/(.+)/$', document_views.fill_docx, name="fill_docx"),
    re_path('document/close_docx/(.+)/$', document_views.close_docx, name="close_docx"),
    re_path('document/download_docx/(.+)/$', document_views.download_docx, name="download_docx"),
    re_path('document/supervise_docx/', document_views.supervise_docx, name="supervise_docx"),

    # quickcheck
    path('quickcheck/', quickcheck_views.quickcheck, name="quickcheck"),
    path('quickcheck/outbound_limit', quickcheck_views.outbound_limit, name="outbound_limit"),
    path('quickcheck/outbound_limit/singapore', quickcheck_views.outbound_limit_singapore, name="outbound_limit_singapore"),
]
