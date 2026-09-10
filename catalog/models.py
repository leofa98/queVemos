from django.db import models


class Genre(models.Model):
    name = models.CharField(unique=True, max_length=100)
    tmdb_id = models.PositiveIntegerField(unique=True, blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Title(models.Model):
    class MediaType(models.TextChoices):
        MOVIE = "movie", "Película"
        TV = "tv", "Serie"

    name = models.CharField(db_index=True, max_length=200)
    media_type = models.CharField(choices=MediaType.choices, max_length=10)
    year = models.PositiveIntegerField(blank=True, null=True)
    synopsis = models.TextField(blank=True)
    image = models.URLField(blank=True)
    genres = models.ManyToManyField(Genre, blank=True, related_name="titles")
    tmdb_id = models.PositiveIntegerField(unique=True, blank=True, null=True)
    last_sync = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.year})" if self.year else self.name
