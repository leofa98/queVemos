from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import redirect, render

from catalog.models import Title
from library.models import Entry


def dashboard(request: HttpRequest):
    if not request.user.is_authenticated:
        return redirect("index")

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
        "rooms/dashboard.html",
        {"message": message, "page_obj": page_obj, "titles": titles},
    )
