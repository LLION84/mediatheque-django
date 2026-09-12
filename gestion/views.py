from datetime import date
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from .models import Membre, Media, JeuDePlateau, Emprunt
from .forms import MembreForm, LivreForm, DvdForm, CdForm, JeuDePlateauForm, EmpruntForm
import logging

logger = logging.getLogger("gestion")

FORMULAIRES_MEDIA = {
    "livre": LivreForm,
    "dvd": DvdForm,
    "cd": CdForm,
    "jeu": JeuDePlateauForm,
}

def liste_membres(request):
    membres = Membre.objects.all()
    return render(request, "gestion/liste_membres.html", {"membres": membres})


def creer_membre(request):
    if request.method == "POST":
        form = MembreForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info("Nouveau membre créé : %s", form.instance)
            return redirect("liste_membres")
    else:
        form = MembreForm()
    return render(request, "gestion/formulaire_membre.html", {"form": form})

def modifier_membre(request, membre_id):
    membre = get_object_or_404(Membre, pk=membre_id)
    if request.method == "POST":
        form = MembreForm(request.POST, instance=membre)
        if form.is_valid():
            form.save()
            return redirect("liste_membres")
    else:
        form = MembreForm(instance=membre)
    return render(request, "gestion/formulaire_membre.html", {"form": form})


def supprimer_membre(request, membre_id):
    membre = get_object_or_404(Membre, pk=membre_id)
    if request.method == "POST":
        membre.delete()
        return redirect("liste_membres")
    return render(request, "gestion/confirmer_suppression.html", {"membre": membre})

def liste_medias_gestion(request):
    medias = Media.objects.all()
    jeux = JeuDePlateau.objects.all()
    return render(request, "gestion/liste_medias.html", {
        "medias": medias,
        "jeux": jeux,
    })

def ajouter_media(request, type_media):
    classe_form = FORMULAIRES_MEDIA.get(type_media)
    if classe_form is None:
        raise Http404("Type de média inconnu")

    if request.method == "POST":
        form = classe_form(request.POST)
        if form.is_valid():
            form.save()
            return redirect("liste_medias_gestion")
    else:
        form = classe_form()

    return render(request, "gestion/formulaire_media.html", {
        "form": form,
        "type_media": type_media,
    })

def liste_emprunts(request):
    emprunts = Emprunt.objects.filter(date_retour__isnull=True)
    return render(request, "gestion/liste_emprunts.html", {"emprunts": emprunts})


def creer_emprunt(request):
    if request.method == "POST":
        form = EmpruntForm(request.POST)
        if form.is_valid():
            emprunt = form.save()
            logger.info("Emprunt créé : %s", emprunt)
            emprunt.media.disponible = False
            emprunt.media.save()
            return redirect("liste_emprunts")
    else:
        form = EmpruntForm()
    return render(request, "gestion/formulaire_emprunt.html", {"form": form})


def rentrer_emprunt(request, emprunt_id):
    emprunt = get_object_or_404(Emprunt, pk=emprunt_id)
    if request.method == "POST":
        emprunt.date_retour = date.today()
        emprunt.save()
        emprunt.media.disponible = True
        emprunt.media.save()
        logger.info("Retour enregistré : %s", emprunt)
        return redirect("liste_emprunts")
    return render(request, "gestion/confirmer_retour.html", {"emprunt": emprunt})