from django.db import models
from django.core.exceptions import ValidationError
from django import forms


# there should be only one instance of this model
class LocalSettings(models.Model):
    min_account = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                      verbose_name="seuil en dessous duquel on ne peut plus faire d'achat (en €)")

    min_account_allow = models.BooleanField(verbose_name="Lorsque le solde n'est pas suffisant, autoriser quand même après demande de confirmation ?", default=False,
                                            help_text="Lorsque cette option est activée, si le solde n'est pas suffisant, il y a une demande de confirmation"
                                                      "lors de l'achat mais il est autorisé. Dans le cas contraire, l'achat est rendu impossible.")

    min_balance = models.DecimalField(max_digits=10, decimal_places=2, default=10,
                                      verbose_name="seuil en dessous duquel une alerte est lancée au moment de commencer un achat (en €)")

    txt_home = models.TextField(blank=True, default="<i>Bienvenu·e au GASE</i>",
                                verbose_name="texte de la page d'accueil (doit être donnée en code html)")

    use_messages = models.BooleanField(verbose_name="Utilisation de la fonction messages/actions ?", default=True,
                                       help_text="La fonction messages/actions sert à laisser des messages"
                                                 "entre les différentes permanences ou lister des actions à faire.")

    use_appro_kind = models.BooleanField(verbose_name="Utilisation de la fonction type de paiement ?", default=True,
                                         help_text="La fonction type de paiement permet de sauvegarder le moyen "
                                                   "de paiement utilisé.")

    use_subscription = models.BooleanField(verbose_name="Utilisation de la fonction cotisation d'adhésion ?", default=True,
                                           help_text="La fonction adhésion permet de renseigner la cotisation d'adhésion"
                                                     "d'adhésion du foyer.")

    use_cost_of_purchase = models.BooleanField(verbose_name="Utilisation de la fonction prix d'achat ?", default=True,
                                               help_text="La fonction prix d'achat permet de spécifier un prix d'achat "
                                                         "différent du prix de vente.")

    use_exports = models.BooleanField(verbose_name="Utiliser les exports ?", default=True,
                                       help_text="Exports de l'historique d'achat et de la liste des produits.")


    use_logo = models.BooleanField(verbose_name="Affiche le logo dans la première page ?", default=True,
                                       help_text="Le fichier de logo doit être placé dans le répertoire base\static\base"
                                                 " et son nom de fichier doit etre logo.png.")

    use_favicon = models.BooleanField(verbose_name="Affiche une favicon ?", default=True,
                                       help_text="Le fichier favicon doit être placé dans le répertoire base\static\base"
                                                 " et son nom de fichier doit etre favicon.ico.")

    use_mail = models.BooleanField(verbose_name="Utilisation de la fonction envoi d'email ?", default=True,
                                   help_text="Cette fonction permet d'envoyer les tickets de caisse ou "
                                             "des alertes stocks aux référents des produits.")

    save_mail = models.BooleanField(verbose_name="Utilisation de la fonction de sauvegarde des emails ?", default=True,
                                    help_text="Cette fonction permet de sauvegarder les emails envoyés ou en attente.")

    prefix_object_mail = models.CharField(blank=True, verbose_name="Prefix dans l'objet des emails.", default="", max_length=15,
                                          help_text="Un prefix est souvent encadré par des crochers, exemples : [GASE].")

    debug_mail = models.CharField(blank=True, verbose_name="Si ce champ est renseigné, tous les emails lui seront envoyés.",
                                  default="", max_length=50,
                                  help_text="Ce champ permet de tester la fonction email sans envoyer de mails intempestifs.")

    mail_host = models.CharField(blank=False, verbose_name="Hebergeur pour l'envoi des mails.",
                                  default="xxx", max_length=50,
                                  help_text="Exemple : smtp.titi.com.")

    mail_port = models.IntegerField(verbose_name="Port smtp pour l'envoi des mails.",
                                    default=465,
                                    help_text="Exemple : 25 (sans chiffrement), 465 (chiffrement implicite, SSL), 587 (chiffrement explicite, TLS).")

    mail_protocole = models.CharField(choices=[('no', 'Pas de chiffrement'), ('tls', 'Utiliser TLS'), ('ssl', 'Utiliser SSL')],
                                        verbose_name="Protocole utilisé pour l'envoie de mails.",
                                        default="no", max_length=100)

    mail_timeout = models.IntegerField(default=4, verbose_name="Timeout pour l'envoi de mail.")

    mail_username = models.CharField(blank=False, verbose_name="Nom d'utilisateur pour l'envoi des mails.",
                                     default="tata@titi.com", max_length=100,
                                     help_text="Exemple : tata@titi.com.")

    mail_passwd = models.CharField(blank=False, verbose_name="Mot de passe pour l'envoi des mails.",
                                   default="xxx", max_length=100)

    class Meta:
        verbose_name = "Réglages divers"
        verbose_name_plural = "Réglages divers"

