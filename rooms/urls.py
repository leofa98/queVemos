from django.urls import path

from . import views

urlpatterns = [
    path("dashboard", views.dashboard, name="dashboard"),
    path("rooms", views.rooms, name="rooms"),
    path("rooms/new", views.room_new, name="room_new"),
    path("rooms/list", views.room_list, name="room_list"),
    path("rooms/join", views.room_join, name="room_join"),
    path("rooms/<str:invitation_code>", views.room_detail, name="room_detail"),
]
