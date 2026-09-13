from django.http import HttpRequest
from django.shortcuts import redirect, render


def index(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("dashboard")
    else:
        return render(request, "core/index.html")
