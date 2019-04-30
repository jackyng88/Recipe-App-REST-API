# time is default python module to make our DB sleep.
import time

# connections module to test if DB connection is available.
from django.db import connections
from django.db.utils import OperationalError
# BaseCommand class is what we need to build on to create our custom command.
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    # Django command to pause execution until Database is available.

    # Handle function that is run whenever we run this management command.
    # *args and **options allow us to pass custom options (like waittimes)
    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        # while db is none, try and set connection. If unavailable
        # throw OperationalError, catch, write, then sleep.
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        # database is finally available. The success function outputs in green.
        self.stdout.write(self.style.SUCCESS('Database available!'))
