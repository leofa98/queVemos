from django.urls import path

from . import views

urlpatterns = [
    path("dashboard", views.dashboard, name="dashboard"),
    path("rooms", views.rooms, name="rooms"),
    path("rooms/new", views.room_new, name="room_new"),
    path("rooms", views.room_list, name="room_list"),
]
