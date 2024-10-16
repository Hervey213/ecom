from django.contrib import admin

from store.models import Cart, Order, Product, Category


# Register your models here.

class AdminCategorie(admin.ModelAdmin):
    list_display = ('name', 'date_added')


class AdminProduct(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'date_added')


admin.site.register(Product, AdminProduct)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Category, AdminCategorie)
