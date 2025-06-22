from django.db import models
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, get_connection
from django import forms


# there should be only one instance of this model
class LocalSettings(models.Model):
    min_account = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                      verbose_name="seuil en dessous duquel on ne peut plus faire d'achat (en €)")

    min_account_allow = models.BooleanField(
        verbose_name="Lorsque le solde n'est pas suffisant, autoriser quand même après demande de confirmation ?",
        default=False,
        help_text="Lorsque cette option est activée, si le solde n'est pas suffisant, il y a une demande de confirmation "
                  "lors de l'achat mais il est autorisé. Dans le cas contraire, l'achat est rendu impossible.")

    min_balance = models.DecimalField(max_digits=10, decimal_places=2, default=10,
                                      verbose_name="seuil en dessous duquel une alerte est lancée au moment de commencer un achat (en €)")

    txt_home = models.TextField(blank=True, default="<i>Bienvenue au GASE</i><br><br>",
                                verbose_name="texte en haut de la page d'accueil (doit être donnée en code html)")

    txt_home2 = models.TextField(blank=True, default="Infos utiles genre :\nlocalisation des clés du GASE\nhoraires des permanences\n...\n(ou rien)",
                                 verbose_name="texte en base de la page d'accueil (doit être donnée en texte pur et sera centré)")

    activity_board = models.BooleanField(verbose_name="Utiliser le tableau des permanences ?", default=True,
                                         help_text="Le tableau des permanences permet de gérer l'inscription des membres pour tenir "
                                                   "les permanences. Il s'affiche sur la page d'accueil.")

    use_messages = models.BooleanField(verbose_name="Utilisation de la fonction messages/actions ?", default=False,
                                       help_text="La fonction messages/actions sert à laisser des messages "
                                                 "entre les différentes permanences ou lister des actions à faire.")

    use_paymenttype = models.BooleanField(verbose_name="Utilisation de la fonction type de paiement ?", default=False,
                                         help_text="La fonction type de paiement permet de sauvegarder le moyen "
                                                   "de paiement utilisé.")

    use_subscription = models.BooleanField(verbose_name="Utilisation de la fonction cotisation d'adhésion ?",
                                           default=False,
                                           help_text="La fonction adhésion permet de renseigner la cotisation "
                                                     "d'adhésion du foyer.")

    use_cost_of_purchase = models.BooleanField(verbose_name="Utilisation de la fonction prix d'achat ?", default=False,
                                               help_text="La fonction prix d'achat permet de spécifier un prix d'achat "
                                                         "différent du prix de vente.")

    use_exports = models.BooleanField(verbose_name="Utiliser les exports ?", default=False,
                                      help_text="Exports de l'historique d'achat et de la liste des produits.")

    use_logo = models.BooleanField(verbose_name="Affiche le logo dans la première page ?", default=False,
                                   help_text="Le fichier de logo doit être placé dans le répertoire base/static/base"
                                             " et son nom de fichier doit etre logo.png.")

    use_categories = models.BooleanField(verbose_name="Utilise les catégories de produits",
                                         help_text="Si désactivé, les catégories ne seront pas proposées dans le formulaire et dans les listings.", default=True)

    use_mail = models.BooleanField(verbose_name="Utilisation de la fonction envoi d'email ?", default=True,
                                   help_text="Cette fonction permet d'envoyer les tickets de caisse ou "
                                             "des alertes stocks aux référents des produits.")

    prefix_object_mail = models.CharField(blank=True, verbose_name="Préfixe dans l'objet des emails.", default="",
                                          max_length=15,
                                          help_text="Un préfixe est souvent encadré par des crochers, exemples : [GASE].")

    debug_mail = models.CharField(blank=True,
                                  verbose_name="Si ce champ est renseigné, tous les emails lui seront envoyés.",
                                  default="", max_length=50,
                                  help_text="Ce champ permet de tester la fonction email "
                                            "sans envoyer de mails intempestifs.")

    mail_host = models.CharField(blank=False, verbose_name="Serveur pour l'envoi des mails. « localhost » pour utiliser le serveur du compteur comme serveur d'envoi.",
                                 default="localhost", max_length=50,
                                 help_text="Exemple : smtp.titi.com.")

    mail_port = models.IntegerField(verbose_name="Port smtp pour l'envoi des mails.",
                                    default=25,
                                    help_text="Exemple : 25 (sans chiffrement), "
                                              "465 (chiffrement implicite, SSL), "
                                              "587 (chiffrement explicite, TLS).")

    mail_protocole = models.CharField(
        choices=[('no', 'Pas de chiffrement'), ('tls', 'Utiliser TLS'), ('ssl', 'Utiliser SSL')],
        verbose_name="Chiffrement utilisé pour l'envoi de mails.",
        default="no", max_length=100)

    mail_timeout = models.IntegerField(default=4, verbose_name="Timeout pour l'envoi de mail.")

    mail_from = models.CharField(blank=True, verbose_name="Expéditeur pour l'envoi des mails.",
                                     default="tata@example.com", max_length=100,
                                     help_text="Exemple : tata@titi.com.")

    mail_username = models.CharField(blank=True, verbose_name="Nom d'utilisateur pour l'envoi des mails.",
                                     default="", max_length=100,
                                     help_text="Utilisateur SMTP, exemple : tata. Si vide : n'utilisera pas d'authentification")

    mail_passwd = models.CharField(blank=True, verbose_name="Mot de passe pour l'envoi des mails.",
                                   default="", max_length=100,
                                   help_text="Mot de passe SMTP. Si vide : n'utilisera pas d'authentification")

    def __str__(self):
        return "Réglages divers"

    class Meta:
        verbose_name = "Réglages divers"
        verbose_name_plural = "Réglages divers"


