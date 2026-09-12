from datetime import date, timedelta
from django.test import TestCase
from .models import Livre, Membre, Emprunt
from django.urls import reverse

class ModeleTest(TestCase):
    """Vérifie les modèles et l'héritage."""

    def setUp(self):
        self.livre = Livre.objects.create(titre="Germinal", auteur="Zola")
        self.membre = Membre.objects.create(
            nom="Blaise", prenom="Zinou", email="zinou@mail.fr"
        )

    def test_livre_herite_des_champs_de_media(self):
        self.assertEqual(self.livre.titre, "Germinal")
        self.assertTrue(self.livre.disponible)

    def test_affichage_livre(self):
        self.assertEqual(str(self.livre), "Germinal")

    def test_affichage_membre(self):
        self.assertEqual(str(self.membre), "Zinou Blaise")


class ReglesMetierTest(TestCase):
    """Vérifie les 3 règles métier de l'énoncé."""

    def setUp(self):
        self.membre = Membre.objects.create(
            nom="Dupont", prenom="Marie", email="marie@mail.fr"
        )
        self.livres = [
            Livre.objects.create(titre=f"Livre {i}", auteur="Auteur")
            for i in range(4)
        ]

    def test_un_emprunt_dure_une_semaine(self):
        emprunt = Emprunt.objects.create(membre=self.membre, media=self.livres[0])
        self.assertEqual(emprunt.date_limite(), date.today() + timedelta(days=7))

    def test_pas_plus_de_trois_emprunts(self):
        for livre in self.livres[:3]:
            Emprunt.objects.create(membre=self.membre, media=livre)
        self.assertFalse(self.membre.peut_emprunter())

    def test_membre_en_retard_est_bloque(self):
        emprunt = Emprunt.objects.create(membre=self.membre, media=self.livres[0])
        Emprunt.objects.filter(pk=emprunt.pk).update(
            date_emprunt=date.today() - timedelta(days=10)
        )
        emprunt.refresh_from_db()
        self.assertTrue(emprunt.est_en_retard())
        self.assertFalse(self.membre.peut_emprunter())

class VueTest(TestCase):
    """Un test par fonctionnalité de l'application bibliothécaire."""

    def setUp(self):
        self.membre = Membre.objects.create(
            nom="Dupont", prenom="Marie", email="marie@mail.fr"
        )
        self.livre = Livre.objects.create(titre="Dune", auteur="Herbert")

    def test_afficher_liste_membres(self):
        reponse = self.client.get(reverse("liste_membres"))
        self.assertEqual(reponse.status_code, 200)
        self.assertContains(reponse, "Dupont")

    def test_creer_membre(self):
        self.client.post(reverse("creer_membre"), {
            "nom": "Martin", "prenom": "Paul", "email": "paul@mail.fr",
        })
        self.assertTrue(Membre.objects.filter(nom="Martin").exists())

    def test_modifier_membre(self):
        self.client.post(reverse("modifier_membre", args=[self.membre.id]), {
            "nom": "Dupont", "prenom": "Marion", "email": "marie@mail.fr",
        })
        self.membre.refresh_from_db()
        self.assertEqual(self.membre.prenom, "Marion")

    def test_supprimer_membre(self):
        self.client.post(reverse("supprimer_membre", args=[self.membre.id]))
        self.assertFalse(Membre.objects.filter(id=self.membre.id).exists())

    def test_afficher_liste_medias(self):
        reponse = self.client.get(reverse("liste_medias_gestion"))
        self.assertEqual(reponse.status_code, 200)
        self.assertContains(reponse, "Dune")

    def test_ajouter_media(self):
        self.client.post(reverse("ajouter_media", args=["livre"]), {
            "titre": "1984", "auteur": "Orwell", "disponible": True,
        })
        self.assertTrue(Livre.objects.filter(titre="1984").exists())

    def test_creer_emprunt(self):
        self.client.post(reverse("creer_emprunt"), {
            "membre": self.membre.id,
            "media": self.livre.id,
        })
        self.assertEqual(Emprunt.objects.count(), 1)
        self.livre.refresh_from_db()
        self.assertFalse(self.livre.disponible)

    def test_rentrer_emprunt(self):
        emprunt = Emprunt.objects.create(membre=self.membre, media=self.livre)
        self.client.post(reverse("rentrer_emprunt", args=[emprunt.id]))
        emprunt.refresh_from_db()
        self.assertIsNotNone(emprunt.date_retour)

    def test_catalogue_public(self):
        reponse = self.client.get(reverse("liste_medias"))
        self.assertEqual(reponse.status_code, 200)
        self.assertContains(reponse, "Dune")