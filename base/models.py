from django.db import models
from django.db.models import Sum
from .utils import *

class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom")

    def __str__(self):
        return self.name

    def get_products(self):
        return Product.objects.filter(category=self.pk)

    class Meta:
        verbose_name = 'Catégorie'


class Provider(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom")
    contact = models.TextField(blank=True, verbose_name="Mail / téléphone / adresse du fournisseur")
    comment = models.TextField(blank=True, verbose_name="Commentaire (quel Gasier a été en contact, historique des échages, ...)")

    def __str__(self):
        return self.name

    def get_products(self):
        return Product.objects.filter(provider=self.pk)

    class Meta:
        verbose_name = 'Fournisseur'


# foyer
class Household(models.Model):
    name = models.CharField("Nom", max_length=200)
    address = models.CharField("Adresse", max_length=200, blank=True)
    comment = models.TextField(blank=True, verbose_name="Commentaire")
    account = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="Solde du compte")
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
    name = models.CharField(max_length=200, verbose_name="Nom")
    email = models.EmailField(blank=True, null=True)
    tel = models.CharField(max_length=200, blank=True)
    household = models.ForeignKey(Household, verbose_name="Foyer", on_delete=models.CASCADE)
    # receive the receipt by mail
    receipt = models.BooleanField(default=True, verbose_name="Recevoir un ticket de caisse par mail ?")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Membre'


class Product(models.Model):
    name = models.CharField("Nom", max_length=200)
    provider = models.ForeignKey(Provider, verbose_name="Fournisseur", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, verbose_name="Catégorie", on_delete=models.CASCADE)
    price = models.DecimalField("Prix", max_digits=10, decimal_places=2)
    pwyw = models.BooleanField("Prix libre", default=False) # PWYW = Pay what you want
    vrac = models.BooleanField("Vrac")
    visible = models.BooleanField("Visible", default=True, null=False)
    comment = models.TextField("Commentaire", blank=True)
    referent = models.ForeignKey(Member, blank=True, null=True, verbose_name="Référent", on_delete=models.CASCADE) # todo : many to many
    stock = models.DecimalField("Stock", default=0, max_digits=15, decimal_places=3)
    
    def __str__(self):
        return self.name

    def value(self):
        return self.price * self.stock

    class Meta:
        verbose_name = 'Produit'


class Operation(models.Model):
    date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return 'Opération - %s' % self.date

    class Meta:
        verbose_name = 'Opération'

class AchatOp(Operation):
    product = models.ForeignKey(Product, on_delete=models.CASCADE) #todo: ça va pas
    household = models.ForeignKey(Household, on_delete=models.CASCADE) #todo: ça va pas
    quantity = models.DecimalField(max_digits=15, decimal_places=3) # négatif
    @property
    def price(self):  # TODO ça va pas le prix d'une référence peut changer !
        return - self.product.price * self.quantity # positif
    def __str__(self):
        return 'Achat {} - {}'.format(self.product, self.quantity)

class ApproStockOp(Operation):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=15, decimal_places=3) # positif
    @property
    def price(self):
        return self.product.price * self.quantity
    def __str__(self):
        return 'Appro'

class ApproCompteOp(Operation):
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2) # positif
    def __str__(self):
        return 'ApproCompte'

class InventoryOp(Operation):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=15, decimal_places=3) # négatif si perte
    @property
    def price(self):
        return self.product.price * self.quantity # négatif si perte
    def __str__(self):
        return 'Inventaire'

# there should be only one instance of this model
class LocalSettings(models.Model):
    class Meta:
        verbose_name = "Réglages divers"
    min_account = models.DecimalField("Seuil en dessous duquel on ne peut plus faire d'achat", max_digits=10, decimal_places=2, default=0)
