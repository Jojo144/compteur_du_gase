from django import forms
from django.forms import inlineformset_factory, ValidationError

from .models import *
from .templatetags.my_tags import *


class HouseholdList(forms.Form):
    household = forms.ModelChoiceField(label='Sélectionnez votre compte : ',
                                       queryset=Household.objects.order_by('name'))


class ProviderList(forms.Form):
    provider = forms.ModelChoiceField(label='Sélectionnez un fournisseur : ',
                                      queryset=Provider.objects.order_by('name'))


class ApproCompteForm(forms.Form):
    amount = forms.DecimalField(label="Combien d'argent avez-vous viré sur le compte bancaire du GASE ?", help_text="♥ Merci d'approvisionner votre compte <strong>après</strong> avoir réalisé le virement (ou alors de ne vraiment pas oublier !).", decimal_places=2)


# utilisé pour inventaire ET appro stock
class ProductList(forms.Form):
    def __init__(self, pdts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for p in pdts:
            help_text = "{} € / {}, stock actuel théorique : {} {}".format(p.price, p.unit, round_stock(p.stock), p.unit)
            self.fields[str(p.pk)] = forms.DecimalField(label=p.name, help_text=help_text, required=False)


# used for details AND creation
class ProductForm(forms.ModelForm):
    stock = forms.DecimalField(disabled=True, required=False)
    value = forms.DecimalField(disabled=True, required=False, decimal_places=2,
                               label="Valeur du stock (en €)")
    class Meta:
        model = Product
        exclude = []


# used for details AND creation
class ProviderForm(forms.ModelForm):
    class Meta:
        model = Provider
        exclude = []


# used for details AND creation
MemberFormSet = inlineformset_factory(Household, Member, fields=('name', 'email', 'tel', 'receipt', 'stock_alert'),
                                      min_num=1, validate_min=True, extra = 0)
