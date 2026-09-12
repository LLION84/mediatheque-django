#!/usr/bin/env python
"""Utilitaire en ligne de commande de Django pour les tâches administratives."""
import os
import sys


def main():
    """Point d'entrée : lance les commandes Django (runserver, migrate, test...)."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mediatheque.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossible d'importer Django. Vérifiez qu'il est installé et que "
            "l'environnement virtuel est bien activé."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
