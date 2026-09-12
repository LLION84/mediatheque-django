from django.shortcuts import render
from gestion.models import Media, JeuDePlateau


def liste_medias(request):
    medias = Media.objects.all()
    jeux = JeuDePlateau.objects.all()
    return render(request, "consultation/liste_medias.html", {
        "medias": medias,
        "jeux": jeux,
    })