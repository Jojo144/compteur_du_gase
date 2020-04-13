from django.contrib import admin
from .models import *

from django.contrib.auth.models import User, Group

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


admin.site.unregister(User)
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

admin.site.register(ChangeStockOp, ChangeStockOpAdmin)
admin.site.register(ApproCompteOp, ApproCompteOpAdmin)
