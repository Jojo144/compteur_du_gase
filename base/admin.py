import datetime

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.conf.urls import url
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.models import User, Group
from django.urls import reverse

from datetime import timedelta

from django.utils.formats import date_format

from .models import *


admin.site.site_header = "Interface d'administration du Compteur du GASE"

def get_week_number(d: datetime.date) -> int:
    _, weeknumber, _ = d.isocalendar()
    return weeknumber

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

class PeriodicityChoice(models.IntegerChoices):
    WEEKLY = 1, "chaque semaine"
    EVERY_2_WEEKS = 2, "toutes les deux semaines"
    EVERY_3_WEEKS = 3, "toutes les trois semaines"
    EVERY_4_WEEKS = 4, "toutes les quatres semaines"


class RecurringForm(forms.Form):
    description = forms.CharField(label='Description', initial='Permanence', max_length=100)
    begin_date = forms.DateField(label='Date de début (incluse)', widget=AdminDateWidget())
    end_date = forms.DateField(label='Date de fin (incluse)', widget=AdminDateWidget())
    periodicity = forms.TypedChoiceField(label="Récurrence", choices=PeriodicityChoice.choices, initial=PeriodicityChoice.WEEKLY, coerce=int)
    DAYS = (
        (0, "Lundi"),
        (1, "Mardi"),
        (2, "Mercredi"),
        (3, "Jeudi"),
        (4, "Vendredi"),
        (5, "Samedi"),
        (6, "Dimanche"),
    )
    days = forms.TypedMultipleChoiceField(label='Jours de la semaine', widget=forms.CheckboxSelectMultiple, choices=DAYS, coerce=int)

class WhenFilter(admin.SimpleListFilter):
    title = "date"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "when"
    def lookups(self, request, model_admin):
        return (
            ('future', "À venir uniquement"),
            ("past", "Passés uniquement"),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        value = self.value()
        today = datetime.date.today()

        if value == "future":
            return queryset.filter(date__gte=today)
        elif value == "past":
            return queryset.filter(date__lt=today)
        else:
            return queryset


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('description', 'formatted_date', 'volunteer1', 'volunteer2', 'comment')
    ordering = ("date", "description")
    list_filter = (WhenFilter,)

    @admin.display(description='Date', ordering="date")
    def formatted_date(self, obj):
        return date_format(obj.date, "l j F Y")

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
                periodicity = form.cleaned_data['periodicity']
                valid_week_modulo = get_week_number(begin_date) % periodicity

                delta = end_date - begin_date
                valid_days = form.cleaned_data['days']
                for i in range(delta.days + 1):
                    d = begin_date + timedelta(days=i)

                    if (
                        d.weekday() in valid_days
                        and
                        (get_week_number(d) % periodicity) == valid_week_modulo
                    ):
                        Activity.objects.create(description=description, date=d)
                return redirect('admin:base_activity_changelist')
        else:
            form = RecurringForm()
        return render(request, 'admin/recurring.html',
                      { 'opts': self.model._meta, 'form': form})


class LocalSettingsAdmin(admin.ModelAdmin):
    """
    Only one instance of LocalSettings is wanted, and one is already created by
    migrations ; thus there is no need neither to create nor delete objects
    """
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def response_post_save_change(self, request, obj):
        return redirect('admin:index')


if settings.YNH_INTEGRATION_ENABLED:
    # users are handled by YunoHost
    admin.site.unregister(User)
    admin.site.login = staff_member_required(admin.site.login, login_url=settings.LOGIN_URL)

admin.site.unregister(Group)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Household, HouseholdAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Note)
admin.site.register(LocalSettings, LocalSettingsAdmin)
admin.site.register(Mail)
admin.site.register(Activity, ActivityAdmin)

admin.site.register(ChangeStockOp, ChangeStockOpAdmin)
admin.site.register(ApproCompteOp, ApproCompteOpAdmin)


admin.site.site_url = reverse('base:index')
