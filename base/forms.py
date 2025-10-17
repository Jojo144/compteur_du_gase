from django import forms
from django.conf import settings
from django.forms import inlineformset_factory, Textarea, BaseFormSet
from django.utils.safestring import mark_safe
from easy_select2.widgets import Select2

from .models import *
from .templatetags.my_tags import *


class HouseholdList(forms.Form):
    household = forms.ModelChoiceField(label='Sélectionnez le compte : ',
                                       widget=Select2(select2attrs=settings.SELECT2_ATTRS),
                                       queryset=Household.objects.all())


class ProviderList(forms.Form):
    provider = forms.ModelChoiceField(label='Sélectionnez un fournisseur : ',
                                      widget=Select2(select2attrs=settings.SELECT2_ATTRS),
                                      queryset=Provider.objects.all())


class ApproCompteForm(forms.Form):
    amount = forms.DecimalField(label="De combien d'argent la cagnotte doit-elle être approvisionnée ?",
                                help_text="♥ Merci de ne pas oublier d'encaisser l'argent !",
                                decimal_places=2)

class ApproCompteFormKind(ApproCompteForm):
    paymenttype = forms.ModelChoiceField(label="Type de paiement",
                                         required=False,
                                         queryset=PaymentType.objects.all(),
                                         help_text="Chèque/espèces/virement pour un approvisionnement normal."
                                                   "Annulation/correction pour corriger une erreur "
                                                   "de saisie (valeur positive ou négative)."
                                                   "Remboursement pour un remboursement ou "
                                                   "lorsque le foyer clotûre sa cagnotte (valeur négative).",
                                         empty_label="(non renseigné)"
                                         )



class ProductList(forms.Form):
    """
    Utilisé pour inventaire
    """
    def __init__(self, pdts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for p in pdts:
            if (get_local_settings().use_cost_of_purchase):
                help_text = "fournisseur : {} <br> prix d'achat : {} € / {} <br> prix de vente : {} € / {} <br> stock actuel théorique : {} {}".format(
                    p.provider, p.cost_of_purchase, p.unit, p.price, p.unit, round_stock(p.stock), p.unit)
            else:
                help_text = "fournisseur : {} <br> prix : {} € / {} <br> stock actuel théorique : {} {}".format(
                    p.provider, p.price, p.unit, round_stock(p.stock), p.unit)
            self.fields[str(p.pk)] = forms.DecimalField(label=p.name, help_text=mark_safe(help_text), required=False)


class ProductApproForm(forms.Form):
    visible = forms.BooleanField(
        label="Visible",
        required=False,
    )
    product = forms.ModelChoiceField(
        label="Produit",
        widget=forms.HiddenInput,
        queryset=Product.objects.all(),
    )
    quantity = forms.DecimalField(
        label="Quantité réceptionnée",
        required=False,
    )
    cost_of_purchase = forms.DecimalField(
        label="Changer le prix d'achat (optionnel)",
        required=False,
        min_value=0,
    )
    price = forms.DecimalField(
        label="Changer le prix de vente (optionnel)",
        required=False,
        min_value=0,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        product = kwargs['initial']['product']

        self.fields['quantity'].help_text = (
            "stock actuel théorique : "
            f"{round_stock(product.stock)} {product.unit}"
        )

        self.fields['cost_of_purchase'].help_text = (
            f"actuel : {product.cost_of_purchase} € / {product.unit}"
        )
        self.fields['cost_of_purchase'].widget.attrs['placeholder'] = (
            "Nouveau prix d'achat"
        )
        self.fields['price'].help_text = (
            f"actuel : {product.price} € / {product.unit}"
        )
        self.fields['price'].widget.attrs['placeholder'] = (
            "Nouveau prix de vente"
        )
        self.fields['visible'].widget.attrs = {"class": "label-hidden"}

        if not get_local_settings().use_cost_of_purchase:
            del self.fields['cost_of_purchase']


class ApproFormSet(BaseFormSet):
    """
    Permet de gérer un tableau de ProductApproForm
    """
    def clean(self):
        if not self.has_changed():
            raise ValidationError("Aucune appro ou modification saisie")


# used for details AND creation
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['activated']
        widgets = { 'comment': Textarea(attrs={'rows': 4}) }


class ProductFormWithoutPurchase(ProductForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not get_local_settings().use_categories:
            self.fields.pop('category')

    class Meta(ProductForm.Meta):
        exclude = ['activated', 'cost_of_purchase']


# used for details AND creation
class ProviderForm(forms.ModelForm):
    class Meta:
        model = Provider
        exclude = []


# used for details AND creation
class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        exclude = []


# used for details AND creation
MemberFormSet = inlineformset_factory(Household, Member, fields=('name', 'email', 'tel', 'receipt', 'stock_alert'),
                                      min_num=1, validate_min=True, extra=0)


class ActivityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['readonly'] = True
        self.fields['date'].widget.attrs['readonly'] = True
    class Meta:
        model = Activity
        exclude = []
        widgets = {
            'comment': Textarea(attrs={'rows': 3}),
            'volunteer1': Select2(select2attrs=settings.SELECT2_ATTRS),
            'volunteer2': Select2(select2attrs=settings.SELECT2_ATTRS),
        }


class ShareAmountForm(forms.Form):
    label = forms.CharField(
        label="Nom de la somme à partager entre tous les foyers",
        max_length=200,
        required=True,
    )
    amount = forms.DecimalField(
        label="Montant de la somme",
        required=True,
    )
    prorata_by_member = forms.BooleanField(
        label="Partager au prorata du nombre de membres de chaque foyer ?",

        help_text="""Si la case est cochée, les foyers comptant plus de membres toucherons
                     une plus grosse somme que ceux avec peu de membres.
                     Sinon, chaque foyer touchera la même somme.""",

        required=False,
    )
