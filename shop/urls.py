"""
URL configuration for shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from store.views import add_to_cart, cart, delete_cart, index, checkout, payment_cancel, payment_error, payment_success, process_paypal, product_detail
from accounts.views import signup, logout_user, login_user

from shop import settings

urlpatterns = [
    path('', index, name ='index'),
    path('admin/', admin.site.urls),
    path('login/', login_user, name="login"),
    path('signup/', signup, name="signup"),
    path('logout/', logout_user, name="logout"),
    path('cart/', cart, name="cart"),
    path('cart/delete', delete_cart, name="delete-cart"),
    path('product/<str:slug>/', product_detail, name="product"),
    path('product/<str:slug>/add-to-cart/', add_to_cart, name="add-to-cart"),
    path('checkout/', checkout, name="checkout"),
    path('process_paypal/', process_paypal, name="process_paypal"),
    path('payment-success/', payment_success, name='payment_success'),
    path('payment-cancel/', payment_cancel, name='payment_cancel'),
    path('payment-error/', payment_error, name='payment_error'),
] + static(settings.MEDIA_URL, document_root =settings.MEDIA_ROOT)
