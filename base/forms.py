from django import forms
from django.conf import settings
from django.forms import inlineformset_factory, Textarea
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
    kind = forms.ChoiceField(label="Type d'approvisionnement", choices=ApproCompteOp.KIND_CHOICES,
                             help_text="Chèque ou espèces pour un approvisionnement normal (valeur positive)."
                                       "</br>Annulation/correction pour corriger une erreur "
                                       "de saisie (valeur positive ou négative)."
                                       "</br>Remboursement pour un remboursement ou "
                                       "lorsque le foyer clotûre sa cagnotte (valeur négative).")



# utilisé pour inventaire ET appro stock
class ProductList(forms.Form):
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
