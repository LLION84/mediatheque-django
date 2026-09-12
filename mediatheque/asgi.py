"""Point d'entree ASGI (mise en ligne en mode asynchrone)."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mediatheque.settings")

application = get_asgi_application()
