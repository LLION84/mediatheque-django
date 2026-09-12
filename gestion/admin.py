from django.contrib import admin
from .models import Media, Livre, Dvd, Cd, JeuDePlateau, Membre, Emprunt

admin.site.register(Media)
admin.site.register(Livre)
admin.site.register(Dvd)
admin.site.register(Cd)
admin.site.register(JeuDePlateau)
admin.site.register(Membre)
admin.site.register(Emprunt)