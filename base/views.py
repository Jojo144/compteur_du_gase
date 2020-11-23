import json
from datetime import date
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic.edit import CreateView, UpdateView
from django.db import transaction
from django.db.models import Q, Sum

from .models import *
from .forms import *
from .templatetags.my_tags import *



def my_send_mail(request, subject, message, recipients, kind):
    local_settings = get_local_settings()
    if (local_settings.use_mail and recipients):
        subject = ' '.join([local_settings.prefix_object_mail, subject])
        mail = Mail(subject=subject, message=message, kind=kind)
        mail.save()
        mail.recipients.set(recipients)
        if mail.send(local_settings):
            messages.success(request, '✔ ' + mail.success_msg())
        else:
            messages.error(request, '✘ ' + mail.error_msg())
    else:
        pass


# ----------------------------------------------------------------------------------------------------------------------
# index
# ----------------------------------------------------------------------------------------------------------------------

def index(request):
    local_settings = get_local_settings()

    note_not_read = len([p for p in Note.objects.all() if not p.read])
    if note_not_read > 1:
        note_pluralize = "s"
    else:
        note_pluralize = ""

    action_not_done = len([p for p in Note.objects.all() if not p.action])
    if action_not_done > 1:
        action_pluralize = "s"
    else:
        action_pluralize = ""

    txt_message = "Il y a actuellement {0:d} message{1:s} non lu{1:s} et {2:d} action{3:s} non réalisée{3:s}.".format(
        note_not_read, note_pluralize, action_not_done, action_pluralize)

    activity_list = Activity.objects.filter(date__gte=date.today()).order_by('date')

    return render(request, 'base/index.html',
                  {'txt_home': local_settings.txt_home,
                   'txt_home2': local_settings.txt_home2,
                   'txt_message': txt_message,
                   'activity_board': local_settings.activity_board,
                   'activity_list': activity_list,
                   'use_logo': local_settings.use_logo})


def gestion(request):
    local_settings = get_local_settings()
    # todo : use aggregate ?
    value_stock = sum([p.value_stock() for p in Product.objects.all()])
    value_accounts = sum([p.account for p in Household.objects.all()])
    alert_pdts = [p for p in Product.objects.filter(stock_alert__isnull=False, visible=True) if
                  p.stock < p.stock_alert]
    return render(request, 'base/gestion.html',
                  {'value_stock': value_stock,
                   'value_accounts': value_accounts,
                   'diff_values': value_accounts - value_stock,
                   'alert_pdts': alert_pdts,
                   'use_subscriptions': local_settings.use_subscription,
                   })


def otherstats(request):
    value_appro = sum([p.amount for p in ApproCompteOp.objects.all()])
    if get_local_settings().use_cost_of_purchase:
        value_purchase = sum([p.cost_of_purchase() for p in ChangeStockOp.objects.filter(label="ApproStock")])
    else:
        value_purchase = sum([p.cost_of_price() for p in ChangeStockOp.objects.filter(label="ApproStock")])

    value_purchase_household = -sum([p.price for p in PurchaseDetailOp.objects.all()])

    return render(request, 'base/other_stats.html',
                  {'value_appro': value_appro,
                   'value_purchase': value_purchase,
                   'value_purchase_household': value_purchase_household
                   })


# ----------------------------------------------------------------------------------------------------------------------
# achats
# ----------------------------------------------------------------------------------------------------------------------

def pre_achats(request):
    if request.method == 'POST':
        form = HouseholdList(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('base:achats', args=(request.POST['household'],)))
    else:
        form = HouseholdList()
    return render(request, 'base/pre_achats.html', {'form': form})


