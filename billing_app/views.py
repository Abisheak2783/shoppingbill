import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F, Count
from django.db.models.functions import TruncHour, TruncDay, TruncMonth
from django.utils import timezone
import datetime

from .models import Product, Category, Bill, BillItem
from .forms import ProductForm

def get_bill_items_summary(bills):
    """Shared helper to aggregate itemized sales consistently."""
    items = BillItem.objects.filter(bill__in=bills).values(
        'product__name', 'price'
    ).annotate(
        total_qty=Sum('quantity'),
        total_price=Sum('total')
    ).order_by('-total_price')
    
    return [
        {
            'name': item['product__name'],
            'price': float(item['price']),
            'qty': item['total_qty'],
            'total': float(item['total_price'])
        } for item in items
    ]

def get_revenue_trend(bills, period):
    """Aggregates revenue by time intervals based on the selected period."""
    if period == 'today':
        trunc_func = TruncHour('created_at')
    elif period == 'yearly':
        trunc_func = TruncMonth('created_at')
    else: # weekly, monthly
        trunc_func = TruncDay('created_at')

    trend = bills.annotate(
        period_label=trunc_func
    ).values('period_label').annotate(
        total=Sum('final_amount')
    ).order_by('period_label')

    result = []
    for item in trend:
        label_dt = item['period_label']
        if not label_dt: continue
        
        if period == 'today':
            l = label_dt.strftime('%I %p') # e.g., 01 PM
        elif period == 'yearly':
            l = label_dt.strftime('%b %Y') # e.g., Jan 2024
        else:
            l = label_dt.strftime('%d %b') # e.g., 12 Apr
        
        result.append({'label': l, 'value': float(item['total'])})
    return result

@login_required
def dashboard(request):
    today = timezone.now().date()
    # Total sales today
    bills_today = Bill.objects.filter(created_at__date=today)
    total_sales_today = bills_today.aggregate(Sum('final_amount'))['final_amount__sum'] or Decimal('0.00')
    
    # Total revenue roughly
    total_revenue = Bill.objects.aggregate(Sum('final_amount'))['final_amount__sum'] or Decimal('0.00')
    
    # Low stock alert
    low_stock_products = Product.objects.filter(stock_quantity__lte=F('low_stock_threshold'))
    
    # Recent Activity (Last 5 sold items)
    recent_activity = BillItem.objects.all().order_by('-id')[:5]

    # Last generated bill for easy viewing
    last_bill = Bill.objects.filter(admin_user=request.user).order_by('-id').first()

    # Today's Item Summary (Using the helper)
    today_items_summary = get_bill_items_summary(bills_today)

    # Daily Goal Logic
    daily_goal = Decimal('10000.00') # Set a default daily goal
    goal_progress = (total_sales_today / daily_goal * 100) if daily_goal > 0 else 0
    goal_progress = min(100, float(goal_progress)) # Cap at 100%
    
    # Recent Bills (Last 5)
    recent_bills = Bill.objects.all().order_by('-id')[:5]

    # Full Product List for Dashboard Quick Search
    all_products = Product.objects.all().order_by('name')
    products_json = json.dumps([
        {
            'id': p.id,
            'name': p.name,
            'price': float(p.price),
            'stock': p.stock_quantity,
            'category': p.category.name if p.category else 'Uncategorized'
        } for p in all_products
    ])

    context = {
        'total_sales_today': total_sales_today,
        'total_revenue': total_revenue,
        'low_stock_products': low_stock_products[:5],
        'bills_today_count': bills_today.count(),
        'recent_activity': recent_activity, # Items
        'recent_bills': recent_bills, # Full Bills
        'today_items_summary': today_items_summary,
        'last_bill': last_bill,
        'daily_goal': daily_goal,
        'goal_progress': goal_progress,
        'total_products_count': all_products.count(),
        'total_categories_count': Category.objects.count(),
        'products_json': products_json,
    }
    return render(request, 'dashboard.html', context)

