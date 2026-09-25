from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render

from catalog.models import Title
from library.models import Entry


@login_required
def entry_new(request: HttpRequest):
    if request.method == "POST":
        title_id = request.POST.get("title", "")
        status = request.POST.get("status", "")
        rating = request.POST.get("rating", "")
        comment = request.POST.get("comment", "")

        try:
            title = Title.objects.get(pk=title_id)

        except Title.DoesNotExist:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "TITLE_NOT_FOUND",
                    "message": "El título seleccionado no existe",
                },
                status=400,
            )
        except IntegrityError:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "INTEGRITY_ERROR",
                    "message": "Ya existe una entrada para este título",
                },
                status=400,
            )
        if status not in ["seen", "pending", "dropped"]:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "INVALID_STATUS",
                    "message": "El estado no es válido",
                },
                status=400,
            )

        if rating:
            try:
                rating = int(rating)
                if not 1 <= rating <= 10:
                    return JsonResponse(
                        {
                            "ok": False,
                            "error": "INVALID_RATING",
                            "message": "La valoración es inválida",
                        }
                    )
            except ValueError:
                return JsonResponse(
                    {
                        "ok": False,
                        "error": "INVALID_RATING",
                        "message": "La valoración es inválida",
                    }
                )
        else:
            rating = None
        Entry.objects.create(
            user=request.user,
            title=title,
            status=status,
            rating=rating,
            comment=comment,
        )
        return JsonResponse({"ok": True}, status=200)


@login_required
def entry_edit(request: HttpRequest, entry_id):
    if request.method == "POST":
        entry = Entry.objects.get(pk=entry_id, user=request.user)

        if not entry:
            return JsonResponse({}, status=404)

        title_id = request.POST.get("title", "")
        status = request.POST.get("status", "")
        rating = request.POST.get("rating", "")
        comment = request.POST.get("comment", "")

        new_title = Title.objects.get(pk=title_id)
        if not new_title:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "INVALID_TITLE",
                    "message": "Título no seleccinado",
                },
                status=400,
            )
        if status not in ["seen", "pending", "dropped"]:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "INVALID_STATUS",
                    "message": "El estado no es válido",
                },
                status=400,
            )

        if rating:
            try:
                rating = int(rating)
                if not 1 <= rating <= 10:
                    return JsonResponse(
                        {
                            "ok": False,
                            "error": "INVALID_RATING",
                            "message": "La valoración no es válida",
                        },
                        status=400,
                    )
            except ValueError:
                return JsonResponse(
                    {
                        "ok": True,
                        "error": "INVALID_RATING",
                        "message": "La valoración no es válida",
                    },
                    status=400,
                )
        else:
            rating = None

        entry.status = status
        entry.title = new_title
        entry.comment = comment
        entry.rating = rating
        entry.save()

        return JsonResponse(
            {
                "ok": True,
            },
            status=200,
        )


@login_required
def remove_entry(request: HttpRequest, entry_id):
    if request.method == "POST":
        entry = Entry.objects.filter(pk=entry_id, user=request.user).first()
        if not entry:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "NOT_FOUND",
                    "message": "Esta entrada no existe",
                },
                status=404,
            )
        entry.delete()
        return JsonResponse({"ok": True}, status=200)


@login_required
def entry_list(request: HttpRequest):
    if request.method == "GET":
        status = request.GET.get("status", "").strip()
        query = request.GET.get("query", "").strip()
        page = request.GET.get("page", None)
        titles = Title.objects.all()

        has_entries = Entry.objects.exists()

        entries = Entry.objects.filter(user=request.user)

        message = ""

        if status:
            entries = entries.filter(status=status)

        if query:
            entries = entries.filter(title__name__icontains=query)

        if not has_entries:
            message = "No tienes entradas todavía"

        elif has_entries and not entries.exists():
            message = "No hay resultados para tu búsqueda"

        p = Paginator(entries, 5)
        page_obj = p.get_page(page)

        return render(
            request,
            "library/entry_list.html",
            {"message": message, "page_obj": page_obj, "titles": titles},
        )


@login_required
def entry_detail(request: HttpRequest, entry_id):
    entry = Entry.objects.get(pk=entry_id, user=request.user)
    if not entry:
        return JsonResponse(
            {
                "ok": False,
                "error": "NOT_FOUND",
                "message": "Esta entrada no existe",
            },
            status=404,
        )
    return JsonResponse(
        {
            "id": entry.id,
            "title": entry.title.id,
            "status": entry.status,
            "rating": entry.rating,
            "comment": entry.comment,
        }
    )
