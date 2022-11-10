from django.contrib import admin

from .models import Transaction, CUser, Category

admin.site.register(Transaction)
admin.site.register(CUser)
admin.site.register(Category)
