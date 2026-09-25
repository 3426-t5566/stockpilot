from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import render
from inventory.models import Product
from orders.models import Order

@login_required
def home(request):
    low_stock = Product.objects.filter(stock_quantity__lte=models.F("low_stock_threshold"))
    recent_orders = Order.objects.order_by("-created_at")[:5]
    context = {
        "low_stock": low_stock,
        "recent_orders": recent_orders,
    }
    return render(request, "dashboard/home.html", context)