def get_local_settings():
    localsettings = LocalSettings.objects.first()
    if localsettings is None:
        localsettings = LocalSettings.objects.create()
    return localsettings


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom")

    def __str__(self):
        return self.name

    def get_products(self):
        return Product.objects.filter(category=self.pk)

    class Meta:
        verbose_name = 'Catégorie'
        ordering = ['name']


class Unit(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom")
    vrac = models.BooleanField(verbose_name="Vrac", help_text="Oui pour kg, L, ... Non pour sachet, bouteille, ...")
    pluralize = models.BooleanField(verbose_name="Plurieliser ?", default=False,
                                    help_text="Ajouter un 's' au pluriel (par ex. 4 sachets mais 4 kg)")

    def plural_name(self):
        if (self.pluralize):
            return (self.name + 's')
        else:
            return (self.name)

    def __str__(self):
        return (self.name + (' (vrac)' if self.vrac else ' (non vrac)'))

    class Meta:
        verbose_name = 'Unité'


class Provider(models.Model):
    name = models.CharField(max_length=200, verbose_name="nom")
    contact = models.TextField(blank=True, verbose_name="mail / téléphone / adresse du fournisseur")
    comment = models.TextField(blank=True,
                               verbose_name="commentaire (quel Gasier a été en contact, historique des échanges, ...)")

    def __str__(self):
        return self.name

    def get_products(self):
        return Product.objects.filter(provider=self.pk)

    class Meta:
        verbose_name = 'Fournisseur'
        ordering = ['name']

# foyer
def get_advised_household_number():
    numbers = [p.number for p in Household.objects.all()]
    i = 1
    if i not in numbers:
        return i
    while i in numbers:
        i += 1
    return i


def validate_household_number(value):
    return # cette verification empeche de modifier un foyer, a corriger
    if value in [getattr(p, 'number') for p in Household.objects.all()]:
        advised_value = get_advised_household_number()
        raise ValidationError(
            "Le numéro d'adhérent {0:d} est déjà utilisé ! Le numéro conseillé est le {1:d}.".format(value,
                                                                                                     advised_value))


class Household(models.Model):
    name = models.CharField(max_length=200,
                            help_text="Nom qui apparaitra dans la liste des comptes pour faire ses achats.",
                            verbose_name="nom du foyer")
    number = models.IntegerField(default=0, verbose_name="numero d'adhérent", validators=[validate_household_number])
    address = models.CharField(max_length=200, blank=True,
                               help_text="Pas indispensable mais pratique quand on fait des réunions "
                                         "chez les uns les autres.",
                               verbose_name="adresse")
    comment = models.TextField(blank=True, verbose_name="commentaire")
    account = models.DecimalField(default=0, max_digits=10, decimal_places=2, editable=False,
                                  verbose_name="solde du compte")  # INVARIANT : account should be sum of operations
    date = models.DateField(auto_now_add=True)  # date d'inscription
    date_closed = models.DateField(blank=True, null=True, verbose_name="Date de clôture",
                                   help_text="Remplir seulement si le foyer souhaite arrêter.")  # date de cloture
    subscription = models.DecimalField(default=0, max_digits=10, decimal_places=2,
                                       verbose_name="montant de la cotisation d'adhésion (en €)")

    on_the_flight = models.BooleanField(verbose_name="Realise un approvisionnement automatique du montant du panier avant de payer.", default=False,
                                        help_text="Cette fonction peut être utilise si l'on autorise le payement à la volée, c'est-à-dire lorsque "
                                                  "le client n'a pas besoin d'approvisionner son compte mais paye la juste somme.")

    def __str__(self):
        return self.name

    def get_members(self):
        return Member.objects.filter(household=self.pk)

    def get_emails_receipt(self):
        return [str(m.email) for m in self.get_members().filter(receipt=True)]

    class Meta:
        verbose_name = 'Foyer'
        ordering = ['name']

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
    household = models.ForeignKey(Household, blank=True, null=True, related_name="has_household",
                                  on_delete=models.CASCADE, verbose_name="foyer")
    # receive the receipt by mail
    receipt = models.BooleanField(default=False, verbose_name="recevoir un ticket de caisse par mail ?")
    stock_alert = models.BooleanField(default=False,
                                      verbose_name="recevoir les approvisionnements et les alertes stock par mail ? "
                                                   "(uniquement pour les référents produit)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Membre'
        ordering = ['name']


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="nom")
    provider = models.ForeignKey(Provider, verbose_name="fournisseur", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, verbose_name="catégorie", on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, verbose_name="unité", on_delete=models.CASCADE)
    # current price, can vary in the time ...
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                verbose_name="prix de vente (en €) à l'unité (kg/L/...)")
    # current price, can vary in the time ...
    cost_of_purchase = models.DecimalField(default=0.0, max_digits=10, decimal_places=2,
                                           verbose_name="prix d'achat (en €) à l'unité (kg/L/...)")
    pwyw = models.BooleanField(default=False, verbose_name="prix libre",
                               help_text="Pas encore géré par le logiciel ...")  # PWYW = Pay what you want
    visible = models.BooleanField(default=True,
                                  help_text="Une référence non visible n'apparait pas dans les produits que l'on peut"
                                            " acheter, on l'utilise généralement pour les produits en rupture de stock",
                                  verbose_name="visible")
    referent = models.ForeignKey(Member, blank=True, null=True,
                                 help_text="S'il le souhaite, le référent reçoit un mail à chaque fois qu'un produit"
                                           " est approvisionné ou que le stock devient plus bas"
                                           " que le niveau \"Alerte stock\"",
                                 verbose_name="référent", on_delete=models.SET_NULL)  # todo : many to many
    stock_alert = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                      help_text="Laisser vide pour pas d'alerte",
                                      verbose_name="Seuil de l'alerte stock")
    comment = models.TextField(blank=True, verbose_name="commentaire")
    stock = models.DecimalField(default=0, max_digits=15, decimal_places=3, editable=False,
                                verbose_name="stock")  # INVARIANT : stock should be sum of operations

    def __str__(self):
        return self.name

    def value_stock(self):
        return self.price * self.stock

    def value_purchase(self):
        return self.cost_of_purchase * self.stock

    def get_email_stock_alert(self):
        if self.referent and self.referent.stock_alert and self.referent.email != '':
            return str(self.referent.email)
        else:
            return None

    class Meta:
        verbose_name = 'Produit'
        ordering = ['name']


