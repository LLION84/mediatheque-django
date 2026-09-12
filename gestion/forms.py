from django import forms
from .models import Membre, Livre, Dvd, Cd, JeuDePlateau, Emprunt, Media


class MembreForm(forms.ModelForm):
    class Meta:
        model = Membre
        fields = ["nom", "prenom", "email"]


class LivreForm(forms.ModelForm):
    class Meta:
        model = Livre
        fields = ["titre", "auteur", "disponible"]


class DvdForm(forms.ModelForm):
    class Meta:
        model = Dvd
        fields = ["titre", "realisateur", "disponible"]


class CdForm(forms.ModelForm):
    class Meta:
        model = Cd
        fields = ["titre", "artiste", "disponible"]


class JeuDePlateauForm(forms.ModelForm):
    class Meta:
        model = JeuDePlateau
        fields = ["titre", "createur"]


class EmpruntForm(forms.ModelForm):
    class Meta:
        model = Emprunt
        fields = ["membre", "media"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["media"].queryset = Media.objects.filter(disponible=True)

    def clean(self):
        donnees = super().clean()
        membre = donnees.get("membre")
        media = donnees.get("media")

        if membre and not membre.peut_emprunter():
            raise forms.ValidationError(
                "Ce membre ne peut pas emprunter : il a déjà 3 emprunts en cours, "
                "ou il a un retard."
            )
        if media and not media.disponible:
            raise forms.ValidationError("Ce média n'est pas disponible.")

        return donnees