def get_local_settings() -> LocalSettings:
    return LocalSettings.objects.first()

class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom")

    def __str__(self):
        return self.name

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
        ordering = ["name"]


class Provider(models.Model):
    name = models.CharField(max_length=200, verbose_name="nom")
    contact = models.TextField(blank=True, verbose_name="mail / téléphone / adresse du fournisseur")
    comment = models.TextField(blank=True,
                               verbose_name="commentaire (quel Gasier a été en contact, historique des échanges, ...)")

    def __str__(self):
        return self.name

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
    return  # cette verification empeche de modifier un foyer, a corriger
    if value in [getattr(p, 'number') for p in Household.objects.all()]:
        advised_value = get_advised_household_number()
        raise ValidationError(
            "Le numéro d'adhérent {0:d} est déjà utilisé ! Le numéro conseillé est le {1:d}.".format(value,
                                                                                                     advised_value))


class ActivatedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(activated=True)

class Household(models.Model):
    name = models.CharField(max_length=200,
                            help_text="Nom qui apparaitra dans la liste des foyers pour faire ses achats.",
                            verbose_name="nom du foyer")
    number = models.IntegerField(default=0, verbose_name="numero d'adhérent", validators=[validate_household_number])
    address = models.CharField(max_length=200, blank=True,
                               help_text="Pas indispensable mais pratique quand on fait des réunions "
                                         "chez les uns les autres.",
                               verbose_name="adresse")
    comment = models.TextField(blank=True, verbose_name="commentaire")
    account = models.DecimalField(default=0, max_digits=10, decimal_places=2, editable=False,
                                  verbose_name="solde de la cagnotte")  # INVARIANT : account should be sum of operations
    date = models.DateField(auto_now_add=True)  # date d'inscription
    date_closed = models.DateField(blank=True, null=True, verbose_name="Date de clôture",
                                   help_text="Remplir seulement si le foyer souhaite arrêter.")  # date de cloture
    subscription = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="cotisation",
                                       help_text="Montant de la cotisation d'adhésion (en €)")

    on_the_flight = models.BooleanField(
        verbose_name="Paie à la volée", default=False,
        help_text="Réalise un approvisionnement automatique du montant du panier avant de payer."
                  "Cette fonction peut être utilise si l'on autorise le payement à la volée, c'est-à-dire lorsque "
                  "le client n'a pas besoin d'approvisionner sa cagnotte mais paye la juste somme.")

    activated = models.BooleanField(default=True,
                                    help_text="Un foyer non activé n'apparaît pas dans le logiciel. Utilisé pour archiver les foyers et ses membres",
                                    verbose_name="activé")

    objects = ActivatedManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.name

    def get_members(self):
        return Member.objects.filter(household=self.pk)

    def get_emails_receipt(self):
        return self.get_members().filter(receipt=True)

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


class MemberManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(household__activated=True)

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

    objects = MemberManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Membre'
        ordering = ['name']


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="nom")
    provider = models.ForeignKey(Provider, verbose_name="fournisseur", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, verbose_name="catégorie", on_delete=models.SET_NULL, null=True)
    unit = models.ForeignKey(Unit, verbose_name="unité", on_delete=models.CASCADE)
    # current price, can vary in the time ...
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="prix de vente",
                                help_text="Prix de vente (en €) à l'unité (kg/L/...)")
    # current price, can vary in the time ...
    cost_of_purchase = models.DecimalField(default=0.0, max_digits=10, decimal_places=2, verbose_name="prix d'achat",
                                           help_text="Prix d'achat (en €) à l'unité (kg/L/...)")
    pwyw = models.BooleanField(default=False, verbose_name="prix libre",
                               help_text="Une référence à prix libre peut être achetée au prix que le consommateur le souhaite."
                                         " Dans ce cas, indiquer un prix indicatif ou 0 dans le Prix de vente.")  # PWYW = Pay what you want
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
    activated = models.BooleanField(default=True,
                                    help_text="Une référence non activée n'apparaît pas dans le logiciel. Utilisé pour archiver les produits",
                                    verbose_name="activé")

    objects = ActivatedManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.name

    def value_stock(self):
        return self.price * self.stock

    def value_purchase(self):
        return self.cost_of_purchase * self.stock

    def get_email_stock_alert(self):
        if self.referent and self.referent.stock_alert and self.referent.email != '':
            return [self.referent]
        else:
            return []

    class Meta:
        verbose_name = 'Produit'
        ordering = ['name']


class Operation(models.Model):
    # en dépit du nom, c'est un datetime:
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        abstract = True


class ChangeStockOpQuerySet(models.QuerySet):
    def appros_only(self):
        return self.filter(label=ChangeStockOp.TYPE_APPRO_STOCK)

    def inventories_only(self):
        return self.filter(label=ChangeStockOp.TYPE_INVENTORY)

    def purchases_only(self):
        # via cette méthode, on accèdera pas à l'attribut de la classe spécifique (household)
        return self.filter(label=ChangeStockOp.TYPE_PURCHASE)


class ChangeStockOp(Operation):
    TYPE_APPRO_STOCK = "ApproStock"
    TYPE_INVENTORY = "Inventaire"
    TYPE_PURCHASE = "Achat"

    product = models.ForeignKey(Product, null=True,
                                on_delete=models.SET_NULL)  # null if the product was deleted and no longer exists
    quantity = models.DecimalField(max_digits=15,
                                   decimal_places=3)  # positif for an appro, negative for a normal buying
    price = models.DecimalField(max_digits=15, decimal_places=3)  # product.price * quantity // decimal_places should have been set to 2...
    purchase_cost = models.DecimalField(max_digits=15, decimal_places=3,
                                        default=0)  # product.cost_of_purchase * quantity // decimal_places should have been set to 2...
    stock = models.DecimalField(max_digits=15, decimal_places=3)  # stock after the operation
    label = models.CharField(max_length=20)

    objects = ChangeStockOpQuerySet.as_manager()

    @classmethod  # constructor computing price and cost_of_purchase
    def create(cls, product=product, quantity=quantity, pwyw=None, **kwargs):
        price = pwyw if (pwyw is not None) else (product.price * quantity)
        purchase_cost = product.cost_of_purchase * quantity
        newstock = product.stock + quantity
        return cls.objects.create(product=product, quantity=quantity, price=price, purchase_cost=purchase_cost, stock=newstock, **kwargs)

    @classmethod
    def create_appro_stock(cls, **kwargs):
        return cls.create(label=cls.TYPE_APPRO_STOCK, **kwargs)

    @classmethod
    def create_inventory(cls, **kwargs):
        return cls.create(label=cls.TYPE_INVENTORY, **kwargs)

    def cost_of_purchase(self):
        if self.label != self.TYPE_APPRO_STOCK:
            raise TypeError("Operation must be filter with label==ApproStock")
        return self.purchase_cost

    def cost_of_price(self):
        if self.label != self.TYPE_APPRO_STOCK:
            raise TypeError("Operation must be filter with label==ApproStock")
        return self.price

    def __str__(self):
        return '{} : {} - {}'.format(self.label, self.product, self.quantity)

    class Meta:
        verbose_name = 'Opération sur le stock'


class Purchase(Operation):
    household = models.ForeignKey(Household, null=True,
                                  on_delete=models.SET_NULL)  # null if the household was deleted and no longer exists


class PurchaseDetailOp(ChangeStockOp):
    purchase = models.ForeignKey(Purchase, null=False, on_delete=models.CASCADE)

    @classmethod
    def create(cls, **kwargs):
        op = super().create(label=cls.TYPE_PURCHASE, **kwargs)
        price = round(op.price, 2)  # arrondi au centime près
        purchase_cost = round(op.purchase_cost, 2)
        op.save() # needed?
        return op


