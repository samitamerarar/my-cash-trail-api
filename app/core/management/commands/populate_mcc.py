"""
Django command to populate Merchant Category Codes from the mcc.csv to the database
"""
import csv
import os
from django.core.management.base import BaseCommand
from core.models import MerchantCategoryCode


class Command(BaseCommand):
    help = 'Populate database with CSV data'

    def handle(self, *args, **options):
        """Entrypoint for command."""
        if MerchantCategoryCode.objects.exists():
            self.stdout.write(self.style.WARNING('Database already populated. Skipping...'))

        csv_path = os.path.join(os.getcwd(), 'core/assets/mcc.csv')
        with open(csv_path) as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # skip header row if exists

            for row in csv_reader:
                field_mcc = row[0]
                field_edited_description = row[1]
                field_combined_description = row[2]
                field_usda_description = row[3]
                field_irs_description = row[4]

                MerchantCategoryCode.objects.create(
                    mcc=field_mcc, edited_description=field_edited_description,
                    combined_description=field_combined_description, usda_description=field_usda_description,
                    irs_description=field_irs_description)

        self.stdout.write(self.style.SUCCESS('Database populated successfully.'))
