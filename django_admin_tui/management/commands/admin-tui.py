from django.contrib.admin import site
from django.core.management.base import BaseCommand
from rich.layout import layout

MODEL_ADMINS = site._registry

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass