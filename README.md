# Overview

The program that I created is a Network Inventory Script (created using Python) that was made with the intent to manage a Network of devices, complete with their vitals including but not limited to information like the following: (IP Address, Hostname, device Type,Make, Model, Status of their condition, site name and location, date installed, etc). I've created this script so that it can be uploaded to a cloud database, that one that I chose to use for this project was MongoDB Atlas, as it was highly recommended to me as the 'free-tier' has plenty of functional features as my research indicated, decent headroom for growth due to data constraints, and overall I just wanted to learn more about this database platform. 

This information for the Network Inventory is initially stored within a csv file, where it is divided and organized by these columns: hostname,ip_address,serial_number,site_name,device_model,installed_date. The data for the 'devices.csv' was queried as a random sample of devices and site names by a LLM that I used to generate the data as again this is a rendition of what a network inventory would look like in a production environment. 

The script that I created in Python uses my 'devices.csv' file to connect to MongoDB, create new collections/tables if needed, extract the data and query it with several specific functions to ensure to that these requirements are met:
1) There are no duplicates uploaded from the dataset.
2) If there are errors in the data, if there are any, it is logged to a file and uploaded to the database as a 'maintenance log'.
3) The data uploaded can then be created, queried, or updated using the MongoDB Altas tools for data analysis and charting.

# Cloud Database

The database that I created as again mentioned was built within the MongoDB Altas platform, which is a NOSQL database, and the reason that I went with this solution is that it is easy to scale, and there is also tons of technical user documentation available for it. 

Here is a brief overview of the structure of the DB:

A. Sites
    - It contains all information related to the site including the name, location and a unique site id to avoid duplicates in the database.
B. Devices
    - It contains overall vitals about the devices, including their status, make, model, and other peritnent information.
C. E-waste 
    - this section is for devices that are EOL or no longer permitted for usage. This was not included as I didn't add any E-Waste Devices in my devices.csv file.
D. Maintenance log
    - This is a collection of all errors that were logged during the upload process, and it contains the error message, the device id, and the date/time stamp of when it was logged. So far, this has not been needed, however, could be salced in the future. 
E. Device Types
    - Last section simply specifies device types by the venor and ensures that these are probably labeled and documented.


[Software Demo Video]()

# Development Environment

I used Python, MongoDB Atlas, Pylance, Visual Code Studio, Github and several plugins from MongoDB to ensure that my coding environment was well structured, alongside with aiding me in the development process, I used MongoDB Documentation to ensure that my cluster for the DB was properly configured. This project overall had several key challenges that were initially identified 

# Useful Websites

* [MongoDB Github Repository](https://github.com/mongodb/mongo)
* [MongoDB Python Documentation](https://www.mongodb.com/docs/languages/python/)
* [MongoDB Youtube Channel](https://youtu.be/c2M-rlkkT5o?feature=shared)
* [W3 Schools](https://www.w3schools.com/python/)


# Future Work

Here are some of the things that I would like to add to this project in the future:

- I think that it would be beneficial to add some flexibility to the script for users being able to upload different csv files, or have more columns that can then be added to the database.
- A newly enhanced GUI would make this an excellent project to showcase, as I could make a new dashboard that is entirely dedicated to the Network Inventory; built either within Python or as a separate web application.
- One deficiency that I have seen with this program is security, as this is a linear program that is not encrypted, and as far as connections go via MongoDB, I am not confident that if this was released in a production environment that it would work as intended. This alone is fine as again this is developmental project, however, adding some sort of encryption or security would be a great addition to this project overall.