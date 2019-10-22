import mysql.connector
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import make_aware

from base.models import *

# Attention, ce script supprime tout avant de migrer ! (sauf les unités)
# Migre tous les produits et toutes les catégories mais seulement les adhérents visibles

# PERSONNALISER CES VARIABLES

user = "root"
password = "neuneu"
database = "gase"

prefix = "_inde_"

# can be PRODUITS or REFERENCES
product_table = "PRODUITS"

migrate_categories=True
migrate_providers=True
migrate_products=True
migrate_members=True
migrate_appro_comptes=True
migrate_change_stock=True
migrate_achats=True


# FIN DE LA PERSONALISATION


mydb = mysql.connector.connect(
    host="localhost",
    user=user,
    passwd=password,
    database=database
)
mycursor = mydb.cursor()

# ----------------------------------------------------------------------------------------------------------------------
# Unités
# ----------------------------------------------------------------------------------------------------------------------

print('Getting Unit')
vrac_unit, created = Unit.objects.get_or_create(name="kg/L", vrac=True, pluralize=False)
print("   kg/L crée" if created else "   kg/l déjà existante")
non_vrac_unit, created = Unit.objects.get_or_create(name="unité", vrac=False, pluralize=False)
print("   'unité' crée" if created else "   'unité' déjà existante")

# ----------------------------------------------------------------------------------------------------------------------
# Catégories
# ----------------------------------------------------------------------------------------------------------------------

if migrate_categories:
    print('\nMigrating Categories')
    Category.objects.all().delete()
    mycursor.execute("SELECT * FROM " + prefix + "CATEGORIES")
    myresult = mycursor.fetchall()
    for x in myresult:
        # seulement les visibles
        # if (x[4] == 1):
        Category(id=x[0], name=x[1].strip()).save()

# ----------------------------------------------------------------------------------------------------------------------
# Fournisseurs
# ----------------------------------------------------------------------------------------------------------------------

if migrate_providers:
    print('\nMigrating Providers')
    Provider.objects.all().delete()
    mycursor.execute("SELECT * FROM " + prefix + "FOURNISSEURS")
    myresult = mycursor.fetchall()
    for x in myresult:
        # seulement les visibles
        # if (x[10] == 1):
        fax = '' if (x[7] == '') else ('Fax : ' + x[7])
        contact = "\n".join([y for y in [x[2], x[3], x[4], x[5], x[6], fax]
                             if y != ''])
        Provider(id=x[0], name=x[1].strip().title(), contact=contact.strip(), comment=x[9].strip()).save()

# ----------------------------------------------------------------------------------------------------------------------
# Produits
# ----------------------------------------------------------------------------------------------------------------------

if migrate_products:
    print('\nMigrating Products')
    Product.objects.all().delete()
    mycursor.execute("SELECT * FROM " + prefix + product_table)
    myresult = mycursor.fetchall()
    for x in myresult:
        comment = x[9] if (x[8] == '') else ('Code fournisseur : ' + x[8] + '\n' + x[9])
        unit = vrac_unit if (x[3]) else non_vrac_unit
        alert = x[11] if (x[11] != -1) else None
        rqst = "SELECT STOCK FROM  {0}STOCKS WHERE ID_REFERENCE='{1}' AND" \
               " DATE = (SELECT MAX(DATE) FROM {0}STOCKS WHERE ID_REFERENCE='{1}')".format(prefix, x[0])
        mycursor.execute(rqst)
        myresult2 = mycursor.fetchall()
        Product(id=x[0], name=x[1].strip().title(), provider_id=x[2], category_id=x[4], unit=unit,
                price=x[5], pwyw=False, visible=x[7], stock_alert=alert, stock=Decimal(myresult2[0][0]),
                comment=comment.strip()).save()

# ----------------------------------------------------------------------------------------------------------------------
# Adhérents
# ----------------------------------------------------------------------------------------------------------------------

