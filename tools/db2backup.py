import os
import sqlite3
from datetime import date

# settings

input_db_default = "../db.sqlite3"
backup_db_directory_default = os.path.join(os.path.join(os.path.expanduser('~')), 'Bureau')


# end settings

def progress(status, remaining, total):
    """Progress function"""
    print(f'*Copied {total - remaining} of {total} pages')


# path of the db file
input_db = ""
while True:
    try:
        input_db = input("*Please enter the path of the database file (enter = {0:s}): ".format(input_db_default))
        if len(input_db.strip()) == 0:
            input_db = input_db_default
        break
    except ValueError:
        print("*Sorry, I didn't understand that.")
        continue

# directory
backup_db_directory = "./"
while True:
    try:
        output_db = input(
            "*Please enter the directory where the database must be saved "
            "(directory must be exist, enter = {0:s}): ".format(backup_db_directory_default))
    except ValueError:
        print("*Sorry, I didn't understand that.")
        continue
    else:
        if len(output_db.strip()) == 0:
            backup_db_directory = backup_db_directory_default
        else:
            backup_db_directory = os.path.abspath(output_db.strip())
        if not os.path.isdir(backup_db_directory):
            print("*Directory {0:s} does not exist.".format(backup_db_directory))
            continue
        else:
            break

# create backup file path
b, e = os.path.splitext(os.path.basename(os.path.abspath(input_db)))
date_str = date.today().strftime("%Y%m%d")
backup_db_file = b + "_" + date_str + e
backup_db = os.path.join(backup_db_directory, backup_db_file)

print("*Input database file : {0:s}".format(input_db))
print("*Output database file : {0:s}".format(backup_db))

# check input database
if not os.path.isfile(input_db):
    print('*File {0:s} does not exist.'.format(input_db))
    print("*aborted backup")
    exit(0)

# check output database
if os.path.isfile(backup_db):
    while True:
        print('*File {0:s} already exists. Overwrite [y/n]?'.format(backup_db))
        yn = input("").lower()
        if yn == "y":
            break
        elif yn == "n":
            print("*Aborted backup")
            exit(0)

# backup
try:
    # open connexions
    connexion = sqlite3.connect(input_db)
    connexion_backup = sqlite3.connect(backup_db)

    # backup
    with connexion_backup:
        connexion.backup(connexion_backup, pages=0, progress=progress)
        print("*backup successful")

        if connexion_backup:
            # close connexions
            connexion.close()
            # connexion_backup.close()

except sqlite3.Error as error:

    print("*Error while creating the backup: ", error)

except NameError as error:
    print("*Error")
    exit(1)
