from django.urls import path
from . import views

urlpatterns = [
    path("membres/", views.liste_membres, name="liste_membres"),
    path("membres/nouveau/", views.creer_membre, name="creer_membre"),
    path("membres/<int:membre_id>/modifier/", views.modifier_membre, name="modifier_membre"),
    path("membres/<int:membre_id>/supprimer/", views.supprimer_membre, name="supprimer_membre"),
    path("medias/", views.liste_medias_gestion, name="liste_medias_gestion"),
    path("medias/ajouter/<str:type_media>/", views.ajouter_media, name="ajouter_media"),
    path("emprunts/", views.liste_emprunts, name="liste_emprunts"),
    path("emprunts/nouveau/", views.creer_emprunt, name="creer_emprunt"),
    path("emprunts/<int:emprunt_id>/rentrer/", views.rentrer_emprunt, name="rentrer_emprunt"),

]