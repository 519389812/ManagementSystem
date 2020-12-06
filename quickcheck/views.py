from django.shortcuts import render


def quickcheck(request):
    return render(request, "quickcheck.html")


def outbound_limit(request):
    return render(request, "outbound_limit.html")


def outbound_limit_singapore(request):
    return render(request, "outbound_limit_singapore.html")
