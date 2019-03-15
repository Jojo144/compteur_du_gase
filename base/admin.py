from django.contrib import admin
from .models import *

from django.contrib.auth.models import User, Group

admin.site.unregister(User)
admin.site.unregister(Group)


admin.site.register(Category)
admin.site.register(Provider)
admin.site.register(Member)
admin.site.register(Household)
admin.site.register(Product)
admin.site.register(InventoryOp)

