from django.urls import path

from . import views

urlpatterns = [
    path("library/new", views.entry_new, name="entry_new"),
    path("library/<int:entry_id>/remove", views.remove_entry, name="remove_entry"),
    path("library/entries", views.entry_list, name="entry_list"),
    path("library/entry/<int:entry_id>", views.entry_detail, name="entry_detail"),
    path("library/<int:entry_id>/edit", views.entry_edit, name="entry_edit"),
]
