from django.conf import settings
from django.db import models


class Room(models.Model):
    class RoomStatus(models.TextChoices):
        OPEN = "open", "Abierta"
        CLOSED = "closed", "Cerrada"

    name = models.CharField(max_length=64)
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hosted_rooms"
    )
    status = models.CharField(choices=RoomStatus.choices, max_length=10)
    invitation_code = models.CharField(max_length=6)
    allow_seen = models.BooleanField(default=False)
    winner = models.ForeignKey(
        "Candidate",
        on_delete=models.SET_NULL,
        related_name="room",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank="True")


class Candidate(models.Model):
    class CandidateOrigin(models.TextChoices):
        SUGGESTED = "suggested", "Sugerido"
        MANUAL = "manual", "Manual"

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="candidates")
    proposed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="candidates"
    )
    origin = models.CharField(choices=CandidateOrigin.choices, max_length=10)
    score = models.PositiveIntegerField(blank=True, null=True)
    reason = models.CharField(max_length=100, blank=True)


class Vote(models.Model):
    class VotePosition(models.TextChoices):
        UP = "up", "Sí"
        DOWN = "down", "No"

    candidate = models.ForeignKey(
        Candidate, on_delete=models.CASCADE, related_name="votes"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="votes"
    )
    position = models.CharField(choices=VotePosition.choices, max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)


class Membership(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships"
    )
    created_at = models.DateTimeField(auto_now_add=True)
