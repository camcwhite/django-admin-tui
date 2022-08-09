import py_cui
from django.contrib.admin import site
from django.core.management.base import BaseCommand

from django_admin_tui.tui import tui

MODEL_ADMINS = site._registry

class Command(BaseCommand):
    def handle(self, *args, **options):
        tui.initialize()
        tui.start()