import os
import csv
import datetime

from django.core.management.base import BaseCommand

folder_path = r"C:\Users\gregoryjones\OneDrive - Preferred Technologies, LLC\Desktop\Pasadena ISD"

# Get today's date in D_M_YYYY format
today = datetime.datetime.today()
today_date = f"{today.month}_{today.day}_{today.year}"

# Create a set to store entities with "Warning" health status
entities_with_warning = set()
entities_with_online = set()


class Command(BaseCommand):

    def handle(self, *args, **options):

        # Loop through all files in the folder
        for filename in os.listdir(folder_path):
            if today_date in filename and filename.endswith('.csv'):  # Check if today's date is in the filename and it's a CSV file
                file_path = os.path.join(folder_path, filename)
                
                try:
                    # Open the CSV file using 'utf-8-sig' to handle BOM characters
                    with open(file_path, mode='r', newline='', encoding='utf-8-sig') as csvfile:
                        reader = csv.DictReader(csvfile)  # Use DictReader to easily access columns by name
                        
                        for row in reader:
                            entity = row['Entity']
                            health = row['Health']

                            # If Health is "Warning", add to entities_with_warning
                            if health == 'Warning':
                                entities_with_warning.add(entity)
                            
                            # If Health is "Online", add to entities_with_online
                            if health == 'Online':
                                entities_with_online.add(entity)
                
                except Exception as e:
                    print(f"Error reading file {filename}: {e}")

        # Remove any entities that are also marked as "Online"
        final_entities = entities_with_warning - entities_with_online

        # If there are entities left, write them to a new CSV file
        if final_entities:
            output_file = os.path.join(folder_path, f"Entities_with_Warning_{today_date}.csv")
            
            # Write the list of entities to a new CSV file
            with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Entity'])  # Write header
                for entity in final_entities:
                    writer.writerow([entity])  # Write each entity as a new row
            
            print(f"Entities with 'Warning' health status saved to: {output_file}")
        else:
            print("No entities with 'Warning' health status found.")
            
                    

                