class Operation(models.Model):
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class ChangeStockOp(Operation):
    product = models.ForeignKey(Product, null=True,
                                on_delete=models.SET_NULL)  # null if the product was deleted and no longer exists
    quantity = models.DecimalField(max_digits=15,
                                   decimal_places=3)  # positif for an appro, negative for a normal buying
    price = models.DecimalField(max_digits=15, decimal_places=3)  # product.price * quantity
    purchase_cost = models.DecimalField(max_digits=15, decimal_places=3, default=0)  # product.cost_of_purchase * quantity
    stock = models.DecimalField(max_digits=15, decimal_places=3)  # stock after the operation
    label = models.CharField(max_length=20)

    @classmethod  # constructor computing price and cost_of_purchase
    def create(cls, product=product, quantity=quantity, **kwargs):
        price = product.price * quantity
        purchase_cost = product.cost_of_purchase * quantity
        newstock = product.stock + quantity
        return cls(product=product, quantity=quantity, price=price, purchase_cost=purchase_cost, stock=newstock, **kwargs)

    @classmethod
    def create_appro_stock(cls, **kwargs):
        return cls.create(label='ApproStock', **kwargs)

    @classmethod
    def create_inventory(cls, **kwargs):
        return cls.create(label='Inventaire', **kwargs)

    def cost_of_purchase(self):
        if self.label != "ApproStock":
            raise TypeError("Operation must be filter with label==ApproStock")
        return self.purchase_cost

    def cost_of_price(self):
        if self.label != "ApproStock":
            raise TypeError("Operation must be filter with label==ApproStock")
        return self.price

    def __str__(self):
        return '{} : {} - {}'.format(self.label, self.product, self.quantity)


