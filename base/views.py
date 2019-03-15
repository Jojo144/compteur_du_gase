from collections import defaultdict

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

import django_tables2 as tables
import django_filters
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from .models import *
from .forms import *
from .utils import *


### index

def index(request):
    return render(request, 'base/index.html')

def gestion(request):
    return render(request, 'base/gestion.html')


### achats

def pre_achats(request):
    if request.method == 'POST':
        form = HouseholdForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('base:achats', args=(request.POST['member'],)))
    else:
        form = HouseholdForm()
    return render(request, 'base/pre_achats.html', {'form': form})

def achats(request, member_id):
    context = {'member': Household.objects.get(pk=member_id),
               'cats': Category.objects.all(),
    }
    return render(request, 'base/achats.html', context)


def achats_cat(request, member_id, cat_id):
    cat = Category.objects.get(pk=cat_id)
    pdts = cat.get_products()
    basket = request.session.get('basket', {})
    if request.method == 'POST':
        form = ProductList(pdts, request.POST)
        if form.is_valid():
            for p, q in form.cleaned_data.items():
                if q:
                    incr_key(basket, p, q)
    context = {'member': Household.objects.get(pk=member_id),
               'cats': Category.objects.all(),
               'cat': cat,
               'products': pdts,
               'form': ProductList(pdts),
               'basket': basket}
    request.session['basket'] = basket
    return render(request, 'base/achats_cat.html', context)


def end_achats(request, member_id):
    basket = request.session['basket']
    member = Household.objects.get(pk=member_id)
    s = 0
    for p, q in basket.items():
        pdt = Product.objects.get(pk=p)
        op = AchatOp(product=pdt, member=member, quantity=-q)
        op.save()
        s += op.price
        member.account -= op.price
        member.save()
        pdt.stock -= q
        pdt.save()
    messages.success(request, 'Votre compte a été débité de ' + str(s) + ' €.')
    del request.session['basket']
    return HttpResponseRedirect(reverse('base:index'))


### compte

def pre_compte(request):
    if request.method == 'POST':
        form = HouseholdForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('base:compte', args=(request.POST['household'],)))
    else:
        form = HouseholdForm()
    return render(request, 'base/pre_compte.html', {'form': form})

def compte(request, household_id):
    household = Household.objects.get(pk=household_id)
    if request.method == 'POST':
        form = ApproCompteForm(request.POST)
        if form.is_valid():
            q = form.cleaned_data['amount']
            op = ApproCompteOp(member=household, amount=q)
            op.save()
            household.account += q
            household.save()
            messages.success(request, 'Appro Compte ok!')
            return HttpResponseRedirect(reverse('base:index'))
    else:
        form = ApproCompteForm()
    context = {'household': household,
               'form': form,
    }
    return render(request, 'base/compte.html', context)


### produits

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit créé !')
            return HttpResponseRedirect(reverse('base:products'))
    else:
        form = ProductForm()
    return render(request, 'base/product.html', {'form': form})

def detail_product(request, product_id):
    pdt = Product.objects.get(pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=pdt)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit mis à jour !')
            return HttpResponseRedirect(reverse('base:products'))
    else:
        form = ProductForm(instance=pdt)
    return render(request, 'base/product.html', {'form': form})


class ProductTable(tables.Table):
    link = tables.Column(verbose_name='', empty_values=(),
                         linkify=('base:detail_product',[tables.A('pk')]))

    def render_link(self, value):
        return "Détails"

    def render_price(self, value):
        return "%s €" % value

    def render_stock(self, value):
        if value >= 100:
            return '{0:.0f}'.format(value)
        if value >= 10:
            return '{0:.1f}'.format(value).rstrip('0').rstrip('.')
        if value >= 1:
            return '{0:.2f}'.format(value).rstrip('0').rstrip('.')
        else:
            return '{0:.3f}'.format(value)

    class Meta:
        model = Product
        fields = ['name', 'category', 'provider', 'price', 'pwyw', 'vrac', 'stock']
        # template_name = 'django_tables2/bootstrap.html'


