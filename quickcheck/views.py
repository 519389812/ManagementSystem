from django.shortcuts import render
from user.views import check_authority


@check_authority
def quickcheck(request):
    return render(request, "quickcheck.html")


@check_authority
def outbound_limit(request):
    return render(request, "outbound_limit.html")


@check_authority
def outbound_limit_singapore(request):
    return render(request, "outbound_limit_singapore.html")


@check_authority
def outbound_limit_cambodia(request):
    return render(request, "outbound_limit_cambodia.html")


@check_authority
def outbound_limit_thailand(request):
    return render(request, "outbound_limit_thailand.html")
