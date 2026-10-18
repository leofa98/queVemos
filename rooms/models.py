from django.conf import settings
from django.db import models

from catalog.models import Title


class Room(models.Model):
    class RoomStatus(models.TextChoices):
        OPEN = "open", "Abierta"
        CLOSED = "closed", "Cerrada"

    name = models.CharField(max_length=64)
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hosted_rooms"
    )
    status = models.CharField(
        choices=RoomStatus.choices, max_length=10, default=RoomStatus.OPEN
    )
    invitation_code = models.CharField(max_length=6, unique=True)
    allow_seen = models.BooleanField(default=False)
    winner = models.ForeignKey(
        "Candidate",
        on_delete=models.SET_NULL,
        related_name="candidate_room",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.invitation_code}"


class Candidate(models.Model):
    class CandidateOrigin(models.TextChoices):
        SUGGESTED = "suggested", "Sugerido"
        MANUAL = "manual", "Manual"

    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name="candidates"
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="candidates")
    proposed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="candidates",
        blank=True,
        null=True,
    )
    origin = models.CharField(choices=CandidateOrigin.choices, max_length=10)
    score = models.PositiveIntegerField(blank=True, null=True)
    reason = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-score"]
        constraints = [
            models.UniqueConstraint(fields=["room", "title"], name="unique_candidate")
        ]

    def __str__(self):
        return f"{self.title} - {self.room}"


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

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["candidate", "user"], name="unique_vote")
        ]

    def __str__(self):
        return f"{self.candidate} - {self.user} - {self.get_position_display()}"


class Membership(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(fields=["room", "user"], name="unique_membership")
        ]

    def __str__(self):
        return f"{self.user} - {self.room} - {self.user}"