class Purchase(Operation):
    household = models.ForeignKey(Household, null=True,
                                  on_delete=models.SET_NULL)  # null if the household was deleted and no longer exists


class PurchaseDetailOp(ChangeStockOp):
    purchase = models.ForeignKey(Purchase, null=False, on_delete=models.CASCADE)

    @classmethod
    def create(cls, **kwargs):
        return super().create(label='Achat', **kwargs)


class ApproCompteOp(Operation):
    household = models.ForeignKey(Household, null=True,
                                  on_delete=models.SET_NULL)  # null if the household was deleted and no longer exists
    amount = models.DecimalField(max_digits=15, decimal_places=2)  # positif for a regular appro
    CASH = 'cash'
    CHEQUE = 'cheque'
    CANCELLATION = 'cancellation'
    REPAYMENT = 'repayment'
    ONTHEFLIGHT = 'ontheflight'
    KIND_CHOICES = [
        (CASH, 'Espèces'),
        (CHEQUE, 'Chèque'),
        (CANCELLATION, 'Annulation/Correction'),
        (REPAYMENT, 'Remboursement'),
        (ONTHEFLIGHT, 'A la volée'),
    ]
    kind = models.CharField(max_length=6, choices=KIND_CHOICES, default=CASH, null=True)

    def __str__(self):
        return 'ApproCompteOp {} - {} - {}'.format(self.household, self.amount, self.get_kind_display())


# message
class Note(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    who = models.ForeignKey(Member, null=True, on_delete=models.SET_NULL,
                            verbose_name="Auteur")  # null if the product was deleted and no longer exists
    message = models.TextField(blank=False, verbose_name="Message")
    read = models.BooleanField(verbose_name="Message lu ?", default=False)
    action = models.BooleanField(verbose_name="Action(s) réalisée(s) ?", default=False,
                                 help_text="Si aucune action n'est nécessaire, côcher cette case.")

# mails
class Mail(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=False, verbose_name="Message")
    subject = models.TextField(blank=False, verbose_name="Sujet")
    recipients = models.TextField(blank=False, verbose_name="Destinataires")
    send = models.BooleanField(verbose_name="Message envoyé ?", default=False)

    REFERENT = 'referent'
    RECEIPT = 'receipt'
    KIND_CHOICES = [
        (REFERENT, 'Référent'),
        (RECEIPT, 'Ticket de caisse'),
    ]
    kind = models.CharField(max_length=8, choices=KIND_CHOICES, default=REFERENT)


