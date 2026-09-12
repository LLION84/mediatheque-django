from django.urls import path
from . import views

urlpatterns = [
    path("", views.liste_medias, name="liste_medias"),
]