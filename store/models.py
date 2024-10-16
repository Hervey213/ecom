from django.db import models
from django.urls import reverse
from django.utils import timezone

from shop.settings import AUTH_USER_MODEL

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length = 200)
    date_added = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_added']
    
    def __str__(self):
        return self.name    


"""
Produit
- Nom
- Prix
- La quantité en stock
- Description
- Image

"""


class Product(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128)
    price = models.FloatField(default=0.0)
    stock = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="products", blank=True, null=True)
    category = models.ForeignKey(Category, related_name='categorie', null=True, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product", kwargs={"slug": self.slug})


# Article (Order)
"""
- Utilisateur
- Produit
-Quantité
- Commande ou non
"""


class Order(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    
    

# Panier (Cart)
"""
-Utilisateur
-Articles
- Commande ou non
- Date de la commande
"""


class Cart(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    orders = models.ManyToManyField(Order)
    
    
    
    def __str__(self):
        return self.user.username
    
    def get_total(self):
        total = 0
        for order in self.orders.all():
            total += order.product.price * order.quantity
        return total



    def delete(self, *args, **kwargs):
        for order in self.orders.all():
            order.ordered = True
            order.ordered_date = timezone.now()
            order.save()
        
        self.orders.clear()
        super().delete(*args, **kwargs)