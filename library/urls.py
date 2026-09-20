from django.urls import path

from . import views

urlpatterns = [
    path("library/new", views.entry_new, name="entry_new"),
    path("library/<int:entry_id>/remove", views.remove_entry, name="remove_entry"),
]
