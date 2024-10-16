import paypalrestsdk
from django.conf import settings
import django.core.paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from paypalrestsdk import Payment

from shop import settings
from store.models import Cart, Order, Product
from store.paypal import *


# Create your views here.
def index(request):
      # Filtrer les produits par catégorie spécifique (par exemple, 'Meilleurs Produits')
    bestProducts = Product.objects.filter(category__name='Mobile')[:4]  # Afficher 4 produits de cette catégorie

    # Récupérer un produit de trois catégories différentes (par exemple, 'Electronics', 'Furniture', 'Clothing')
    category1 = Product.objects.filter(category__name='Ordinateur').first()
    category2 = Product.objects.filter(category__name='Mobile')[2]
    category3 = Product.objects.filter(category__name='Imprimante').first()
    
    # Récupérer tous les produits indépendamment de leur catégorie
    products = Product.objects.all()
    # Diviser les produits en deux groupes égaux
    half = len(products) // 2
    products_line1 = products[:half]
    products_line2 = products[half:]
    item_name = request.GET.get('item-name')
    if item_name !='' and item_name is not None:
        products = Product.objects.filter(name__icontains=item_name)
    
    #paginator = django.core.paginator.Paginator(products, 4)
    #page = request.GET.get('page')
    #products = paginator.get_page(page)
    
    paginator = django.core.paginator.Paginator(products_line1, 4)
    page = request.GET.get('page')
    products_line1 = paginator.get_page(page)
    
    paginator = django.core.paginator.Paginator(products_line2, 4)
    page = request.GET.get('page')
    products_line2 = paginator.get_page(page)
    
    context = {
        'bestProducts': bestProducts,
        'category1': category1,
        'category2': category2,
        'category3': category3,
        'products': products,
        'products_line1' : products_line1,
        'products_line2' : products_line2,
    }
        
    return render(request, 'store/index.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/detail.html', context={"product": product})


def add_to_cart(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug=slug)
    cart, _ = Cart.objects.get_or_create(user=user)
    order, created = Order.objects.get_or_create(user=user,
                                                 ordered=False,
                                                 product=product)

    if created:
        cart.orders.add(order)
        cart.save()
    else:
        order.quantity += 1
        order.save()

    return redirect(reverse("product", kwargs={"slug": slug}))


def cart(request):
    cart = get_object_or_404(Cart, user=request.user)

    return render(request, 'store/cart.html', context={"orders": cart.orders.all()})


def delete_cart(request):
    if cart := request.user.cart:
        cart.delete()
        
    return redirect('index')


def checkout(request):
    # Récupérer toutes les commandes non finalisées pour cet utilisateur
    orders = Order.objects.filter(user=request.user, ordered=False)

    # Calculer le total
    total = 0
    for order in orders:
        total += order.product.price * order.quantity
        
    total_formatted = "{:.2f}".format(total)  # Formater avec un point décimal

    # Passer les informations au contexte pour l'affichage
    context = {
        'orders': orders,  # Liste des commandes
        'total': total_formatted,  # Total du panier
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
    }

    return render(request, 'store/checkout.html', context)


# Configuration du SDK PayPal
paypalrestsdk.configure({
  "mode": settings.PAYPAL_MODE,  # 'sandbox' pour le développement, 'live' pour la production
  "client_id": settings.PAYPAL_CLIENT_ID,
  "client_secret": settings.PAYPAL_CLIENT_SECRET
})



def process_paypal(request):
    cart = Cart.objects.get(user=request.user)
    total = cart.get_total()

    
    payment = Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('payment_success')),
            "cancel_url": request.build_absolute_uri(reverse('payment_cancel'))},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "Total commande",
                    "sku": "001",
                    "price": str(total),
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": str(total),
                "currency": "USD"},
            "description": "Achat de produits sur votre site"}]})

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                # Rediriger l'utilisateur vers PayPal pour approuver le paiement
                return redirect(link.href)
    else:
        return render(request, 'store/payment_error.html', {'error': payment.error})
    
    
    
def payment_success(request):
    order_id = request.GET.get('orderID')

    if order_id:
        # Rechercher les détails de la commande via PayPal
        order = paypalrestsdk.Order.find(order_id)

        if order:
            # Traiter la commande (par exemple marquer comme "payé" dans ta base de données)
            return render(request, 'store/payment_success.html', {'order': order})
        else:
            return render(request, 'store/payment_error.html', {'error': "Commande non trouvée."})
    else:
        return render(request, 'store/payment_cancel.html', {'error': "ID de commande manquant."})
    
    
    
""" payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    
    payment = Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Marquer les commandes comme payées
        cart = Cart.objects.get(user=request.user)
        cart.delete()
        return render(request, 'store/payment_success.html')
    else:
        return render(request, 'store/payment_error.html', {'error': payment.error})
    
"""
def payment_cancel(request):
    return render(request, 'store/payment_cancel.html')


def payment_error(request):
    return render(request, 'store/payment_error.html')