from base.models import *
import mysql.connector 

# - Attention, çe script écrase les objects qui ont déjà le même id
# - La base est supposée vide !
#   Sinon vous pourriez avoir des anciens membres qui se rajoutent dans les foyers ...

# PERSONNALISER CES VARIABLES

user = "root"
password = "neuneu"
database = "gase"

prefix="_inde_"

# can be PRODUITS or REFERENCES
product_table = "PRODUITS"

# FIN DE LA PERSONALISATION


mydb = mysql.connector.connect(
    host="localhost",
    user=user,
    passwd=password,
    database=database
)
mycursor = mydb.cursor()


# ## Unités ##

# vrac_unit=Unit(name="kg/L", vrac=True, pluralize=False)
# vrac_unit.save()
# non_vrac_unit=Unit(name="unité", vrac=False, pluralize=False)
# non_vrac_unit.save()


# ## Catégories ##

# mycursor.execute("SELECT * FROM " + prefix + "CATEGORIES")
# myresult = mycursor.fetchall()

# for x in myresult:
#     # seulement les visibles
#     if (x[4] == 1):
#         Category(id=x[0], name=x[1]).save()


# ## Fournisseurs ##

# mycursor.execute("SELECT * FROM " + prefix + "FOURNISSEURS")
# myresult = mycursor.fetchall()

# for x in myresult:
#     # seulement les visibles
#     if (x[10] == 1):
#         fax = '' if (x[7] == '') else ('Fax : ' + x[7])
#         contact="\n".join([y for y in [x[2], x[3], x[4], x[5], x[6], fax]
#                            if y != ''])
#         Provider(id=x[0], name=x[1], contact=contact, comment=x[9]).save()


# ## Produits ##

# mycursor.execute("SELECT * FROM " + prefix + product_table)
# myresult = mycursor.fetchall()

# for x in myresult:
#     comment = x[9] if (x[8] == '') else ('Code fournisseur : ' + x[8] + '\n' + x[9])
#     unit = vrac_unit if (x[3]) else non_vrac_unit
#     alert= x[11] if (x[11] != -1) else None
#     Product(id=x[0], name=x[1], provider_id=x[2], category_id=x[4], unit=unit,
#             price=x[5], pwyw=False, visible=x[7], stock_alert=alert,
#             comment=comment).save()


# ## Adhérents ##

# mycursor.execute("SELECT * FROM " + prefix + "ADHERENTS")
# myresult = mycursor.fetchall()

# # ignoring x[11] "RECEIVE_ALERT_STOCK"
# for x in myresult:
#     # seulement les visibles
#     if (x[8] == 1):
#         name = x[2] + ' ' + x[1]
#         hsld=Household(id=x[0], name=name, address=x[4], comment=x[7], date=x[10])
#         tel = ((x[5] + ' ' + x[6]) if (x[6]) else x[5]) if (x[5]) else x[6]
#         hsld.save()
#         Member(name=name, email=x[3], tel=tel, household=hsld, receipt=x[9],
#                stock_alert=False).save()


## Appro Comptes ##

mycursor.execute("SELECT * FROM " + prefix + "COMPTES ORDER BY DATE ASC")
myresult = mycursor.fetchall()

from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import make_aware

for x in myresult:
    # pas les dépenses
    if (x[3] == 'APPROVISIONNEMENT'):
        try:
            household=Household.objects.get(id=x[0])
        except ObjectDoesNotExist:
            household=None
        op=ApproCompteOp(household=household, amount=x[4])
        op.save()
        date= make_aware(x[2])
        ApproCompteOp.objects.filter(id=op.pk).update(date=date)

# ApproCompteOp.objects.all().delete()
