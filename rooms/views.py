import random
import string
from datetime import timezone

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, Exists, OuterRef, Q
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from catalog.models import Title
from library.models import Entry
from rooms.models import Candidate, Membership, Room, Vote


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


def get_user_rooms(user, status, page):

    rooms = Room.objects.filter(memberships__user=user)

    message = ""
    if not rooms.exists():
        message = "No tienes salas asociadas"

    if status:
        rooms = rooms.filter(status=status)

    if not rooms.exists():
        message = "No hay resultados para tu búsqueda"

    p = Paginator(rooms, 5)

    page_obj = p.get_page(page)

    return {"page_obj": page_obj, "message": message}


def rooms(request: HttpRequest):

    if not request.user.is_authenticated:
        return redirect("index")

    if request.method == "GET":
        status = request.GET.get("status", "").strip()
        page = request.GET.get("page", None)

        obj = get_user_rooms(request.user, status, page)

        return render(request, "rooms/list.html", obj)


@login_required
def room_list(request: HttpRequest):

    if request.method == "GET":
        status = request.GET.get("status", "").strip()
        page = request.GET.get("page", None)

        obj = get_user_rooms(request.user, status, page)

        return render(request, "rooms/room_list.html", obj)


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


@login_required
def room_join(request: HttpRequest):
    if request.method == "POST":
        invitation_code = request.POST.get("invitation_code", "").upper().strip()
        if not invitation_code:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "CODE_ERROR",
                    "message": "Introduce un código",
                },
                status=400,
            )
        try:
            room = Room.objects.get(invitation_code=invitation_code)

        except Room.DoesNotExist:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "DOES_NOT_EXISTS_ERROR",
                    "message": "La sala no existe",
                },
                status=400,
            )

        if room.status == Room.RoomStatus.CLOSED:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "CLOSED_ROOM_ERROR",
                    "message": "La sala está cerrada",
                },
                status=400,
            )

        Membership.objects.get_or_create(
            room=room,
            user=request.user,
        )

        url = reverse("room_detail", kwargs={"invitation_code": invitation_code})

        return JsonResponse(
            {
                "ok": True,
                "redirect_url": url,
                "message": f"Te has unido a {room.name}",
            },
            status=200,
        )


@login_required
def room_detail(request: HttpRequest, invitation_code):
    if request.method == "GET":
        room = get_object_or_404(Room, invitation_code=invitation_code)
        titles = Title.objects.all()

        candidates = room.candidates.annotate(
            up_count=Count("votes", filter=Q(votes__position=Vote.VotePosition.UP)),
            down_count=Count("votes", filter=Q(votes__position=Vote.VotePosition.DOWN)),
            voted_up=Exists(
                Vote.objects.filter(
                    candidate=OuterRef("pk"),
                    user=request.user,
                    position=Vote.VotePosition.UP,
                )
            ),
            voted_down=Exists(
                Vote.objects.filter(
                    candidate=OuterRef("pk"),
                    user=request.user,
                    position=Vote.VotePosition.DOWN,
                )
            ),
        )
        try:
            membership = Membership.objects.get(room=room, user=request.user)
        except Membership.DoesNotExist:
            return redirect("rooms")

        message = ""

        if room.candidates.count():
            message = "Todavía no hay candidatos"

        return render(
            request,
            "rooms/detail.html",
            {
                "message": message,
                "room": room,
                "titles": titles,
                "candidates": candidates,
            },
        )


@login_required
def room_exit(request: HttpRequest):
    if request.method == "POST":
        invitation_code = request.POST.get("invitation_code", "")
        try:
            membership = Membership.objects.get(
                room__invitation_code=invitation_code, user=request.user
            )

            if membership.room.host == request.user:
                return JsonResponse(
                    {
                        "ok": False,
                        "error": "NOT_ALLOWED_ERROR",
                        "message": "No puedes salir de tu propia sala",
                    },
                    status=403,
                )
        except Membership.DoesNotExist:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "DOES_NOT_EXISTS_ERROR",
                    "message": "No eres miembro de esta sala",
                },
                status=400,
            )

        membership.delete()

        return JsonResponse(
            {"ok": True, "message": "Has salido de la sala"}, status=200
        )


@login_required
def candidate_list(request: HttpRequest, invitation_code):
    if request.method == "GET":
        try:
            room = Room.objects.get(invitation_code=invitation_code)
        except Room.DoesNotExist:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "DOES_NOT_EXISTS_ERROR",
                    "message": "La sala no existe",
                },
                status=404,
            )
        candidates = room.candidates.annotate(
            up_count=Count("votes", filter=Q(votes__position=Vote.VotePosition.UP)),
            down_count=Count("votes", filter=Q(votes__position=Vote.VotePosition.DOWN)),
            voted_up=Exists(
                Vote.objects.filter(
                    candidate=OuterRef("pk"),
                    user=request.user,
                    position=Vote.VotePosition.UP,
                )
            ),
            voted_down=Exists(
                Vote.objects.filter(
                    candidate=OuterRef("pk"),
                    user=request.user,
                    position=Vote.VotePosition.DOWN,
                )
            ),
        )
        return render(request, "rooms/candidate_list.html", {"candidates": candidates})


