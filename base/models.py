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
    account = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="Solde du compte") # INVARIANT : account should be sum of operations
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
    stock_alert = models.BooleanField(default=True, verbose_name="Recevoir les alertes stock par mail ? (uniquement pour les référents produit)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Membre'


class Product(models.Model):
    name = models.CharField("Nom", max_length=200)
    provider = models.ForeignKey(Provider, verbose_name="Fournisseur", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, verbose_name="Catégorie", on_delete=models.CASCADE)
    price = models.DecimalField("Prix à l'unité (kg/L/...)", max_digits=10, decimal_places=2) # current price, can vary in the time ...
    pwyw = models.BooleanField("Prix libre", default=False, help_text="Pas encore géré par le logiciel ...") # PWYW = Pay what you want
    vrac = models.BooleanField("Vrac") # todo = unité
    visible = models.BooleanField("Visible", default=True, null=False, help_text="Une référence non visible n'apparait pas dans les produits que l'on peut acheter, on l'utilise généralement pour les produits e rupture de stock")
    referent = models.ForeignKey(Member, blank=True, null=True, verbose_name="Référent", on_delete=models.SET_NULL) # todo : many to many
    comment = models.TextField("Commentaire", blank=True)
    stock = models.DecimalField("Stock", default=0, max_digits=15, decimal_places=3) # INVARIANT : stock should be sum of operations
    
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
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL) # null if the product was deleted and no longer exists
    household = models.ForeignKey(Household, null=True, on_delete=models.SET_NULL) # null if the household was deleted and no longer exists
    quantity = models.DecimalField(max_digits=15, decimal_places=3) # negative for a regular achat
    price = models.DecimalField(max_digits=15, decimal_places=3) # positive for a regular achat (we record it because pdt.price can vary in the time)

    # constructor computing price
    def __init__(self, product=product, household=household, quantity=quantity, *args, **kwargs):
        price = - product.price * quantity
        super().__init__(product=product, household=household, quantity=quantity, price=price, *args, **kwargs)
    def __str__(self):
        return 'Achat {} - {}'.format(self.product, self.quantity)

class ApproStockOp(Operation):
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL) # null if the product was deleted and no longer exists
    quantity = models.DecimalField(max_digits=15, decimal_places=3) # positif for a regular appro
    price = models.DecimalField(max_digits=15, decimal_places=3) # positive for a regular appro (we record it because pdt.price can vary in the time)

    # constructor computing price
    def __init__(self, product=product, quantity=quantity, *args, **kwargs):
        price = product.price * quantity
        super().__init__(product=product, quantity=quantity, price=price, *args, **kwargs)
    def __str__(self):
        return 'Appro'

class ApproCompteOp(Operation):
    household = models.ForeignKey(Household, null=True, on_delete=models.SET_NULL) # null if the household was deleted and no longer exists
    amount = models.DecimalField(max_digits=15, decimal_places=2) # positif for a regular appro
    def __str__(self):
        return 'ApproCompte'

class InventoryOp(Operation):
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL) # null if the household was deleted and no longer exists
    quantity = models.DecimalField(max_digits=15, decimal_places=3) # négatif si perte
    price = models.DecimalField(max_digits=15, decimal_places=3) # negative if loss (we record it because pdt.price can vary in the time)

    # FIXME I don't understand this bug! (apparait sur ecart)
    # # constructor computing price
    # def __init__(self, product=product, quantity=quantity, *args, **kwargs):
    #     print("lolololo")
    #     print(product)
    #     price = product.price * quantity
    #     super().__init__(product=product, quantity=quantity, price=price, *args, **kwargs)
    def __str__(self):
        return 'Inventaire'

# there should be only one instance of this model
class LocalSettings(models.Model):
    min_account = models.DecimalField("Seuil en dessous duquel on ne peut plus faire d'achat", max_digits=10, decimal_places=2, default=0)
    txt_home = models.TextField(blank=True, verbose_name="Texte de la page d'accueil (doit être donnée en code html)", default="<i>Bienvenu au GASE</i>")
    mail_admin = models.EmailField(blank=True, null=True, verbose_name="Mail de l'admin à qui sont reporté les erreurs du logiciel")
    class Meta:
        verbose_name = "Réglages divers"
