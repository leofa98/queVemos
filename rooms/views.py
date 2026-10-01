import random
import string

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render

from catalog.models import Title
from library.models import Entry
from rooms.models import Membership, Room


def dashboard(request: HttpRequest):
    if not request.user.is_authenticated:
        return redirect("index")

    status = request.GET.get("status", "").strip()
    query = request.GET.get("query", "").strip()
    page = request.GET.get("page", None)
    titles = Title.objects.all()

    entries = Entry.objects.filter(user=request.user)

    message = ""

    if not entries.exists():
        message = "No tienes entradas todavía"

    if status:
        entries = entries.filter(status=status)

    if query:
        entries = entries.filter(title__name__icontains=query)

    if not entries.exists():
        message = "No hay resultados para tu búsqueda"

    p = Paginator(entries, 5)
    page_obj = p.get_page(page)

    return render(
        request,
        "library/dashboard.html",
        {
            "page_obj": page_obj,
            "titles": titles,
            "message": message,
        },
    )


@login_required
def rooms(request: HttpRequest):

    if not request.user.is_authenticated:
        return redirect("index")

    if request.method == "GET":
        status = request.GET.get("status", "").strip()
        page = request.GET.get("page", None)

        rooms = Room.objects.filter(memberships__user=request.user)

        message = ""
        if not rooms.exists():
            message = "No tienes salas asociadas"

        if status:
            rooms = rooms.filter(status=status)

        if not rooms.exists():
            message = "No hay resultados para tu búsqueda"

        p = Paginator(rooms, 5)

        page_obj = p.get_page(page)

        return render(
            request, "rooms/list.html", {"page_obj": page_obj, "message": message}
        )


@login_required
def room_list(request: HttpRequest):
    if not request.user.is_authenticated:
        return redirect("index")

    if request.method == "GET":
        status = request.GET.get("status", "").strip()
        page = request.GET.get("page", None)

        rooms = Room.objects.filter(memberships__user=request.user)

        message = ""

        if not rooms.exists():
            message = "No tienes salas asociadas"

        if status:
            rooms = rooms.filter(status=status)

        if not rooms.exists():
            message = "No hay resultados para tu búsqueda"

        p = Paginator(rooms, 5)

        page_obj = p.get_page(page)

        return render(
            request, "rooms/room_list.html", {"page_obj": page_obj, "message": message}
        )


@login_required
def room_new(request: HttpRequest):
    if request.method == "POST":
        name = request.POST.get("name", "")
        allow_seen = request.POST.get("allow_seen", False)

        if not name:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "INTEGRITY_ERROR",
                    "message": "Completa el nombre de la sala",
                },
                status=400,
            )
        while True:
            invitation_code = "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
            )
            repeated = Room.objects.filter(invitation_code=invitation_code)

            if not repeated:
                break

        room = Room.objects.create(
            name=name,
            host=request.user,
            invitation_code=invitation_code,
            allow_seen=allow_seen,
        )

        try:
            Membership.objects.create(user=request.user, room=room)
        except IntegrityError:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "INTEGRITY_ERROR",
                    "message": "Tu membresía ya existe",
                },
                status=400,
            )

        return JsonResponse({"ok": True, "message": "Sala creada"}, status=200)
