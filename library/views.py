from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render

from catalog.models import Title
from library.models import Entry


@login_required
def entry_new(request: HttpRequest):

    if request.user.is_authenticated and request.method == "POST":
        title_id = request.POST.get("title", "")
        status = request.POST.get("status", "")
        rating = request.POST.get("rating", "")
        comment = request.POST.get("comment", "")

        try:
            title = Title.objects.get(pk=title_id)
            Entry.objects.create(
                user=request.user,
                title=title,
                status=status,
                rating=rating,
                comment=comment,
            )
            # return render(
            #     request,
            #     "rooms/dashboard.html",
            #     {"message": "Entrada creada"},
            # )
            return redirect("dashboard")
        except (IntegrityError, Title.DoesNotExist):
            return redirect("dashboard")


@login_required
def remove_entry(request: HttpRequest, entry_id):
    if request.method == "POST":
        entry = Entry.objects.filter(pk=entry_id, user=request.user).first()
        if not entry:
            return JsonResponse({"ok": False}, status=404)
        entry.delete()
        return JsonResponse({"ok": True})


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
            "rooms/entry_list.html",
            {"message": message, "page_obj": page_obj, "titles": titles},
        )
