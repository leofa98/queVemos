from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect

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