def achats(request, household_id):
    household = Household.objects.get(pk=household_id)
    if request.method == 'POST':
        s = 0
        msg = "Voici votre ticket de caisse :\n"
        purchase = Purchase(household=household)
        purchase.save()
        for p, q in request.POST.items():
            if p.startswith('basket_qtity_'):
                pdt = Product.objects.get(pk=int(p[13:]))
                q = Decimal(q)
                pwyw = -Decimal(request.POST['basket_price_' + p[13:]]) if pdt.pwyw else None
                op = PurchaseDetailOp.create(product=pdt, purchase=purchase, quantity=-q, pwyw=pwyw)
                op.save()
                household.account += op.price
                household.save()
                pdt.stock -= q
                pdt.save()
                s -= op.price
                msg += "{} ({} € / unité) : {} unité  -> {} €\n".format(pdt.name, pdt.price, q, op.price)
                if pdt.stock_alert and pdt.stock <= pdt.stock_alert:
                    my_send_mail(request, subject='Alerte de stock : {}'.format(pdt),
                                 message='Le stock de {} est bas : il reste {} unités'.format(pdt, pdt.stock),
                                 recipients=pdt.get_email_stock_alert(),
                                 kind=Mail.ALERTE_STOCK)
        if household.on_the_flight:
            opa = ApproCompteOp(household=household, amount=s, kind=ApproCompteOp.ONTHEFLIGHT)
            opa.save()
            household.account += s
            household.save()
            messages.success(request, '✔ Approvisionnement de la cagnotte de {0:.2f} € effectué'.format(s))

        msg += "Ce qui nous donne un total de {} €.\n\nCiao!".format(s)
        balance = household.account
        messages.success(request, '✔ Votre cagnotte a été débitée de {} €<br>Solde restant : {} €'.format(round2(s),
                                                                                                       round2(balance)))
        my_send_mail(request, subject='Ticket de caisse', message=msg, recipients=household.get_emails_receipt(), kind=Mail.TICKET)
        return HttpResponseRedirect(reverse('base:index'))
    else:
        local_settings = get_local_settings()
        purchases_history = Purchase.objects.filter(household_id=household_id).order_by('-date')[:10]
        history = [{'date': p.date, 'details': PurchaseDetailOp.objects.filter(purchase=p),
                    'total': '{0:.2f} €'.format(sum([-q.price for q in PurchaseDetailOp.objects.filter(purchase=p)]))}
                   for p in purchases_history]
        pdts = {str(p.id): {"name": p.name, "category": p.category.name, "pwyw": p.pwyw,
                            "price": str(p.price), "unit": p.unit.plural_name(), "vrac": p.unit.vrac}
                for p in Product.objects.filter(visible=True)}
        pdts = json.dumps(pdts)
        balance = household.account
        alerte_balance_amount = local_settings.min_balance

        context = {'household': household,
                   'cats': Category.objects.all(),
                   'max_amount': household.account - local_settings.min_account,
                   'balance_amount': balance,
                   'pdts': pdts,
                   'history': history,
                   'use_exports': local_settings.use_exports,
                   'alerte_balance': balance < alerte_balance_amount,
                   'alerte_balance_amount': '{0:.2f}'.format(alerte_balance_amount),
                   'on_the_flight': household.on_the_flight,
                   'min_account_allow': local_settings.min_account_allow}

        return render(request, 'base/achats.html', context)


# ----------------------------------------------------------------------------------------------------------------------
# compte
# ----------------------------------------------------------------------------------------------------------------------

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
    local_settings = get_local_settings()
    use_appro_kind = local_settings.use_appro_kind
    if request.method == 'POST':
        form = ApproCompteFormKind(request.POST) if use_appro_kind else ApproCompteForm(request.POST)
        if form.is_valid():
            q = form.cleaned_data['amount']
            k = form.cleaned_data.get('kind')  # None if kinds are not used
            op = ApproCompteOp(household=household, amount=q, kind=k)
            op.save()
            household.account += q
            household.save()
            messages.success(request, '✔ Approvisionnement de la cagnotte de {0:.2f} € effectué'.format(q))
            my_send_mail(request, subject="Approvisionnement de votre cagnotte",
                         message='Votre cagnotte a été approvisionnée de {} €'.format(q),
                         recipients=household.get_emails_receipt(), kind=Mail.APPRO_CAGNOTTE)
            return HttpResponseRedirect(reverse('base:index'))
    else:
        form = ApproCompteFormKind() if use_appro_kind else ApproCompteForm()
    context = {'household': household,
               'form': form,
               'history': history,
               'use_subscription': local_settings.use_subscription,
               'number': household.get_formated_number()
               }
    return render(request, 'base/compte.html', context)


def compteslist(request):
    columns = ['jour', 'mois', 'année', 'foyer', 'approvisionnement']
    if get_local_settings().use_appro_kind:
        columns.append("type")
    comptes = [{"jour": p.date.day, "mois": p.date.month, "année": p.date.year, "foyer": str(p.household),
                "approvisionnement": '{} €'.format(p.amount), "type": p.get_kind_display(), "date": p.date.isoformat()}
               for p in ApproCompteOp.objects.all()]
    columns = json.dumps(columns)
    comptes = json.dumps(comptes)
    comptes_stats = get_comptes_stats()
    return render(request, 'base/compteslist.html',
                  {'columns': columns, 'comptes': comptes, 'comptes_stats': comptes_stats})


