from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse


def auth_register(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("dashboard")
    elif request.method == "POST":
        username = request.POST.get("register-user", "")
        email = request.POST.get("register-email", "")
        password = request.POST.get("register-password", "")
        confirm_password = request.POST.get("confirm-password", "")

        if password != confirm_password:
            return render(
                request,
                "accounts/register.html",
                {"message": "Las contraseñas no coinciden"},
            )

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "accounts/register.html",
                {"message": "Ya existe un usuario con el mismo nombre"},
            )
        login(request, user)

        return redirect("dashboard")

    return render(request, "accounts/register.html")


def auth_login(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("dashboard")
    elif request.method == "POST":
        username = request.POST.get("login-user", "")
        password = request.POST.get("login-password", "")
        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(
                request,
                "accounts/login.html",
                {"message": "Usuario y/o contraseña inválidos"},
            )

        login(request, user)
        return redirect("dashboard")

    return render(request, "accounts/login.html")


@login_required
def auth_logout(request: HttpRequest):
    logout(request)
    return HttpResponseRedirect(reverse("index"))
