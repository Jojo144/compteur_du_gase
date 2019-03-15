from django.db import models
from django.db.models import Sum
from .utils import *

class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def get_products(self):
        return Product.objects.filter(category=self.pk)

    class Meta:
        verbose_name = 'Catégorie'


class Provider(models.Model):
    name = models.CharField(max_length=200)
    contact = models.TextField(blank=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def get_products(self):
        return Product.objects.filter(provider=self.pk)

    class Meta:
        verbose_name = 'Fournisseur'


# foyer
class Household(models.Model):
    name = models.CharField("Nom", max_length=200)
    # persons = models.ManyToManyField(Member)
    address = models.CharField("Adresse", max_length=200, blank=True)
    comment = models.TextField(blank=True)
    account = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    date = models.DateField(auto_now=True) # date d'inscription

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Foyer'


class Member(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    tel = models.CharField(max_length=200, blank=True)
    household = models.ForeignKey(Household, verbose_name="Foyer", on_delete=models.CASCADE)
    # @property
    # def foyer(self):
    #     return Household.objects.filter(persons=self)

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
    member = models.ForeignKey(Household, on_delete=models.CASCADE) #todo: ça va pas
    quantity = models.DecimalField(max_digits=15, decimal_places=3) # négatif
    @property
    def price(self):
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
    member = models.ForeignKey(Household, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=3) # positif
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
