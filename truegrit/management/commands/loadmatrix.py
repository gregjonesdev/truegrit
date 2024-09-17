import json
from openpyxl import load_workbook

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

class Command(BaseCommand):  

    def handle(self, *args, **options):

        file_path = input("Enter file path of matrix: ")
        print(file_path)
        workbook = load_workbook(filename=file_path)
        for sheet_name in workbook.sheetnames:
            # Select the sheet
            sheet = workbook[sheet_name]
            
            # Access and print row 3
            print(f"Sheet: {sheet_name}, Row 3:")
            row_3 = sheet[3]  # OpenPyXL uses 1-based indexing for rows
            for cell in row_3:
                print(cell.value, end='\t')
            print()  