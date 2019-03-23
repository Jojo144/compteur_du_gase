import smtplib, ssl
import json
import decimal, datetime
from collections import defaultdict

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail

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
    # todo : use aggregate ?
    value_stock=sum([p.value() for p in Product.objects.all()])
    value_accounts=sum([p.account for p in Household.objects.all()])
    return render(request, 'base/gestion.html',
                  {'value_stock': round0(value_stock),
                   'value_accounts': round0(value_accounts),
                   'diff_values': round0(value_accounts - value_stock),
                  })


### achats

def pre_achats(request):
    if request.method == 'POST':
        form = HouseholdList(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('base:achats', args=(request.POST['household'],)))
    else:
        form = HouseholdList()
    return render(request, 'base/pre_achats.html', {'form': form})

def achats(request, household_id):
    localsettings = LocalSettings.objects.first()
    if localsettings is None:
        localsettings = LocalSettings.objects.create()

    household = Household.objects.get(pk=household_id)
    if request.method == 'POST':
        s = 0
        msg = "Voici votre ticket de caisse :\n"
        for p, q in request.POST.items():
            if p.startswith('basket_'):
                pdt = Product.objects.get(pk=int(p[7:]))
                q = decimal.Decimal(q)
                op = AchatOp(product=pdt, household=household, quantity=-q)
                op.save()
                household.account -= op.price
                household.save()
                pdt.stock -= q
                pdt.save()
                s += op.price
                msg += "{} ({} € / unité) : {} unité  -> {} €\n".format(pdt.name, pdt.price, q, op.price)
        msg += "Ce qui nous donne un total de {} €.\n\nCiao!".format(s)
        mails = household.get_emails_receipt()
        send_mail('[Compteur de GASE] Ticket de caisse', msg, 'gase.nantest@mailoo.org', mails, fail_silently=False)
        messages.success(request, 'Votre compte a été débité de ' + str(s) + ' €.')
        return HttpResponseRedirect(reverse('base:index'))
    else:
        pdts = {str(p.id): {"name": p.name, "category": p.category.id,
                            "price": str(p.price), "pwyw": p.pwyw, "vrac": p.vrac}
                for p in Product.objects.all()}
        pdts = json.dumps(pdts)
        context = {'household': household,
                   'cats': Category.objects.all(),
                   'max_amount': household.account - localsettings.min_account,
                   'pdts': pdts}
        return render(request, 'base/achats.html', context)


### compte

def pre_compte(request):
    if request.method == 'POST':
        form = HouseholdList(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('base:compte', args=(request.POST['household'],)))
    else:
        form = HouseholdList()
    return render(request, 'base/pre_compte.html', {'form': form})

def compte(request, household_id):
    household = Household.objects.get(pk=household_id)
    history = ApproCompteOp.objects.filter(household_id=household_id).order_by('-date')[:5]
    if request.method == 'POST':
        form = ApproCompteForm(request.POST)
        if form.is_valid():
            q = form.cleaned_data['amount']
            op = ApproCompteOp(household=household, amount=q)
            op.save()
            household.account += q
            household.save()
            messages.success(request, 'Approvisionnement du compte effectué')
            return HttpResponseRedirect(reverse('base:index'))
    else:
        form = ApproCompteForm()
    context = {'household': household,
               'form': form,
               'history': history,
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
        form = ProductForm(instance=pdt, initial={'value': pdt.value()})
    return render(request, 'base/product.html', {'form': form})

def products(request):
    columns = ['nom', 'catégorie', 'fournisseur', 'prix', 'prix libre', 'vrac', 'stock']
    pdts = [{"id": p.id, "nom": p.name, "catégorie": str(p.category), "fournisseur": str(p.provider),
             "prix": '{} €'.format(p.price), "prix libre": p.pwyw, "vrac": p.vrac, "stock": round_stock(p.stock)}
            for p in Product.objects.all()]
    columns = json.dumps(columns)
    pdts = json.dumps(pdts)
    return render(request, 'base/products.html', {'columns': columns, 'pdts': pdts})


### appro

def pre_appro(request):
    if request.method == 'POST':
        form = ProviderList(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('base:appro', args=(request.POST['provider'],)))
    else:
        form = ProviderList()
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
            messages.success(request, 'Approvisionnement effectué')
            return HttpResponseRedirect(reverse('base:index'))
    else:
        form = ApproForm(prod)
    context = {'provider': prod,
               'pdts': prod.get_products(),
               'form': form,
    }
    return render(request, 'base/appro.html', context)


### membres

def members(request):
    columns = ['nom', 'foyer', 'email', 'bigophone']
    members = [{"id": p.id, "nom": p.name, "foyer": str(p.household), "email": p.email, "bigophone": p.tel}
               for p in Member.objects.all()]
    columns = json.dumps(columns)
    members = json.dumps(members)
    return render(request, 'base/members.html', {'columns': columns, 'members': members})


def detail_member(request, member_id):
    member = Member.objects.get(pk=member_id)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membre mis à jour')
            return HttpResponseRedirect(reverse('base:members'))
    else:
        form = MemberForm(instance=member, initial={'address': member.household.address})
    return render(request, 'base/member.html', {'form': form})

### membres

def providers(request):
    columns = ['nom', 'contact', 'commentaire']
    providers = [{"id": p.id, "nom": p.name, "contact": str(p.contact),
                  "commentaire": p.comment}
                 for p in Provider.objects.all()]
    columns = json.dumps(columns)
    providers = json.dumps(providers)
    return render(request, 'base/providers.html', {'columns': columns, 'providers': providers})


def detail_provider(request, provider_id):
    provider = Provider.objects.get(pk=provider_id)
    if request.method == 'POST':
        form = ProviderForm(request.POST, instance=provider)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fournisseur mis à jour')
            return HttpResponseRedirect(reverse('base:providers'))
    else:
        form = ProviderForm(instance=provider)
    return render(request, 'base/provider.html', {'form': form})


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
            return HttpResponseRedirect(reverse('base:ecarts'))
    else:
        form = ProductList(pdts, request.POST)
    return render(request, 'base/inventory.html', {'form': form})

def ecarts(request):
    ope = InventoryOp.objects.all()
    for o in list(ope):
        print(o.date, o.price)
    dates = {o.date.date() for o in ope} # on regroupe par jour
    # dates = list(dates).sort(reverse=True) # on garde les 10 derniers FIXME
    ecarts = [{'date': d,
               'result': round2(sum([o.price for o in ope.filter(date__date=d)]))}
              for d in dates]
    return render(request, 'base/ecarts.html',
                  {'ecarts': ecarts
                  })


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