class MyBooleanFilter(django_filters.Filter):
    field_class = forms.BooleanField


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(label='Filtrer le nom', lookup_expr='icontains')
    visible = MyBooleanFilter(label="N'afficher que les visibles", lookup_expr='lt', initial=True, exclude=True)
    class Meta:
        model = Product
        fields = ['name', 'visible']


def products(request):
    f = ProductFilter(request.GET, queryset=Product.objects.order_by('name'))
    table = ProductTable(f.qs)
    tables.RequestConfig(request).configure(table)
    return render(request, 'base/products.html', {'table': table, 'filter': f})


### appro

def pre_appro(request):
    if request.method == 'POST':
        form = ProviderForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('base:appro', args=(request.POST['provider'],)))
    else:
        form = ProviderForm()
    return render(request, 'base/pre_appro.html', {'form': form})

def appro(request, provider_id):
    prod = Provider.objects.get(pk=provider_id)
    if request.method == 'POST':
        form = ApproForm(prod, request.POST)
        if form.is_valid():
            for p, q in form.cleaned_data.items():
                if q:
                    pdt = Product.objects.get(pk=p)
                    op = ApproStockOp(product=pdt, quantity=q)
                    op.save()
                    pdt.stock += q
                    pdt.save()
            messages.success(request, 'Appro ok!')
            return HttpResponseRedirect(reverse('base:index'))
    else:
        form = ApproForm(prod)
    context = {'provider': prod,
               'pdts': prod.get_products(),
               'form': form,
    }
    return render(request, 'base/appro.html', context)





### membres

class MemberTable(tables.Table):
    # foyer = tables.Column(verbose_name='Foyer', empty_values=(),
    #                       accessor=tables.A('pk'),
    #                       linkify=('base:detail_produit',[tables.A('pk')]))

    link = tables.Column(verbose_name='', empty_values=(),
                         linkify=('base:detail_member',[tables.A('pk')]))

    def render_link(self, value):
        return 'Détails'

    class Meta:
        model = Member
        fields = ['name', 'foyer', 'email', 'tel']
        # template_name = 'django_tables2/bootstrap.html'


class MemberFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(label='Filtrer le nom', lookup_expr='icontains')
    class Meta:
        model = Member
        fields = ['name']


def members(request):
    f = MemberFilter(request.GET, queryset=Member.objects.order_by('name'))
    table = MemberTable(f.qs)
    tables.RequestConfig(request).configure(table)
    return render(request, 'base/members.html', {'table': table, 'filter': f})


def detail_member(request, member_id):
    member = Member.objects.get(pk=member_id)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membre mis à jour !')
            return HttpResponseRedirect(reverse('base:members'))
    else:
        form = MemberForm(instance=member)
    return render(request, 'base/member.html', {'form': form})


## inventaire

def inventory(request):
    pdts = Product.objects.all()
    if request.method == 'POST':
        form = ProductList(pdts, request.POST)
        if form.is_valid():
            for p, q in form.cleaned_data.items():
                pdt = Product.objects.get(pk=p)
                if q:
                    diff = q-pdt.stock
                    if diff != 0: # todo check
                        op = InventoryOp(product=pdt, quantity=diff)
                        op.save()
                        pdt.stock = q
                        pdt.save()
            messages.success(request, 'Stock mis à jour !')
            return HttpResponseRedirect(reverse('base:gestion'))
    else:
        form = ProductList(pdts, request.POST)
    return render(request, 'base/inventory.html', {'form': form})

### stats
from jchart import Chart
from jchart.config import Axes, DataSet, rgba

class LineChart(Chart):
    chart_type = 'line'
    scales = {
        'xAxes': [Axes(type='time', position='bottom')],
    }
    def get_datasets(self, product_id):
        # pdt = Product.objects.get(pk=2)
        opes = AchatOp.objects.filter(product=product_id)
        data = [{'y': a.quantity, 'x': a.date.isoformat()[:-13],} for a in opes ]
        print(data)
        return [DataSet(type='line', data=data)]

def stats(request, product_id):
    pdt = Product.objects.get(pk=product_id)
    return render(request, 'base/stats.html', {'pdt': pdt, 'chart': LineChart(),})
