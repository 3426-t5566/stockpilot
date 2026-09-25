from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Order
from .forms import OrderForm, OrderItemFormSet


@login_required
def order_list(request):
    orders = Order.objects.prefetch_related("items__product").all()
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_create(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            order = form.save()
            formset.instance = order
            formset.save()
            return redirect("orders:order_list")
    else:
        form = OrderForm()
        formset = OrderItemFormSet()
    return render(request, "orders/order_form.html", {"form": form, "formset": formset})


@login_required
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect("orders:order_list")
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)
    return render(request, "orders/order_form.html", {"form": form, "formset": formset})