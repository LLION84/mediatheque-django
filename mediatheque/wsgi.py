"""Point d'entree WSGI (mise en ligne sur un serveur classique)."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mediatheque.settings")

application = get_wsgi_application()