@login_required
def propose_title(request: HttpRequest, invitation_code):
    if request.method == "POST":
        title_id = request.POST.get("title_id", None)

        try:
            title = Title.objects.get(pk=title_id)
        except Title.DoesNotExist:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "DOES_NOT_EXISTS_ERROR",
                    "message": "El título seleccionado no existe",
                },
                status=404,
            )

        room = get_object_or_404(Room, invitation_code=invitation_code)

        if not Membership.objects.filter(room=room, user=request.user).exists():
            return JsonResponse(
                {
                    "ok": False,
                    "error": "DOES_NOT_EXISTS_ERROR",
                    "message": "No eres miembro de esta sala",
                },
                status=403,
            )

        if room.status == Room.RoomStatus.CLOSED:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "CLOSED_ROOM_ERROR",
                    "message": "La sala está cerrada",
                },
                status=403,
            )
        try:
            Candidate.objects.create(
                title=title,
                room=room,
                proposed_by=request.user,
                origin=Candidate.CandidateOrigin.MANUAL,
            )
        except IntegrityError:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "INTEGRITY_ERROR",
                    "message": "Este título ya está propuesto",
                },
                status=400,
            )

        return JsonResponse({"ok": True, "message": "Título propuesto"}, status=200)


@login_required
def vote(request: HttpRequest, candidate_id, invitation_code):
    if request.method == "POST":
        position = request.POST.get("position", "")
        if not position:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "INTEGRITY_ERROR",
                    "message": "El valor del voto no es válido",
                },
                status=400,
            )
        try:
            candidate = Candidate.objects.get(pk=candidate_id)
        except Candidate.DoesNotExist:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "DOES_NOT_EXISTS_ERROR",
                    "message": "La propuesta no existe",
                },
                status=404,
            )

        if not Membership.objects.filter(
            room=candidate.room, user=request.user
        ).exists():
            return JsonResponse(
                {
                    "ok": False,
                    "error": "DOES_NOT_EXISTS_ERROR",
                    "message": "No eres miembro de esta sala",
                },
                status=403,
            )

        if candidate.room.status == Room.RoomStatus.CLOSED:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "CLOSED_ROOM_ERROR",
                    "message": "La sala está cerrada",
                },
                status=404,
            )

        vote = Vote.objects.filter(candidate=candidate, user=request.user).first()

        if not vote:
            Vote.objects.create(
                candidate=candidate, user=request.user, position=position
            )
            return JsonResponse(
                {
                    "ok": True,
                    "message": "Voto registrado",
                },
                status=200,
            )

        if vote.position == position:
            vote.delete()

            return JsonResponse(
                {
                    "ok": True,
                    "message": "Voto retirado",
                },
                status=200,
            )

        else:
            vote.position = position
            vote.save()

            return JsonResponse(
                {
                    "ok": True,
                    "message": "Voto registrado",
                },
                status=200,
            )


@login_required
def close_room(request: HttpRequest):
    if request.method == "POST":
        invitation_code = request.POST.get("invitation_code", "")
        candidate_id = request.POST.get("candidate_id", "")

        try:
            candidate = Candidate.objects.get(pk=candidate_id)
        except Candidate.DoesNotExist:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "DOES_NOT_EXISTS_ERROR",
                    "message": "La propuesta no existe",
                },
                status=400,
            )

        try:
            room = Room.objects.get(invitation_code=invitation_code)
        except Room.DoesNotExist:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "DOES_NOT_EXISTS_ERROR",
                    "message": "La sala no existe",
                },
                status=404,
            )

        if request.user != room.host:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "NOT_ALLOWED_ERROR",
                    "message": "No eres el anfitrión de esta sala",
                },
                status=403,
            )

        if room.status == room.RoomStatus.CLOSED:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "CLOSED_ROOM_ERROR",
                    "message": "La sala ya está cerrada",
                },
                status=409,
            )

        if candidate.room != room:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "INTEGRITY_ERROR",
                    "message": "La propuesta no pertenece a esta sala",
                },
                status=400,
            )
        try:
            with transaction.atomic():
                room.status = Room.RoomStatus.CLOSED
                room.winner = candidate
                room.closed_at = timezone.now()
                room.save()
        except IntegrityError:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "INTEGRITY_ERROR",
                    "message": "No se pudo cerrar la sala",
                },
                status=400,
            )

        return JsonResponse(
            {
                "ok": True,
                "message": "Sala cerrada",
            },
            status=200,
        )
