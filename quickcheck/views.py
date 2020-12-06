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