def get_comptes_stats():
    # dates
    dates = [date.today()]
    for a in ApproCompteOp.objects.all():
        if a.date.date() not in dates:
            dates.append(a.date.date())

    dates.sort()

    # value
    values = [0] * len(dates)
    labels = [0] * len(dates)
    for a in ApproCompteOp.objects.all():
        for ii, i in enumerate(range(dates.index(a.date.date()), len(dates))):
            values[i] += a.amount
            if ii == 0:
                labels[i] += a.amount

    # stats
    comptes_stats = [{'value': '{0:.2f}'.format(values[i]), 'date': dates[i].isoformat(),
                      'label': 'Évolution : {0:.2f} €'.format(labels[i])}
                     for i in range(len(dates))]

    return comptes_stats


def subscriptionslist(request):
    columns = ['jour', 'mois', 'année', 'foyer', 'adhesion']
    subscriptions = [{"jour": p.date.day, "mois": p.date.month, "année": p.date.year, "foyer": str(p),
                      "adhesion": '{} €'.format(p.subscription)}
                     for p in Household.objects.all()]
    columns = json.dumps(columns)
    subscriptions = json.dumps(subscriptions)
    return render(request, 'base/subscriptionslist.html', {'columns': columns, 'subscriptions': subscriptions})


# ----------------------------------------------------------------------------------------------------------------------
# produits
# ----------------------------------------------------------------------------------------------------------------------

