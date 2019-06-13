from django.db import models
from .utils import *

class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom")

    def __str__(self):
        return self.name

    def get_products(self):
        return Product.objects.filter(category=self.pk)

    class Meta:
        verbose_name = 'Catégorie'


class Unit(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom")
    vrac = models.BooleanField(verbose_name="Vrac", help_text="Oui pour kg, L, ... Non pour sachet, bouteille, ...")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Unité'


class Provider(models.Model):
    name = models.CharField(max_length=200, verbose_name="nom")
    contact = models.TextField(blank=True, verbose_name="mail / téléphone / adresse du fournisseur")
    comment = models.TextField(blank=True, verbose_name="commentaire (quel Gasier a été en contact, historique des échanges, ...)")

    def __str__(self):
        return self.name

    def get_products(self):
        return Product.objects.filter(provider=self.pk)

    class Meta:
        verbose_name = 'Fournisseur'


# foyer
class Household(models.Model):
    name = models.CharField(max_length=200, help_text="Nom qui apparaitra dans la liste des comptes pour faire ses achats", verbose_name="nom du foyer")
    address = models.CharField(max_length=200, blank=True, help_text="Pas indispensable mais pratique quand on fait des réunions chez les uns les autres", verbose_name="adresse")
    comment = models.TextField(blank=True, verbose_name="commentaire")
    account = models.DecimalField(default=0, max_digits=10, decimal_places=2, editable=False, verbose_name="solde du compte") # INVARIANT : account should be sum of operations
    date = models.DateField(auto_now=True) # date d'inscription

    def __str__(self):
        return self.name

    def get_members(self):
        return Member.objects.filter(household=self.pk)

    def get_emails_receipt(self):
        return [str(m.email) for m in self.get_members().filter(receipt=True)]

    class Meta:
        verbose_name = 'Foyer'


class Member(models.Model):
    name = models.CharField(max_length=200, verbose_name="nom")
    email = models.EmailField(blank=True, null=True, verbose_name="email")
    tel = models.CharField(max_length=200, blank=True, verbose_name="numéro de téléphone")
    household = models.ForeignKey(Household, blank=True, null=True, related_name="has_household", on_delete=models.CASCADE, verbose_name="foyer")
    # receive the receipt by mail
    receipt = models.BooleanField(default=True, verbose_name="recevoir un ticket de caisse par mail ?")
    stock_alert = models.BooleanField(default=True, verbose_name="recevoir les approvisionnements et les alertes stock par mail ? (uniquement pour les référents produit)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Membre'


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="nom")
    provider = models.ForeignKey(Provider, verbose_name="fournisseur", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, verbose_name="catégorie", on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, verbose_name="unité", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="prix (en €) à l'unité (kg/L/...)") # current price, can vary in the time ...
    pwyw = models.BooleanField(default=False, verbose_name="prix libre", help_text="Pas encore géré par le logiciel ...") # PWYW = Pay what you want
    visible = models.BooleanField(default=True, help_text="Une référence non visible n'apparait pas dans les produits que l'on peut acheter, on l'utilise généralement pour les produits en rupture de stock", verbose_name="visible")
    referent = models.ForeignKey(Member, blank=True, null=True, help_text="S'il le souhaite, le référent reçoit un mail à chaque fois qu'un produit est approvisionné ou que le stock devient plus bas que le niveau \"Alerte stock\"", verbose_name="référent", on_delete=models.SET_NULL) # todo : many to many
    stock_alert = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Laisser vide pour pas d'alerte", verbose_name="Alerte stock")
    comment = models.TextField(blank=True, verbose_name="commentaire")
    stock = models.DecimalField(default=0, max_digits=15, decimal_places=3, editable=False, verbose_name="stock") # INVARIANT : stock should be sum of operations
    
    def __str__(self):
        return self.name

    def value_stock(self):
        return self.price * self.stock

    def get_email_stock_alert(self):
        if (self.referent and self.referent.stock_alert and self.referent.email != ''):
            return str(self.referent.email)
        else:
            return None

    class Meta:
        verbose_name = 'Produit'


class Operation(models.Model):
    date = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class ChangeStockOp(Operation):
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL) # null if the product was deleted and no longer exists
    quantity = models.DecimalField(max_digits=15, decimal_places=3) # positif for an appro, negative for a normal buying
    price = models.DecimalField(max_digits=15, decimal_places=3) # product.price * quantity
    stock = models.DecimalField(max_digits=15, decimal_places=3) # stock before the operation
    label = models.CharField(max_length=20)
    class Meta:
        abstract = True

    @classmethod    # constructor computing price
    def create(cls, product=product, quantity=quantity, **kwargs):
        price = product.price * quantity
        return cls(product=product, quantity=quantity, price=price, stock=product.stock, **kwargs)

    def create_appro_stock(cls, **kwargs):
        cls.create(label='ApproStock', **kwargs)

    def create_inventory(cls, **kwargs):
        cls.create(label='Inventaire', **kwargs)

    def __str__(self):
        return '{} : {} - {}'.format(self.label, self.product, self.quantity)

class Purchase(Operation):
    household = models.ForeignKey(Household, null=True, on_delete=models.SET_NULL) # null if the household was deleted and no longer exists

class PurchaseDetailOp(ChangeStockOp):
    purchase = models.ForeignKey(Purchase, null=False, on_delete=models.CASCADE)

    @classmethod
    def create(cls, *args, **kwargs):
        super().create(label='Achat', *arsg, **kwargs)

class ApproStockOp(ChangeStockOp):
    @classmethod
    def create(cls, *args, **kwargs):
        super().create(label='ApproStock', *arsg, **kwargs)

class InventoryOp(ChangeStockOp):
    def __str__(self):
        return 'Inventaire' + super().__str__()

class ApproCompteOp(Operation):
    household = models.ForeignKey(Household, null=True, on_delete=models.SET_NULL) # null if the household was deleted and no longer exists
    amount = models.DecimalField(max_digits=15, decimal_places=2) # positif for a regular appro
    def __str__(self):
        return 'ApproCompteOp {} - {}'.format(self.household, self.amount)


# there should be only one instance of this model
class LocalSettings(models.Model):
    min_account = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="seuil en dessous duquel on ne peut plus faire d'achat (en €)")
    txt_home = models.TextField(blank=True, default="<i>Bienvenu au GASE</i>", verbose_name="texte de la page d'accueil (doit être donnée en code html)")
    class Meta:
        verbose_name = "Réglages divers"
