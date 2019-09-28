import os
import sqlite3

# settings

delimiter = ";"
output_directory = "./csv"

# end settings

# open connexion
connexion = sqlite3.connect("../db.sqlite3")

# cursor
cursor = connexion.cursor()

# get all tables and filter with name
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall() if t[0].startswith("base_")]

# create output directory
if not os.path.isdir(output_directory):
    os.makedirs(output_directory)

# loop on tables
for table in tables:

    # open file
    fw_path = os.path.join(output_directory, table + ".csv")
    print("*Writing " + fw_path)
    fw = open(fw_path, 'w')

    # set cursor
    cursor.execute("SELECT * FROM {0:s}".format(table))

    # get description
    names = [description[0] for description in cursor.description]

    # write header
    fw.write((" " + delimiter).join(names) + "\n")

    # write data
    for result in cursor:
        print(result)
        fw.write((" " + delimiter).join([str(r).replace("\n", " ").replace("\r", " ") for r in result]) + "\n")

    # close file
    fw.close()

# close connexion
connexion.close()
