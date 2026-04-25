from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=3, default=0.000)
    low_stock_threshold = models.DecimalField(max_digits=10, decimal_places=3, default=10.000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Bill(models.Model):
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    customer_name = models.CharField(max_length=150, blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00) # Subtotal
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00) # Grand Total
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill #{self.id} - {self.customer_name or 'Walk-in'} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1.000)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price at the time of sale
    total = models.DecimalField(max_digits=12, decimal_places=2) # quantity * price
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Bill #{self.bill.id})"
