import py_cui
from django.contrib.admin import site
from django.core.management.base import BaseCommand

MODEL_ADMINS = site._registry

class Command(BaseCommand):
    def handle(self, *args, **options):
        root = py_cui.PyCUI(1,1)
        root.add_label('Hello World!', 0, 0)
        root.start()