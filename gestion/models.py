from django.db import models
from datetime import date, timedelta

class Media(models.Model):
    titre = models.CharField(max_length=200)
    disponible = models.BooleanField(default=True)


    def __str__(self):
        return self.titre

class Livre(Media):
    auteur = models.CharField(max_length=200)

class Dvd(Media):
    realisateur = models.CharField(max_length=200)

class Cd(Media):
    artiste = models.CharField(max_length=200)


class JeuDePlateau(models.Model):
    titre = models.CharField(max_length=200)
    createur = models.CharField(max_length=200)

    def __str__(self):
        return self.titre


class Membre(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    NB_EMPRUNTS_MAX = 3

    def emprunts_en_cours(self):
        return self.emprunt_set.filter(date_retour__isnull=True)

    def a_du_retard(self):
        for emprunt in self.emprunts_en_cours():
            if emprunt.est_en_retard():
                return True
        return False

    def peut_emprunter(self):
        if self.a_du_retard():
            return False
        return self.emprunts_en_cours().count() < self.NB_EMPRUNTS_MAX

class Emprunt(models.Model):
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    date_emprunt = models.DateField(auto_now_add=True)
    date_retour = models.DateField(null=True, blank=True)
    DUREE_EMPRUNT_JOURS = 7

    def __str__(self):
        return f"{self.media} emprunté par {self.membre}"

    def date_limite(self):
        return self.date_emprunt + timedelta(days=self.DUREE_EMPRUNT_JOURS)

    def est_en_retard(self):
        if self.date_retour is not None:
            return False
        return date.today() > self.date_limite()



