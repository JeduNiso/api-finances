from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Drop all tables in the database and recreate them via migrations'

    def handle(self, *args, **options):
        self.stdout.write('Dropping all tables...')
        with connection.cursor() as cursor:
            cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
            cursor.execute('SHOW TABLES')
            tables = [row[0] for row in cursor.fetchall()]
            for table in tables:
                cursor.execute(f'DROP TABLE IF EXISTS `{table}`')
                self.stdout.write(f'  Dropped: {table}')
            cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
        self.stdout.write(self.style.SUCCESS(f'Dropped {len(tables)} tables. Ready for fresh migrations.'))
