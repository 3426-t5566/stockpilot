from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "sku", "category", "price", "stock_quantity", "low_stock_threshold"]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]