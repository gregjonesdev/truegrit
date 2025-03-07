def generate_csharp_macro(area_name):
    # C# code template as an escaped string
    csharp_code = """
    using System;
    using Genetec.Sdk;
    using Genetec.ConfigTool;
    using Genetec.AccessControl;

    class Program
    {
        static void Main(string[] args)
        {
            try
            {
                // Connect to Genetec Config Tool
                Console.WriteLine(\"Connecting to Genetec Config Tool...\");
                ConfigurationToolClient client = new ConfigurationToolClient();
                client.Connect();

                // Get the area specified
                Area area = client.GetArea(\"{area_name}\");

                if (area == null)
                {
                    Console.WriteLine(\"Area not found.\");
                    return;
                }

                // Retrieve the list of doors from the specified area
                Console.WriteLine($\"Listing doors from area: {area.Name}\");
                foreach (Door door in area.Doors)
                {
                    Console.WriteLine($\"Door ID: {door.Id}, Door Name: {door.Name}\");
                }

                // Disconnect from Config Tool
                client.Disconnect();
            }
            catch (Exception ex)
            {
                Console.WriteLine(\"An error occurred: \" + ex.Message);
            }
        }
    }
""".replace("{area_name}", area_name)  # Replaces the placeholder with the actual area name
    return csharp_code

def write_to_file(filename, content):
    # Open the file in write mode and write the content
    with open(filename, 'w') as file:
        file.write(content)
    print(f"C# code has been written to {filename}")
        

def get_door_names():
    # The area name you want to retrieve doors from
    area_name = "MRE Access Control"

    # Generate the C# code for the macro
    csharp_macro = generate_csharp_macro(area_name)

    # Define the filename to save the C# code
    filename = "GenetecDoorList.cs"

    # Write the generated C# code to a file
    write_to_file(filename, csharp_macro)