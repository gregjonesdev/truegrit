import json
from openpyxl import load_workbook

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from truegrit.models import (
    Project,
    ProjectStatus,
)

class Command(BaseCommand):  

    def create_project(self, number, description):
        current = ProjectStatus.objects.get(name='current')
        try:
            return Project.objects.get(number=number)
        except ObjectDoesNotExist:
            new_project = Project(
                number=number,
                description=description,
                status=current
            )    
            new_project.set_fields_to_base()
            new_project.save()
            return new_project


    def handle(self, *args, **options):

        # file_path = input("Enter file path of matrix: ")
        file_path = "/Users/gregjones/Downloads/heb-matrix.xlsx"
        print(file_path)
        workbook = load_workbook(filename=file_path)
        project = self.create_project(106191, "HEB 2024 Camera Refresh")
        for sheet_name in workbook.sheetnames:
            # Select the sheet
            sheet = workbook[sheet_name]
            for row in sheet.iter_rows(min_row=4, values_only=True):
                # Print data from each column in the current row
                # for cell_value in row:
                #     print(cell_value, end='\t')  # Print cell value with a tab separator
                if row[0]:
                    print(row[0].split(" - ")[0])
                    print(row[0].split(" - ")[1])

                    print(row[1])
                    print(row[2])
                    print(row[3])
                    print(row[4])
                    print(row[5])
                    print()  # Newline after each row
            raise SystemExit(0) # test first sheet