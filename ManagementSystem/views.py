from django.shortcuts import render
import os
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_v1_5
import base64
from urllib import parse
from django.shortcuts import render
from django.http import *
# 当前路径钥匙地址
curr_dir = os.path.dirname(os.path.realpath(__file__))
private_key_file = os.path.join(curr_dir, "my_private_rsa_key.bin")  # 密钥
public_key_file = os.path.join(curr_dir, "my_rsa_public.pem")  # 公钥


def home(request):
    return render(request, "home.html")


def error_404(request, exception, template_name='templates/error_404.html'):
    return render(request, "error_404.html")


def error_400(request, exception, template_name='templates/error_400.html'):
    return render(request, "error_400.html")


def error_403(request, exception, template_name='templates/error_403.html'):
    return render(request, "error_403.html")


def error_500(request):
    return render(request, "error_500.html")


def contact(request):
    return render(request, "contact.html")


def about(request):
    return render(request, "about.html")


# 解码
def decrypt_data(inputdata):
    # URLDecode
    data = parse.unquote(inputdata)
    # base64decode
    data = base64.b64decode(data)
    # 读取密钥
    private_key = RSA.import_key(open(curr_dir + "/my_private_rsa_key.bin").read())
    # 使用 PKCS1_v1_5解密
    cipher_rsa = PKCS1_v1_5.new(private_key)
    # 当解密失败，会返回 sentinel
    sentinel = None
    ret = cipher_rsa.decrypt(data, sentinel)
    return ret.decode()  # 解码


# 自定义注解 过滤GET和POST请求解码。
def custom_decode(fun):
    def check(request, *args, **kwargs):
        if "GET" == request.method:
            request.GET = request.GET.copy()  # request设置可以修改
            for i in list(request.GET):
                request.GET[i] = decrypt_data(request.GET[i])  # 解码
        elif "POST" == request.method:
            request.POST = request.POST.copy()
            for i in list(request.POST):
                request.POST[i] = decrypt_data(request.POST[i])
        return fun(request, *args, **kwargs)
    return check
