from django import forms

from .models import *

class HouseholdForm(forms.Form):
    household = forms.ModelChoiceField(label='Sélectionnez votre compte : ',
                                       queryset=Household.objects.all())

class ProviderForm(forms.Form):
    provider = forms.ModelChoiceField(label='Qui qui ?',
                                      queryset=Provider.objects.all())

class ApproCompteForm(forms.Form):
    amount = forms.DecimalField(label="Combien d'argent avez-vous virez sur le compte du GASE ?", decimal_places=2)

class ApproForm(forms.Form):
    def __init__(self, prod, *args, **kwargs):
        super(ApproForm, self).__init__(*args, **kwargs)
        for p in prod.get_products():
            self.fields[str(p.pk)] = forms.DecimalField(label=p.name, required=False)

class ProductList(forms.Form):
    def __init__(self, pdts, *args, **kwargs):
        super(ProductList, self).__init__(*args, **kwargs)
        for p in pdts:
            self.fields[str(p.pk)] = forms.DecimalField(label=p.name, required=False)

class ProductForm(forms.ModelForm):
    stock = forms.DecimalField(disabled=True, initial=0)

    class Meta:
        model = Product
        exclude = []

class MemberForm(forms.ModelForm):
    account = forms.DecimalField(disabled=True, initial=0)

    class Meta:
        model = Member
        exclude = []
