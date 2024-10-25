import os
import csv
import platform
from openpyxl import load_workbook

from django.core.management.base import BaseCommand

from truegrit.models import BusinessUnit, Camera


# Define file paths
csv_file_path = r"C:\Users\gregoryjones\OneDrive - Preferred Technologies, LLC\Documents\My Data Sources\Devices.csv"
excel_file_path = r"C:\Users\gregoryjones\OneDrive - Preferred Technologies, LLC\Book3.xlsx"

# List to store tuples
class Command(BaseCommand):  

    def clear_screen(self):
        # move this to common file
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    def get_network_from_bu(self, bu_identifier):
        return Network.objects.get(business_unit__identifier=bu_identifier)

    def update_camera(self, ip_address):
        # Open the CSV file and process each row

        # ask if DHCP 

        #otherwise process static


    def handle(self, *args, **options):
        self.clear_screen() 
        bu_identifier = input("Enter business unit ID: \n")             
        network = self.get_network_from_bu(bu_identifier)
        # Load the workbook and select the specific sheet
        wb = load_workbook(excel_file_path)
        sheet = wb[bu_identifier]

        
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            
            for row in csv_reader:
                # Extract substring from row[2] before the ":"
                search_value = row[2].split(":")[0]
                
                # Iterate through rows in Excel sheet to find the match in column F (6th column, 1-indexed)
                for excel_row in sheet.iter_rows(min_row=2, max_col=11, values_only=False):  # Adjust min_row if there's a header
                    cell_f = excel_row[5]  # Column F is the 6th column in zero-based index

                    if cell_f.value == search_value:  # Check if the value in F matches the extracted value
                        # Assign values to columns K and J (10th and 9th columns)
                        excel_row[10].value = row[0]  # Column K
                        excel_row[8].value = row[4]   # Column I
                        break  # Exit after finding the match

        # Save the modified workbook
        wb.save(excel_file_path)
        print("Excel file updated successfully.")