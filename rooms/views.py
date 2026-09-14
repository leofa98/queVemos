from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render


@login_required
def dashboard(request: HttpRequest):
    if not request.user.is_authenticated:
        return redirect("index")

    return render(request, "rooms/dashboard.html")
