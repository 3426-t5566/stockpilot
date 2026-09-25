from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from inventory.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("fulfilled", "Fulfilled"),
        ("cancelled", "Cancelled"),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def save(self, *args, **kwargs):
        if self.pk:
            old_status = Order.objects.get(pk=self.pk).status
        else:
            old_status = None

        super().save(*args, **kwargs)

        if old_status != "cancelled" and self.status == "cancelled":
            for item in self.items.all():
                item.product.stock_quantity += item.quantity
                item.product.save(update_fields=["stock_quantity"])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        if is_new:
            super().save(*args, **kwargs)
            self.product.stock_quantity -= self.quantity
            self.product.save(update_fields=["stock_quantity"])
        else:
            old_quantity = OrderItem.objects.get(pk=self.pk).quantity
            difference = self.quantity - old_quantity
            super().save(*args, **kwargs)
            if difference != 0:
                self.product.stock_quantity -= difference
                self.product.save(update_fields=["stock_quantity"])


@receiver(post_delete, sender=OrderItem)
def restore_stock_on_delete(sender, instance, **kwargs):
    instance.product.stock_quantity += instance.quantity
    instance.product.save(update_fields=["stock_quantity"])