@login_required
def reports_view(request):
    today = timezone.now().date()
    # Today
    today_bills = Bill.objects.filter(created_at__date=today)
    today_revenue = today_bills.aggregate(Sum('final_amount'))['final_amount__sum'] or Decimal('0.00')
    
    # Weekly (last 7 days)
    week_ago = today - datetime.timedelta(days=7)
    weekly_bills = Bill.objects.filter(created_at__date__gte=week_ago)
    weekly_revenue = weekly_bills.aggregate(Sum('final_amount'))['final_amount__sum'] or Decimal('0.00')
    
    # Monthly (last 30 days)
    month_ago = today - datetime.timedelta(days=30)
    monthly_bills = Bill.objects.filter(created_at__date__gte=month_ago)
    monthly_revenue = monthly_bills.aggregate(Sum('final_amount'))['final_amount__sum'] or Decimal('0.00')
    
    # Yearly (current year)
    yearly_bills = Bill.objects.filter(created_at__year=today.year)
    yearly_revenue = yearly_bills.aggregate(Sum('final_amount'))['final_amount__sum'] or Decimal('0.00')
    
    context = {
        'today_revenue': today_revenue,
        'today_count': today_bills.count(),
        'today_items_json': json.dumps(get_bill_items_summary(today_bills)),
        'today_trend_json': json.dumps(get_revenue_trend(today_bills, 'today')),
        
        'weekly_revenue': weekly_revenue,
        'weekly_count': weekly_bills.count(),
        'weekly_items_json': json.dumps(get_bill_items_summary(weekly_bills)),
        'weekly_trend_json': json.dumps(get_revenue_trend(weekly_bills, 'weekly')),
        
        'monthly_revenue': monthly_revenue,
        'monthly_count': monthly_bills.count(),
        'monthly_items_json': json.dumps(get_bill_items_summary(monthly_bills)),
        'monthly_trend_json': json.dumps(get_revenue_trend(monthly_bills, 'monthly')),
        
        'yearly_revenue': yearly_revenue,
        'yearly_count': yearly_bills.count(),
        'yearly_items_json': json.dumps(get_bill_items_summary(yearly_bills)),
        'yearly_trend_json': json.dumps(get_revenue_trend(yearly_bills, 'yearly')),
    }
    return render(request, 'reports.html', context)

@login_required
def product_list(request):
    products = Product.objects.all().order_by('name')
    
    # Calculate stats
    total_products = products.count()
    low_stock_count = products.filter(stock_quantity__gt=0, stock_quantity__lte=F('low_stock_threshold')).count()
    out_of_stock_count = products.filter(stock_quantity__lte=0).count()
    total_inventory_value = products.aggregate(
        total_value=Sum(F('price') * F('stock_quantity'))
    )['total_value'] or Decimal('0.00')
    
    context = {
        'products': products,
        'stats': {
            'total_products': total_products,
            'low_stock': low_stock_count,
            'out_of_stock': out_of_stock_count,
            'total_value': total_inventory_value,
        }
    }
    return render(request, 'product_list.html', context)

@login_required
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form, 'action': 'Add'})

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form, 'action': 'Edit'})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})

@login_required
def billing_view(request):
    if request.method == 'POST':
        try:
            customer_name = request.POST.get('customer_name')
            customer_phone = request.POST.get('customer_phone')
            discount = Decimal(request.POST.get('discount', '0.00'))
            gst_percent = Decimal(request.POST.get('gst', '0.00'))
            
            product_ids = request.POST.getlist('product_id[]')
            quantities = request.POST.getlist('quantity[]')
            
            if not product_ids:
                messages.error(request, 'No products added to the bill.')
                return redirect('billing')

            bill = Bill(
                admin_user=request.user,
                customer_name=customer_name,
                customer_phone=customer_phone,
            )
            bill.save() # Save early to get ID for items
            
            subtotal = Decimal('0.00')
            
            # Process items
            for p_id, qty_str in zip(product_ids, quantities):
                qty = int(qty_str)
                if qty <= 0: continue
                
                product = Product.objects.get(id=p_id)
                price = product.price
                item_total = price * qty
                subtotal += item_total
                
                # Check stock and deduct
                if product.stock_quantity < qty:
                    # rollback bill if insufficient stock just to be safe structurally, though handled loosely here
                    messages.warning(request, f'Warning: Sold more {product.name} than in stock.')
                
                product.stock_quantity -= qty
                product.save()
                
                BillItem.objects.create(
                    bill=bill,
                    product=product,
                    quantity=qty,
                    price=price,
                    total=item_total
                )
            
            # Apply calculations
            bill.total_amount = subtotal
            bill.discount = discount
            after_discount = subtotal - discount
            gst_amount = (after_discount * gst_percent) / Decimal('100.0')
            bill.gst_amount = gst_amount
            bill.final_amount = after_discount + gst_amount
            bill.save()
            
            messages.success(request, 'Bill generated and saved successfully.')
            return redirect('invoice', pk=bill.pk)
            
        except Exception as e:
            messages.error(request, f'Error generating bill: {str(e)}')
            return redirect('billing')
            
    products = Product.objects.filter(stock_quantity__gt=0).order_by('name')
    categories = Category.objects.all().order_by('name')
    
    # converting to list of dicts to safely pass to JS template as json
    products_list = []
    for p in products:
        products_list.append({
            'id': p.id, 
            'name': p.name, 
            'price': float(p.price), 
            'stock': p.stock_quantity,
            'category_id': p.category.id if p.category else None,
            'category_name': p.category.name if p.category else 'Uncategorized',
            'image_url': p.image.url if p.image else ''
        })
    products_json = json.dumps(products_list)
    
    return render(request, 'billing.html', {
        'products': products, 
        'categories': categories,
        'products_json': products_json
    })

@login_required
def invoice_view(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    return render(request, 'invoice.html', {'bill': bill})
