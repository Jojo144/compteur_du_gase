from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.conf.urls import url
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.models import User, Group

from datetime import timedelta

from .models import *


admin.site.site_header = "Interface d'administration du Compteur du GASE"

class MemberInline(admin.TabularInline):
    model = Member


class HouseholdAdmin(admin.ModelAdmin):
    list_display = ('activated', 'id', 'number', 'name', 'members', 'address', 'date', 'date_closed', 'subscription', 'on_the_flight')
    list_display_links = ('name',)

    inlines = [MemberInline, ]

    def members(self, obj):
        return ', '.join([str(m) for m in Member.objects.filter(household=obj.pk)])

    def get_queryset(self, request):
        return Household.all_objects.all()


class ProductAdmin(admin.ModelAdmin):
    list_display = ('activated', 'id', 'name', 'provider', 'category', 'unit', 'price',
                    'cost_of_purchase', 'pwyw', 'visible', 'referent', 'stock_alert', 'stock')
    list_display_links = ('name',)
    list_filter = ('activated', 'category', 'unit', 'pwyw', 'visible', 'provider')

    def get_queryset(self, request):
        return Product.all_objects.all()


class ProviderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact')
    list_display_links = ('name',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)


class UnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'vrac', 'pluralize')
    list_display_links = ('name',)


class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'household', 'receipt', 'stock_alert')
    list_display_links = ('name',)

    def get_queryset(self, request):
        return Member.all_objects.all()


class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'household', 'receipt', 'stock_alert')
    list_display_links = ('name',)


class ChangeStockOpAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'date', 'product', 'quantity', 'price', 'purchase_cost')
    list_filter = ('label','product')
    list_display_links = ('label',)


class ApproCompteOpAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'household', 'kind')
    list_filter = ('kind','household')
    list_display_links = ('household',)


# Formulaire pour ajouter une activité récurrente au tableau des permanences
class RecurringForm(forms.Form):
    description = forms.CharField(label='Description', initial='Permanence', max_length=100)
    begin_date = forms.DateField(label='Date de début (incluse)', widget=AdminDateWidget())
    end_date = forms.DateField(label='Date de fin (incluse)', widget=AdminDateWidget())
    DAYS = (
        (0, "Lundi"),
        (1, "Mardi"),
        (2, "Mercredi"),
        (3, "Jeudi"),
        (4, "Vendredi"),
        (5, "Samedi"),
        (6, "Dimanche"),
    )
    days = forms.MultipleChoiceField(label='Jours', widget=forms.CheckboxSelectMultiple, choices=DAYS)

# Ajout du formulaire pour activité récurrente à l'interface d'admin
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('description', 'date', 'volunteer1', 'volunteer2', 'comment')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'^recurring/$', self.add_recurring_view, name='recurring'),
        ]
        return my_urls + urls

    def add_recurring_view(self, request):
        if request.method == 'POST':
            form = RecurringForm(request.POST)
            if form.is_valid():
                description = form.cleaned_data['description']
                begin_date = form.cleaned_data['begin_date']
                end_date = form.cleaned_data['end_date']
                delta = end_date - begin_date
                days = [int(d) for d in form.cleaned_data['days']]
                for i in range(delta.days + 1):
                    d = begin_date + timedelta(days=i)
                    if d.weekday() in days:
                        a = Activity(description=description, date=d)
                        a.save()
                return redirect('admin:base_activity_changelist')
        else:
            form = RecurringForm()
        return render(request, 'admin/recurring.html',
                      { 'opts': self.model._meta, 'form': form})


# admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Household, HouseholdAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Note)
admin.site.register(LocalSettings)
admin.site.register(Mail)
admin.site.register(Activity, ActivityAdmin)

admin.site.register(ChangeStockOp, ChangeStockOpAdmin)
admin.site.register(ApproCompteOp, ApproCompteOpAdmin)

admin.site.login = staff_member_required(admin.site.login, login_url=settings.LOGIN_URL)