if migrate_members:
    print('\nMigrating Members')
    Household.objects.all().delete()
    Member.objects.all().delete()
    mycursor.execute("SELECT * FROM " + prefix + "ADHERENTS")
    myresult = mycursor.fetchall()
    # ignoring x[11] "RECEIVE_ALERT_STOCK"
    print("{} adhérents à migrer".format(len(myresult)))
    for x in myresult:
        # seulement les visibles
        if x[8] == 1:
            name = (x[2] + ' ' + x[1]).strip().title()
            hsld = Household(id=x[0], name=name, address=x[4].strip(), comment=x[7], date=x[10])
            rqst = "SELECT SOLDE FROM  {0}COMPTES WHERE ID_ADHERENT='{1}' AND " \
                   "DATE = (SELECT MAX(DATE) FROM {0}COMPTES WHERE ID_ADHERENT='{1}')".format(prefix, x[0])
            mycursor.execute(rqst)
            myresult2 = mycursor.fetchall()
            hsld.account = Decimal(myresult2[0][0])
            hsld.save()
            date= make_aware(x[10])
            Household.objects.filter(id=x[0]).update(date=date)
            tel = ((x[5] + ' ' + x[6]) if (x[6]) else x[5]) if (x[5]) else x[6]
            Member(name=name, email=x[3].strip(), tel=tel.strip(), household=hsld, receipt=x[9],
                   stock_alert=False).save()

# ----------------------------------------------------------------------------------------------------------------------
# Appro Comptes
# ----------------------------------------------------------------------------------------------------------------------

if migrate_appro_comptes:
    print('\nMigrating Appro Comptes')
    ApproCompteOp.objects.all().delete()
    mycursor.execute("SELECT * FROM " + prefix + "COMPTES WHERE OPERATION='APPROVISIONNEMENT' ORDER BY DATE ASC")
    myresult = mycursor.fetchall()
    print("{} opérations à migrer".format(len(myresult)))
    i = 1
    for x in myresult:
        if i % 100 == 0:
            print("  - opération {}".format(i))
        i += 1
        try:
            household = Household.objects.get(id=x[0])
        except ObjectDoesNotExist:
            household = None
        op = ApproCompteOp(household=household, amount=x[4])
        op.save()
        date = make_aware(x[2])
        ApproCompteOp.objects.filter(id=op.pk).update(date=date)

# ----------------------------------------------------------------------------------------------------------------------
# Appro Stock + Inventaire
# ----------------------------------------------------------------------------------------------------------------------

if migrate_change_stock:
    print('\nMigrating Appro Stock + Inventory')
    ChangeStockOp.objects.all().delete()
    mycursor.execute("SELECT * FROM " + prefix + "STOCKS ORDER BY DATE ASC")
    myresult = mycursor.fetchall()
    print("{} opérations à migrer".format(len(myresult)))
    i = 1
    for x in myresult:
        if i % 100 == 0:
            print("  - opération {}".format(i))
        i += 1
        if x[2] == 'APPROVISIONNEMENT' or x[2] == 'INVENTAIRE':
            quantity = Decimal(x[4])
            try:
                pdt = Product.objects.get(id=x[0])
                price = pdt.price * quantity
            except ObjectDoesNotExist:
                pdt = None
                price=0
            if x[2] == 'APPROVISIONNEMENT':
                label='ApproStock'
            if x[2] == 'INVENTAIRE':
                label='Inventaire'
            op = ChangeStockOp(product=pdt, quantity=quantity, price=price,
                               stock=Decimal(x[1]), label=label)
            op.save()
            date = make_aware(x[3])
            ChangeStockOp.objects.filter(id=op.pk).update(date=date)

# ----------------------------------------------------------------------------------------------------------------------
# Achats
# ----------------------------------------------------------------------------------------------------------------------

if migrate_achats:
    print('\nMigrating Achats')
    Purchase.objects.all().delete()
    PurchaseDetailOp.objects.all().delete()
    mycursor.execute("SELECT * FROM {}ACHATS ORDER BY DATE_ACHAT ASC ".format(prefix))
    myresult = mycursor.fetchall()
    print("{} achats à migrer".format(len(myresult)))
    i = 1
    for x in myresult:
        if i % 100 == 0:
            print("  - achat {}".format(i))
        i += 1
        try:
            hsld = Household.objects.get(id=x[2])
        except ObjectDoesNotExist:
            hsld = None
        p = Purchase(id=x[0], household=hsld)
        p.save()
        mycursor.execute("SELECT * FROM {0}STOCKS WHERE ID_ACHAT={1} ORDER BY DATE ASC".format(prefix, x[0]))
        myresult2 = mycursor.fetchall()
        for y in myresult2:
            try:
                pdt = Product.objects.get(id=y[0])
                price = pdt.price * Decimal(-y[4])
            except ObjectDoesNotExist:
                price = 0
            pd = PurchaseDetailOp(product_id=y[0], purchase=p, quantity=Decimal(-y[4]),
                                  price=price, stock=Decimal(y[1]), label='Achat')
            pd.save()
            date = make_aware(y[3])
            PurchaseDetailOp.objects.filter(id=pd.pk).update(date=date)
        date = make_aware(x[1])
        Purchase.objects.filter(id=p.pk).update(date=date)
