from django.http import HttpRequest
from django.shortcuts import redirect, render


def index(request: HttpRequest):
    if not request.user.is_authenticated:
        return render(request, "core/index.html")

    return redirect("dashboard")