class PaymentType(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Type de paiement'
        ordering = ['name']


class ApproCompteOp(Operation):
    household = models.ForeignKey(Household, null=True,
                                  on_delete=models.SET_NULL, verbose_name="Foyer")  # null if the household was deleted and no longer exists
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Montant")  # positif for a regular appro
    paymenttype = models.ForeignKey(PaymentType, null=True,
                                    on_delete=models.SET_NULL, verbose_name="Type de paiement")

    def get_paymenttype_display(self):
        if self.paymenttype:
            return self.paymenttype.name
        else:
            return "(non renseigné)"

    def __str__(self):
        return 'ApproCompteOp {} - {} - {}'.format(self.household, self.amount, self.paymenttype)

    class Meta:
        verbose_name = "Opération d'appro de cagnotte"
        verbose_name_plural = "Opérations d'appro de cagnotte"


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
    recipients = models.ManyToManyField(Member, verbose_name="Destinataires")
    sent = models.BooleanField(verbose_name="Message envoyé ?", default=False)

    APPRO_CAGNOTTE, TICKET, ALERTE_STOCK, APPRO_STOCK, NOTIFICATION = 'appro_cagnotte', 'ticket', 'alerte_stock', 'appro_stock', 'notification'
    KIND_CHOICES = [
        (APPRO_CAGNOTTE, 'approvisionnement de la cagnotte'),
        (TICKET, 'ticket de caisse'),
        (ALERTE_STOCK, 'alerte stock'),
        (APPRO_STOCK, 'approvisionnement stock'),
        (NOTIFICATION, 'notification')
    ]
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default='notification')

    def success_msg(self):
        if self.kind == self.APPRO_CAGNOTTE:
            return "La notification d'approvisionnement a bien été envoyée"
        elif self.kind == self.TICKET:
            return "Le ticket de caisse a bien été envoyé"
        elif self.kind == self.ALERTE_STOCK:
            return "L'alerte stock a bien été envoyée"
        elif self.kind == self.APPRO_STOCK:
            return "La notification d'approvisionnement a bien été envoyée"
        else:
            return "La notification a bien été envoyée"

    def error_msg(self):
        if self.kind == self.APPRO_CAGNOTTE:
            return "La notification d'approvisionnement n'a pas été envoyée"
        elif self.kind == self.TICKET:
            return "Le ticket de caisse n'a pas été envoyé"
        elif self.kind == self.ALERTE_STOCK:
            return "L'alerte stock n'a pas été envoyée"
        elif self.kind == self.APPRO_STOCK:
            return "La notification d'approvisionnement n'a pas été envoyée"
        else:
            return "La notification n'a pas été envoyée"

    def recipient_list(self):
        return [m.email for m in self.recipients.all()]

    def send(self, local_settings):
        debug_mail = local_settings.debug_mail
        if debug_mail:
            print("* Mode de test pour les mails qui sont automatiquement envoyés à {}.".format(debug_mail))
            recipient_list = [debug_mail]
        else:
            recipient_list = self.recipient_list()

        try:
            with get_connection(host=local_settings.mail_host,
                                port=local_settings.mail_port,
                                username=local_settings.mail_username,
                                password=local_settings.mail_passwd,
                                use_tls=(local_settings.mail_protocole == 'tls'),
                                use_ssl=(local_settings.mail_protocole == 'ssl'),
                                timeout=local_settings.mail_timeout) as connection:
                send_mail(self.subject, self.message, local_settings.mail_from, recipient_list,
                          fail_silently=False, connection=connection)
                self.sent = True
                self.save()
            return True
        except Exception as e:
            # todo better error reporting
            print("Erreur lors de l'envoi du mail : {}".format(e))
            return False


# activité/permanence pour le tableau des permanences
class Activity(models.Model):
    class Meta:
        verbose_name = "Activité"
        ordering = ['-date']

    description = models.CharField(max_length=200)
    date = models.DateField()
    volunteer1 = models.ForeignKey(Member, null=True, blank=True, verbose_name='Permanencier 1', on_delete=models.SET_NULL, related_name='volunteer1')
    volunteer2 = models.ForeignKey(Member, null=True, blank=True, verbose_name='Permanencier 2', on_delete=models.SET_NULL, related_name='volunteer2')
    comment = models.TextField(verbose_name='Commentaire', max_length=1000, blank=True)

    @property
    def volunteers(self):
        return [self.volunteer1, self.volunteer2]

    def __str__(self):
        return self.description
