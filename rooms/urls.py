from django.urls import path

from . import views

urlpatterns = [
    path("dashboard", views.dashboard, name="dashboard"),
    path("rooms", views.rooms, name="rooms"),
    path("rooms/new", views.room_new, name="room_new"),
    path("rooms/list", views.room_list, name="room_list"),
    path("rooms/join", views.room_join, name="room_join"),
    path("rooms/exit", views.room_exit, name="room_exit"),
    path("rooms/<str:invitation_code>", views.room_detail, name="room_detail"),
    path(
        "rooms/<str:invitation_code>/candidates/new",
        views.propose_title,
        name="propose_title",
    ),
    path(
        "rooms/<str:invitation_code>/candidates",
        views.candidate_list,
        name="candidate_list",
    ),
    path(
        "rooms/<str:invitation_code>/candidates/<int:candidate_id>/vote",
        views.vote,
        name="vote",
    ),
]
