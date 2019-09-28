from django.db import models
from django.core.exceptions import ValidationError

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
    pluralize = models.BooleanField(verbose_name="Plurieliser ?", default=False, help_text="Ajouter un 's' au pluriel (par ex. 4 sachets mais 4 kg)")

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
def get_advised_household_number():
    numbers = [p.number for p in Household.objects.all()]
    i = 1
    if i not in numbers:
        return i
    while i not in numbers:
        i += 1
    return i


def validate_household_number(value):
    if value in [getattr(p, 'number') for p in Household.objects.all()]:
        advised_value = get_advised_household_number()
        raise ValidationError("Le numéro d'adhérent {0:d} est déjà utilisé ! Le numéro conseillé est le {1:d}.".format(value, advised_value))
        
class Household(models.Model):
    name = models.CharField(max_length=200, help_text="Nom qui apparaitra dans la liste des comptes pour faire ses achats.", verbose_name="nom du foyer")
    number = models.IntegerField(default=0, verbose_name="numero d'adhérent", validators=[validate_household_number])
    address = models.CharField(max_length=200, blank=True, help_text="Pas indispensable mais pratique quand on fait des réunions chez les uns les autres.", verbose_name="adresse")
    comment = models.TextField(blank=True, verbose_name="commentaire")
    account = models.DecimalField(default=0, max_digits=10, decimal_places=2, editable=False, verbose_name="solde du compte") # INVARIANT : account should be sum of operations
    date = models.DateField(auto_now=True) # date d'inscription
    date_closed = models.DateField(blank=True, null=True, verbose_name="Date de clôture", help_text="Remplir seulement si le foyer souhaite arrêter.") # date de cloture

    def __str__(self):
        return self.name

    def get_members(self):
        return Member.objects.filter(household=self.pk)

    def get_emails_receipt(self):
        return [str(m.email) for m in self.get_members().filter(receipt=True)]

    class Meta:
        verbose_name = 'Foyer'
        
    def get_formated_number(self):
        return '{0:03d}'.format(self.number)
        
    def get_formated_date_closed(self, fmt):
        if self.date_closed is not None:
            return self.date_closed.strftime(fmt)
        else:
            return '-'
        

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
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="prix de vente (en €) à l'unité (kg/L/...)") # current price, can vary in the time ...  
    cost_of_purchase = models.DecimalField(default=0.0, max_digits=10, decimal_places=2, verbose_name="prix d'achat (en €) à l'unité (kg/L/...)") # current price, can vary in the time ...
    pwyw = models.BooleanField(default=False, verbose_name="prix libre", help_text="Pas encore géré par le logiciel ...") # PWYW = Pay what you want
    visible = models.BooleanField(default=True, help_text="Une référence non visible n'apparait pas dans les produits que l'on peut acheter, on l'utilise généralement pour les produits en rupture de stock", verbose_name="visible")
    referent = models.ForeignKey(Member, blank=True, null=True, help_text="S'il le souhaite, le référent reçoit un mail à chaque fois qu'un produit est approvisionné ou que le stock devient plus bas que le niveau \"Alerte stock\"", verbose_name="référent", on_delete=models.SET_NULL) # todo : many to many
    stock_alert = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Laisser vide pour pas d'alerte", verbose_name="Seuil de l'alerte stock")
    comment = models.TextField(blank=True, verbose_name="commentaire")
    stock = models.DecimalField(default=0, max_digits=15, decimal_places=3, editable=False, verbose_name="stock") # INVARIANT : stock should be sum of operations
    
    def __str__(self):
        return self.name

    def value_stock(self):
        return self.price * self.stock
        
    def value_purchase(self):
        return self.cost_of_purchase * self.stock

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
    stock = models.DecimalField(max_digits=15, decimal_places=3) # stock after the operation
    label = models.CharField(max_length=20)

    @classmethod    # constructor computing price
    def create(cls, product=product, quantity=quantity, **kwargs):
        price = product.price * quantity
        newstock = product.stock + quantity
        return cls(product=product, quantity=quantity, price=price, stock=newstock, **kwargs)

    @classmethod
    def create_appro_stock(cls, **kwargs):
        return cls.create(label='ApproStock', **kwargs)

    @classmethod
    def create_inventory(cls, **kwargs):
        return cls.create(label='Inventaire', **kwargs)
        
    def cost_of_purchase(self):
        if self.label != "ApproStock":
            raise TypeError("Operation must be filter with label==ApproStock")
        return self.product.cost_of_purchase * self.quantity

    def __str__(self):
        return '{} : {} - {}'.format(self.label, self.product, self.quantity)

class Purchase(Operation):
    household = models.ForeignKey(Household, null=True, on_delete=models.SET_NULL) # null if the household was deleted and no longer exists

class PurchaseDetailOp(ChangeStockOp):
    purchase = models.ForeignKey(Purchase, null=False, on_delete=models.CASCADE)
    @classmethod
    def create(cls, **kwargs):
        return super().create(label='Achat', **kwargs)

class ApproCompteOp(Operation):
    household = models.ForeignKey(Household, null=True, on_delete=models.SET_NULL) # null if the household was deleted and no longer exists
    amount = models.DecimalField(max_digits=15, decimal_places=2) # positif for a regular appro
    CASH = 'cash'
    CHEQUE = 'cheque'
    CANCELLATION = 'cancellation'
    REPAYMENT = 'repayment'
    KIND_CHOICES = [
        (CASH, 'Espèces'),
        (CHEQUE, 'Chèque'),
        (CANCELLATION, 'Annulation/Correction'),
        (REPAYMENT, 'Remboursement')
    ]
    kind = models.CharField(max_length=6, choices=KIND_CHOICES, default=CASH)
    def __str__(self):
        return 'ApproCompteOp {} - {} - {}'.format(self.household, self.amount, self.get_kind_display())

# message
class Note(models.Model):    
    date = models.DateTimeField(auto_now=True) 
    who = models.ForeignKey(Member, null=True, on_delete=models.SET_NULL, verbose_name="Qui ?") # null if the product was deleted and no longer exists
    message = models.TextField(blank=False, verbose_name="Message")
    read = models.BooleanField(verbose_name="Message lu ?", default=False)
    action = models.BooleanField(verbose_name="Action(s) réalisée(s) ?", default=False, help_text="Si aucune action n'est nécessaire, côcher cette case.")


# there should be only one instance of this model
class LocalSettings(models.Model):
    min_account = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="seuil en dessous duquel on ne peut plus faire d'achat (en €)")
    txt_home = models.TextField(blank=True, default="<i>Bienvenu·e au GASE</i>", verbose_name="texte de la page d'accueil (doit être donnée en code html)")
    class Meta:
        verbose_name = "Réglages divers"
