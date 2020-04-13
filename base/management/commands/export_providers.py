from django.core.management.base import BaseCommand

from base.exports import *

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filename')

    def handle(self, *args, **options):
        generate_export_providers(options['filename'])
