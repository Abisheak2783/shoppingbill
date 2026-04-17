from django.contrib import admin
from .models import Category, Product, Bill, BillItem

class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 0

class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'total_amount', 'discount', 'gst_amount', 'final_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('customer_name', 'customer_phone')
    inlines = [BillItemInline]

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'low_stock_threshold')
    list_filter = ('category',)
    search_fields = ('name',)

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Bill, BillAdmin)