def create_product(request):
    if request.method == 'POST':
        if get_local_settings().use_cost_of_purchase:
            form = ProductForm(request.POST)
        else:
            form = ProductFormWithoutPurchase(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✔ Produit créé !')
            return HttpResponseRedirect(reverse('base:products'))
    else:
        if get_local_settings().use_cost_of_purchase:
            form = ProductForm()
        else:
            form = ProductFormWithoutPurchase()
    return render(request, 'base/create_product.html', {'form': form})


def detail_product(request, product_id):
    pdt = Product.objects.get(pk=product_id)
    if request.method == 'POST':
        if get_local_settings().use_cost_of_purchase:
            form = ProductForm(request.POST, instance=pdt)
        else:
            form = ProductFormWithoutPurchase(request.POST, instance=pdt)
        if form.is_valid():
            form.save()
            messages.success(request, '✔ Produit mis à jour !')
            return HttpResponseRedirect(reverse('base:products'))
    else:
        if get_local_settings().use_cost_of_purchase:
            form = ProductForm(instance=pdt)
        else:
            form = ProductFormWithoutPurchase(instance=pdt)
    return render(request, 'base/detail_product.html', {'pdt': pdt, 'stock_value': pdt.value_stock(), 'form': form})

def archive_product(request, product_id):
    pdt = Product.objects.get(pk=product_id)
    pdt.activated = False
    pdt.save()
    messages.success(request, '✔ {} archivé !'.format(pdt.name))
    return HttpResponseRedirect(reverse('base:products'))

def product_history(request, product_id):
    operations = [{"label": str(p.label), "date": str(p.date), "quantity": str(p.quantity), "price": str(p.price)}
                  for p in ChangeStockOp.objects.filter(product_id=product_id).order_by('-date')]
    operations = json.dumps(operations)
    pdt = Product.objects.get(id=product_id)
    plural_unit = pdt.unit.plural_name()
    return render(request, 'base/product_history.html', {'operations': operations, 'pdt': pdt, 'unit': plural_unit})


def products(request):
    local_settings = get_local_settings()
    if local_settings.use_cost_of_purchase:
        columns = ['nom', 'catégorie', 'fournisseur', "prix d'achat", 'prix de vente', 'vrac', 'visible',
                   'alerte stock', 'stock']
    else:
        columns = ['nom', 'catégorie', 'fournisseur', 'prix', 'vrac', 'visible', 'alerte stock', 'stock']
    pdts = [{"id": p.id, "nom": p.name, "catégorie": str(p.category), "fournisseur": str(p.provider),
             "prix d'achat": '{} € / {}'.format(p.cost_of_purchase, p.unit.name),
             "prix de vente": '{} € / {}'.format(p.price, p.unit.name), "prix": '{} € / {}'.format(p.price, p.unit.name),
             "visible": bool_to_utf8(p.visible), "vrac": bool_to_utf8(p.unit.vrac),
             "alerte stock": '{} [{}]'.format(bool_to_utf8(p.stock < p.stock_alert), round_stock(p.stock_alert)) if (p.stock_alert) else '',
             "stock": round_stock(p.stock)}
            for p in Product.objects.all()]
    columns = json.dumps(columns)
    pdts = json.dumps(pdts)
    return render(request, 'base/products.html', {'columns': columns,
                                                  'pdts': pdts,
                                                  'use_exports': local_settings.use_exports})


# ----------------------------------------------------------------------------------------------------------------------
# appro
# ----------------------------------------------------------------------------------------------------------------------

def pre_appro(request):
    if request.method == 'POST':
        form = ProviderList(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('base:appro', args=(request.POST['provider'],)))
    else:
        form = ProviderList()
    return render(request, 'base/pre_appro.html', {'form': form})


def appro(request, provider_id):
    prov = Provider.objects.get(pk=provider_id)
    pdts = Product.objects.filter(provider=prov, visible=True)
    if request.method == 'POST':
        form = ProductList(pdts, request.POST)
        if form.is_valid():
            msgs = {}
            for p, q in form.cleaned_data.items():
                if q:
                    pdt = Product.objects.get(pk=p)
                    op = ChangeStockOp.create_appro_stock(product=pdt, quantity=q)
                    op.save()
                    pdt.stock += q
                    pdt.save()
                    for ref in pdt.get_email_stock_alert():
                        msgs[ref] = msgs.get(ref, '') + '{} a été approvisionné de {} unités\n'.format(pdt, q)
            messages.success(request, '✔ Approvisionnement effectué')
            for (key, value) in msgs.items():
                my_send_mail(request, subject='Approvisionnement : {}'.format(prov), message=value, recipients=[key], kind=Mail.APPRO_STOCK)
            return HttpResponseRedirect(reverse('base:index'))
    else:
        form = ProductList(pdts)
    context = {'provider': prov,
               'form': form,
               }
    return render(request, 'base/appro.html', context)


def approslist(request):
    use_cost_of_purchase = get_local_settings().use_cost_of_purchase
    columns = ['jour', 'mois', 'année', 'fournisseur', 'produit', "coût total (prix de vente)"]
    if use_cost_of_purchase:
        columns.append("coût total (prix d'achat)")
    appros = [{"jour": p.date.day, "mois": p.date.month, "année": p.date.year, "fournisseur": str(p.product.provider),
               "produit": str(p.product), "coût total (prix d'achat)": '{0:.2f} €'.format(p.cost_of_purchase()),
               "coût total (prix de vente)": '{0:.2f} €'.format(p.cost_of_price()),
               "date": p.date.isoformat()}
              for p in ChangeStockOp.objects.filter(label="ApproStock")]
    columns = json.dumps(columns)
    appros = json.dumps(appros)
    appros_stats = get_appros_stats()
    return render(request, 'base/approslist.html',
                  {'columns': columns, 'appros': appros, 'use_cost_of_purchase': use_cost_of_purchase,
                   'appros_stats': appros_stats})


def get_appros_stats():
    purchase = get_local_settings().use_cost_of_purchase

    # dates
    dates = [date.today()]
    for p in ChangeStockOp.objects.filter(label="ApproStock"):
        if p.date.date() not in dates:
            dates.append(p.date.date())

    dates.sort()

    # value
    values = [0] * len(dates)
    labels = [0] * len(dates)
    for p in ChangeStockOp.objects.filter(label="ApproStock"):
        for ii, i in enumerate(range(dates.index(p.date.date()), len(dates))):
            if purchase:
                value = p.cost_of_purchase()
            else:
                value = p.cost_of_price()
            values[i] += value
            if ii == 0:
                labels[i] += value

    # stats
    comptes_stats = [{'value': '{0:.2f}'.format(values[i]), 'date': dates[i].isoformat(),
                      'label': 'Évolution : {0:.2f} €'.format(labels[i])}
                     for i in range(len(dates))]

    return comptes_stats


# ----------------------------------------------------------------------------------------------------------------------
# stock
# ----------------------------------------------------------------------------------------------------------------------

def stockslist(request):
    columns = ['fournisseur', 'catégorie', 'produit', 'valeur totale']
    stocks = [{"fournisseur": str(p.provider), "catégorie": str(p.category), "produit": str(p),
               "valeur totale": '{0:.2f} €'.format(p.value_stock())}
              for p in Product.objects.all()]
    columns = json.dumps(columns)
    stocks = json.dumps(stocks)
    return render(request, 'base/stockslist.html', {'columns': columns, 'stocks': stocks})


# ----------------------------------------------------------------------------------------------------------------------
# achats
# ----------------------------------------------------------------------------------------------------------------------

def purchaseslist(request):
    columns = ['jour', 'mois', 'année', 'prix moyen du panier', 'nombre de paniers', 'total']

    dates = []
    for d in Purchase.objects.all():
        date = d.date.date()
        if date not in dates:
            dates.append(date)

    dates.sort()

    purchases = []

    for date in dates:
        baskets = []
        for p in Purchase.objects.all():
            if p.date.date() == date:
                price = PurchaseDetailOp.objects.filter(purchase=p).aggregate(Sum('price'))['price__sum']
                baskets.append(-price)
        total_baskets = sum(baskets)
        mean_baskets = total_baskets / len(baskets)
        purchases.append({"date": date.isoformat(), "jour": date.day, "mois": date.month, "année": date.year,
                          'prix moyen du panier': '{0:.2f} €'.format(mean_baskets), 'nombre de paniers': len(baskets),
                          'total': '{0:.2f} €'.format(total_baskets)})

    columns = json.dumps(columns)
    purchases = json.dumps(purchases)
    purchases_stats = get_purchases_stats()
    return render(request, 'base/purchaseslist.html',
                  {'columns': columns, 'purchases': purchases, 'purchases_stats': purchases_stats})


def get_purchases_stats():
    # dates
    dates = [date.today()]
    for a in PurchaseDetailOp.objects.all():
        if a.date.date() not in dates:
            dates.append(a.date.date())

    dates.sort()

    # value
    values = [0] * len(dates)
    labels = [0] * len(dates)
    for a in PurchaseDetailOp.objects.all():
        for ii, i in enumerate(range(dates.index(a.date.date()), len(dates))):
            values[i] -= a.price
            if ii == 0:
                labels[i] -= a.price

    # stats
    purchases_stats = [{'value': '{0:.2f}'.format(values[i]), 'date': dates[i].isoformat(),
                        'label': 'Évolution : {0:.2f} €'.format(labels[i])}
                       for i in range(len(dates))]

    return purchases_stats


# ----------------------------------------------------------------------------------------------------------------------
# fonctionnement de l'epicerie
# ----------------------------------------------------------------------------------------------------------------------

def valueslist(request):
    # get stats
    purchases_stats = get_purchases_stats()
    comptes_stats = get_comptes_stats()
    appros_stats = get_appros_stats()

    # compute diff
    diff_dates = []
    for a in comptes_stats:
        date = a['date']
        if date not in diff_dates:
            diff_dates.append(date)
    for a in appros_stats:
        date = a['date']
        if date not in diff_dates:
            diff_dates.append(date)
    diff_dates.sort()

    values_p = [0] * len(diff_dates)
    values_n = [0] * len(diff_dates)
    values = [0] * len(diff_dates)
    labels = [0] * len(diff_dates)
    for a in comptes_stats:
        value = float(a['value'])
        date = a['date']
        i = diff_dates.index(date)
        values_p[i] = value
    for i in range(1, len(values_p)):
        if values_p[i] == 0:
            values_p[i] = values_p[i - 1]

    for a in appros_stats:
        value = float(a['value'])
        date = a['date']
        i = diff_dates.index(date)
        values_n[i] = value
    for i in range(1, len(values_n)):
        if values_n[i] == 0:
            values_n[i] = values_n[i - 1]

    values = [values_p[i] - values_n[i] for i in range(len(values))]

    labels[0] = values[0]
    for i in range(1, len(values)):
        labels[i] = values[i] - values[i - 1]

    diff_stats = [{'value': '{0:.2f}'.format(values[i]), 'date': diff_dates[i],
                   'label': 'Évolution : {0:.2f} €'.format(labels[i])}
                  for i in range(len(diff_dates))]

    # return
    return render(request, 'base/valueslist.html', {'purchases_stats': purchases_stats,
                                                    'comptes_stats': comptes_stats,
                                                    'appros_stats': appros_stats,
                                                    'diff_stats': diff_stats})


# ----------------------------------------------------------------------------------------------------------------------
# membres
# ----------------------------------------------------------------------------------------------------------------------

def members(request):
    local_settings = get_local_settings()
    if local_settings.use_subscription:
        columns = ['nom', "numéro d'adhérent", "date d'adhésion", "date de clotûre", "costisation d'adhésion du foyer",
                   'foyer', 'email', 'bigophone']
    else:
        columns = ['nom', "date d'adhésion", 'foyer', 'email', 'bigophone']
    members_data = [{"id": p.id, "nom": p.name, "numéro d'adhérent": p.household.get_formated_number(),
                     "date d'adhésion": p.household.date.strftime("%d/%m/%Y"),
                     "date de clotûre": p.household.get_formated_date_closed("%d/%m/%Y"), "foyer": str(p.household),
                     "costisation d'adhésion du foyer": '{0:.2f} €'.format(p.household.subscription),
                     "email": p.email, "bigophone": p.tel, "household_id": p.household.id if p.household else 0}
                    for p in Member.objects.all()]
    columns = json.dumps(columns)
    members_data = json.dumps(members_data)

    txt_number_h = str(len([p for p in Household.objects.all() if p.date_closed is None]))
    txt_number_m = str(len([p for p in Member.objects.all() if p.household.date_closed is None]))

    return render(request, 'base/members.html',
                  {'columns': columns, 'members': members_data,
                   'txt_number_m': txt_number_m,
                   'txt_number_h': txt_number_h,
                   'use_subscription': local_settings.use_subscription})


def menbersstats(request):
    # dates
    dates = [date.today()]
    for h in Household.objects.all():
        if h.date not in dates:
            dates.append(h.date)
        if h.date_closed is not None:
            if h.date_closed not in dates:
                dates.append(h.date_closed)
    dates.sort()

    # foyers
    households_stats = [0] * len(dates)
    for h in Household.objects.all():
        for i in range(dates.index(h.date), len(dates)):
            households_stats[i] += 1
        if h.date_closed is not None:
            for i in range(dates.index(h.date_closed), len(dates)):
                households_stats[i] -= 1
    households_data = [{'nb': str(households_stats[i]), 'date': dates[i].isoformat(), 'label': str(households_stats[i])}
                       for i in range(len(dates))]

    # membres
    members_stats = [0] * len(dates)
    for m in Member.objects.all():
        for i in range(dates.index(m.household.date), len(dates)):
            members_stats[i] += 1
        if m.household.date_closed is not None:
            for i in range(dates.index(m.household.date_closed), len(dates)):
                members_stats[i] -= 1
    members_data = [{'nb': str(members_stats[i]), 'date': dates[i].isoformat(), 'label': str(members_stats[i])} for i in
                    range(len(dates))]

    # return
    return render(request, 'base/menbersstats.html', {'households_data': households_data, 'members_data': members_data})


class HouseholdCreate(CreateView):
    model = Household
    fields = ['number', 'name', 'address', 'comment']
    template_name = 'base/household.html'
    success_url = reverse_lazy('base:members')

    def __init__(self, *args, **kwargs):
        super(HouseholdCreate, self).__init__(*args, **kwargs)
        if get_local_settings().use_subscription:
            fields = ['number', 'name', 'address', 'subscription', 'comment']
        else:
            fields = ['name', 'address', 'comment']
        self.fields = fields

    def get_initial(self):
        initial = super(HouseholdCreate, self).get_initial()
        initial['number'] = get_advised_household_number()
        return initial

    def get_context_data(self, **kwargs):
        data = super(HouseholdCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['members'] = MemberFormSet(self.request.POST)
        else:
            data['members'] = MemberFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        member = context['members']
        with transaction.atomic():
            form.instance.created_by = self.request.user
            if member.is_valid():
                member.instance = form.save()
                member.save()
                messages.success(self.request, '✔ Foyer créé !')
            else:
                return self.form_invalid(form)
        return super(HouseholdCreate, self).form_valid(form)


class HouseholdUpdate(UpdateView):
    model = Household
    fields = ['number', 'name', 'date_closed', 'address', 'comment']
    template_name = 'base/household.html'
    success_url = reverse_lazy('base:members')

    def __init__(self, *args, **kwargs):
        super(HouseholdUpdate, self).__init__(*args, **kwargs)
        if get_local_settings().use_subscription:
            fields = ['number', 'name', 'date_closed', 'address', 'comment']
        else:
            fields = ['name', 'address', 'comment']
        self.fields = fields

    def get_context_data(self, **kwargs):
        data = super(HouseholdUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['members'] = MemberFormSet(self.request.POST, instance=self.object)
        else:
            data['members'] = MemberFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        member = context['members']
        with transaction.atomic():
            form.instance.created_by = self.request.user
            if member.is_valid():
                member.instance = form.save()
                member.save()
                messages.success(self.request, '✔ Foyer mis à jour !')
            else:
                return self.form_invalid(form)
        return super(HouseholdUpdate, self).form_valid(form)


def archive_household(request, household_id):
    h = Household.objects.get(pk=household_id)
    h.activated = False
    h.save()
    messages.success(request, '✔ {} archivé !'.format(h.name))
    return HttpResponseRedirect(reverse('base:members'))


# ----------------------------------------------------------------------------------------------------------------------
# providers
# ----------------------------------------------------------------------------------------------------------------------

def providers(request):
    columns = ['nom', 'contact', 'commentaire']
    providers_data = [{"id": p.id, "nom": p.name, "contact": str(p.contact),
                       "commentaire": p.comment}
                      for p in Provider.objects.all()]
    columns = json.dumps(columns)
    providers_data = json.dumps(providers_data)
    return render(request, 'base/providers.html', {'columns': columns, 'providers': providers_data})


def create_provider(request):
    if request.method == 'POST':
        form = ProviderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✔ Fournisseur créé !')
            return HttpResponseRedirect(reverse('base:providers'))
    else:
        form = ProviderForm()
    return render(request, 'base/provider.html', {'form': form})


def detail_provider(request, provider_id):
    provider = Provider.objects.get(pk=provider_id)
    if request.method == 'POST':
        form = ProviderForm(request.POST, instance=provider)
        if form.is_valid():
            form.save()
            messages.success(request, '✔ Fournisseur mis à jour')
            return HttpResponseRedirect(reverse('base:providers'))
    else:
        form = ProviderForm(instance=provider)
    return render(request, 'base/provider.html', {'form': form})


# ----------------------------------------------------------------------------------------------------------------------
# notes
# ----------------------------------------------------------------------------------------------------------------------

def notes(request):
    columns = ['date', 'auteur', 'message', 'message lu ?', 'action(s) réalisée(s) ?']
    notes_data = [{"id": p.id, "date": p.date.strftime("%d/%m/%Y"), "auteur": str(p.who), "message": p.message,
                   'message lu ?': bool_to_utf8(p.read), 'action(s) réalisée(s) ?': bool_to_utf8(p.action)}
                  for p in Note.objects.all()]
    columns = json.dumps(columns)
    notes_data = json.dumps(notes_data)
    return render(request, 'base/notes.html', {'columns': columns, 'notes': notes_data})


def create_note(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✔ Message créé !')
            return HttpResponseRedirect(reverse('base:notes'))
    else:
        form = NoteForm()
    return render(request, 'base/note.html', {'form': form})


def detail_note(request, note_id):
    pdt = Note.objects.get(pk=note_id)

    if request.method == 'POST':
        form = NoteForm(request.POST, instance=pdt)
        if form.is_valid():
            form.save()
            messages.success(request, '✔ Message mis à jour !')
            return HttpResponseRedirect(reverse('base:notes'))
    else:
        form = NoteForm(instance=pdt)
    return render(request, 'base/note.html', {'form': form})


# ----------------------------------------------------------------------------------------------------------------------
# mails
# ----------------------------------------------------------------------------------------------------------------------

def mailslist(request):
    columns = ['jour', 'destinataires', 'sujet', 'envoyé ?']
    mails = [{"id": p.id, "jour": p.date.strftime("%d/%m/%Y"), "destinataires": ', '.join(p.recipient_list()),
              "sujet": p.subject, "envoyé ?": bool_to_utf8(p.sent)}
             for p in Mail.objects.all()]
    columns = json.dumps(columns)
    mails = json.dumps(mails)
    return render(request, 'base/mailslist.html', {'columns': columns, 'mails': mails})


def mails_action(request, mails, action):
    for mail in mails:
        if action == "send":
            local_settings = get_local_settings()
            if mail.send(local_settings):
                messages.success(request, '✔ ' + mail.success_msg())
            else:
                messages.error(request, '✘ ' + mail.error_msg())
        elif action == "del":
            mail.delete()
        else:
            raise NotImplementedError("Action inconnue : " + str(action))
    return redirect('base:mailslist')


def mails_send_all(request):
    mails = Mail.objects.all()
    return mails_action(request, mails, action="send")


def mails_del_send(request):
    mails = Mail.objects.filter(sent=True)
    return mails_action(request, mails, action="del")


def mails_del_all(request):
    mails = Mail.objects.all()
    return mails_action(request, mails, action="del")


def mail_del(request, mail_id):
    mails = Mail.objects.filter(pk=mail_id)
    return mails_action(request, mails, action="del")


def mail_send(request, mail_id):
    mails = Mail.objects.filter(pk=mail_id)
    return mails_action(request, mails, action="send")


# ----------------------------------------------------------------------------------------------------------------------
# inventaire
# ----------------------------------------------------------------------------------------------------------------------

def inventory(request):
    pdts = Product.objects.filter(Q(visible__exact=True) | ~Q(stock__exact=0))
    if request.method == 'POST':
        form = ProductList(pdts, request.POST)
        if form.is_valid():
            for p, q in form.cleaned_data.items():
                pdt = Product.objects.get(pk=p)
                if q is not None:
                    diff = q - pdt.stock
                    if diff != 0:  # todo check
                        op = ChangeStockOp.create_inventory(product=pdt, quantity=diff)
                        op.save()
                        pdt.stock = q
                        pdt.save()
            messages.success(request, '✔ Stock mis à jour !')
            return HttpResponseRedirect(reverse('base:ecarts'))
    else:
        form = ProductList(pdts, request.POST)
    return render(request, 'base/inventory.html', {'form': form})


def stats(request, product_id):
    # opes = ChangeStockOp.objects.filter(product=product_id, date__date__gt=date(2018, 1, 1))
    opes = ChangeStockOp.objects.filter(product=product_id).order_by('date')
    data = [{'stock': str(a.stock), 'date': a.date.isoformat(), 'label': a.label} for a in opes]
    pdt = Product.objects.get(pk=product_id)
    return render(request, 'base/stats.html', {'pdt': pdt, 'data': data, })


def database_info(request):
    pdts = [{'name': pdt.name, 'stock': pdt.stock,
             'computed': ChangeStockOp.objects.filter(product=pdt).aggregate(Sum('quantity'))['quantity__sum']}
            for pdt in Product.objects.all()]

    def f1(h):
        x = ApproCompteOp.objects.filter(household=h).aggregate(Sum('amount'))['amount__sum']
        return x if x else Decimal(0)

    def f2(h):
        x = PurchaseDetailOp.objects.filter(purchase__household=h).aggregate(Sum('price'))['price__sum']
        return x if x else Decimal(0)

    households = [{'name': h.pk, 'account': h.account,
                   'computed': f1(h) + f2(h)} for h in Household.objects.all()]
    return render(request, 'base/database_info.html', {'pdts': pdts, 'households': households, })


from .exports import *

def export_households(request):
    with NamedTemporaryFile() as tmp:
        generate_export_households(tmp.name)
        tmp.seek(0)
        response = HttpResponse(tmp.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=export_foyers.xlsx'
        return response

def export_products(request):
    with NamedTemporaryFile() as tmp:
        generate_export_products(tmp.name)
        tmp.seek(0)
        response = HttpResponse(tmp.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=export_produits.xlsx'
        return response

def export_providers(request):
    with NamedTemporaryFile() as tmp:
        generate_export_providers(tmp.name)
        tmp.seek(0)
        response = HttpResponse(tmp.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=export_fournisseurs.xlsx'
        return response

def export_inventory(request):
    with NamedTemporaryFile() as tmp:
        generate_export_inventory(tmp.name)
        tmp.seek(0)
        response = HttpResponse(tmp.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=bilan_inventaires.xlsx'
        return response

def ecarts(request):
    return render(request, 'base/ecarts.html', {'ecarts': generate_ecarts_data()})


def activity_details(request, perm_id):
    activity = get_object_or_404(Activity, pk=perm_id)
    if request.method == "POST":
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            return redirect('base:index')
    else:
        form = ActivityForm(instance=activity)
    return render(request, 'base/details_activity.html', {'form': form})
