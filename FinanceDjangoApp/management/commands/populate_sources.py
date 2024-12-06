from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Populate Source table with predefined values"

    def handle(self, *args, **options):
        sources = [
            ("S1", "Capital Gains"),
            ("S2", "Dividend Income"),
            ("S3", "Earned Income"),
            ("S4", "Interest Income"),
            ("S5", "Others"),
            ("S6", "Profit Income"),
            ("S7", "Rental Income"),
            ("S8", "Royalty Income"),
        ]

        with connection.cursor() as cursor:
            for source_id, source_name in sources:
                cursor.execute("""
                    INSERT IGNORE INTO Source (sourceID, sourceName, description)
                    VALUES (%s, %s, %s)
                """, [source_id, source_name, None])

        self.stdout.write("Source table populated successfully.")
