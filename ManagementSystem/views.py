from django.shortcuts import render


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
