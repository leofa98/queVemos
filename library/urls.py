from django.urls import path

from . import views

urlpatterns = [path("/library/new", views.entry_new, name="entry_new")]
