import csv
import time
from datetime import datetime
from pymongo import MongoClient

# Edit Notes: could integrate a pool of threads to speed up the upload process, other than that, this would work as a fairly robust db script.

# This is what was provided by MongoDB when I created the cluster, along with the as a test user for the DB.
client = MongoClient("mongodb+srv://test100:password123Nope@networkdb.hmz0oiw.mongodb.net/")
db = client["NetworkDB"]


# This is a function that I created to ensure that my schema is correct, and if needed, that a new collection / relationship is created within MongoDB.
# I would need to augment the upload script to so that the data can be uploaded within the csv file... 
def collection_checker():
    collections = db.list_collection_names()
    required_collections = ["sites", "device_types", "devices"]
    
    for collection in required_collections:
        if collection not in collections:
            print(f"Creating collection: {collection}")
            db.create_collection(collection)

    print()
    print("The Collections are now live, any additional requirement updates were made.")
    print()

# This searches for the site_name within the csv file, 4th column, and returns the site names, stored within a set.
# I added a set which ensures that there are no duplicates, which fixes concerns with the database being corrupted by duplicate entries, as this was one of the concerns I initially had.
def sites(csv_file):

    sites_set = set()

    with open(csv_file, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            sites_set.add(row["site_name"])

    return sites_set

# Searches for device models that are found within the csv file, which is the 5th column with how I've arranged that file, stored within a set by the way.
# It just iterates through the csv file row by row, so it terms of batch filing, there isn't an allocation solution for that yet...
def device_model_names(csv_file):

    models = set()

    with open(csv_file, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            models.add(row["device_model"])

    return models

# If a site hasn't been added to the collection, this function will first search by the site_name and if it exists, it won't create a new site location, however, if not, it will add one 
# and ensure that no duplicates are made that would otherwise corrupt the database.
def populate_sites(site_names):
    existing_sites = {site["site_name"] for site in db.sites.find({}, {"site_name": 1, "_id": 0})}
    
    count = 0

    for site_name in site_names:
        if site_name not in existing_sites:
            site_doc = {
                "site_name": site_name,
                "created_at": datetime.now()
            }
            db.sites.insert_one(site_doc)
            count += 1
    
    print()
    print(f"Added {count} new sites to the database.")
    print()

# Makes the Device_types by using this as a check against any previous uploads, or duplicates... This was a previous issue that I had, but it could've also been that I wasn't using a set. 
def device_types(models):
    existing_models = {dtype["model"] for dtype in db.device_types.find({}, {"model": 1, "_id": 0})}
    
    count = 0

    for model in models:

        if model not in existing_models:
            device_type_doc = {
                "model": model,
                "created_at": datetime.now(),
                "vendor": vendor_model(model)
            }
            db.device_types.insert_one(device_type_doc)


            count += 1
    
    print()
    print(f"Added {count} new device types to the database.")
    print()


# This is a useful function that I made to assist with identifying unique vendor models, as a way to aggregate the models by the vendor name, as sometimes Cisco, PA, and even Dell, HP and others (though not included here will have similar names for their models.)
# This seeks to remediate that issue though, I would need to update this function in the future though with repeat vendor names, as again HP and Dell are not included here.
def vendor_model(model):

    if model.startswith("MX") or model.startswith("SRX"):
        return "Juniper"
    elif model.startswith("ASR") or model.startswith("ISR") or model.startswith("WS-C"):
        return "Cisco"
    
    # Could add more items to my csv file, as Avaya, Dell, HP, and many others are not included within my list.
    
    else:
        return "Unknown"
    

# Gets the site_id from site_name, it still checks if the sites was within the csv, before adding to the MongoDB.
def site_id(site_name):

    site = db.sites.find_one({"site_name": site_name})

    if site:
        return site["_id"]
    

    else:

        print()
        print(f"WARNING!!!: Site '{site_name}' not found in database!")
        print()
        print("The Site Name will be added, MONGODB update required...")
        print()
        print()

        return None
    


# Get device_type_id from the model, as extracted from my csv file. If it is not found, or not within the database, 
# it would have already have been added, this is just an additional check...
def device_type_id(model):
    dtype = db.device_types.find_one({"model": model})
    if dtype:
        return dtype["_id"]
    

    else:

        print()
        print(f"WARNING!!!: Device model '{model}' not found in database!")
        print()
        print("The Device Model will be added, MONGODB update required...")
        print()
        print()

        return None
    


def upload_devices(csv_file):

    print()
    print("Checking and creating required collections...")
    print()
    collection_checker()
    
    print("Collecting sites and device models from the device CSV...")
    site_names = sites(csv_file)  
    models = device_model_names(csv_file)
    
    print("Creating collections...")
    populate_sites(site_names)
    device_types(models)
    
    print("Starting device upload...")
    total_count = 0
    success_count = 0
    duplicate_count = 0

    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            total_count += 1
            
            if db.devices.find_one({"serial_number": row["serial_number"]}):
                print()
                print(f"Duplicate found: {row['serial_number']} - Skipping")
                print()


                duplicate_count += 1

                continue
              
            sid = site_id(row["site_name"])
            deviceid = device_type_id(row["device_model"])
            
            if not sid or not deviceid:

                print()    
                print(f"Missing reference for row: {row['hostname']} - Skipping")
                print()

                continue

            device = {
                "hostname": row["hostname"],
                "ip_address": row["ip_address"],
                "serial_number": row["serial_number"],
                "site_id": sid,
                "device_type_id": deviceid,
                "status": "active",
                "installed_date": datetime.strptime(row["installed_date"], "%Y-%m-%d"),
                "last_updated": datetime.now()
            }
            
            result = db.devices.insert_one(device)
            print(f"Inserted: {row['hostname']} ({row['serial_number']})")
            success_count += 1
    
    print()
    print()
    print("\nSummary of Network Vitals")
    print("===================================")
    print()
    print(f"Total records processed: {total_count}")
    print()
    print()
    print(f"Successfully inserted items: {success_count}")
    print()
    print(f"Duplicates found: {duplicate_count}")
    print()
    print()
    print(f"Failed entries for the network: {total_count - success_count - duplicate_count}")
    print()
    print()
    print("===================================")
    print()
    print()
    print()


# Its always been taught as good practice to have a main function, which is why I have it here, and if I want to change anything in the future that is now way easier to maintain.

if __name__ == "__main__":
    start_of_upload = time.time()
    
    csv_filename = "devices.csv"
    upload_devices(csv_filename)
    
    end_of_upload = time.time()

    print()
    print("Cloud Network Inventory Database:")
    print("===================================")
    print()
    print()
    print(f"\nUpload completed in {end_of_upload - start_of_upload:.2f} seconds.")
    print()
    print()
    print("The upload to the DB was indeed successful, and no further issues were found.")
    print()


