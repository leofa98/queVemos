from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from catalog.models import Title


class Entry(models.Model):
    class EntryStatus(models.TextChoices):
        SEEN = "seen", "Visto"
        PENDING = "pending", "Pendiente"
        DROPPED = "dropped", "Abandonado"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="entries"
    )
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name="entries")
    status = models.CharField(max_length=10, choices=EntryStatus.choices)
    rating = models.PositiveIntegerField(
        blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "title"], name="unique_entry")
        ]

    def __str__(self):
        return f"{self.user} - {self.title} - {self.get_status_display()}"
