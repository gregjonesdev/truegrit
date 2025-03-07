
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
                Console.WriteLine("Connecting to Genetec Config Tool...");
                ConfigurationToolClient client = new ConfigurationToolClient();
                client.Connect();

                // Get the area specified
                Area area = client.GetArea("MRE Access Control");

                if (area == null)
                {
                    Console.WriteLine("Area not found.");
                    return;
                }

                // Retrieve the list of doors from the specified area
                Console.WriteLine($"Listing doors from area: {area.Name}");
                foreach (Door door in area.Doors)
                {
                    Console.WriteLine($"Door ID: {door.Id}, Door Name: {door.Name}");
                }

                // Disconnect from Config Tool
                client.Disconnect();
            }
            catch (Exception ex)
            {
                Console.WriteLine("An error occurred: " + ex.Message);
            }
        }
    }
