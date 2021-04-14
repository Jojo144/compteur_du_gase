from django.core.management.base import BaseCommand
from django_q.models import Schedule


class Command(BaseCommand):
    def handle(self, *args, **options):
        defaults = {
            'name': 'Gestion des permanences',
            'func': 'base.tasks.check_activities',
            'cron': '0 2 * * *',
            'schedule_type': 'C',
            'repeats': '-1'
        }
        Schedule.objects.update_or_create(name='Gestion des permanences', defaults=defaults)
