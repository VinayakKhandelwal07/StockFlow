from datetime import datetime, timedelta
import json
import colorsys
import string
import secrets
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Sum, Q, Prefetch
from django.db.models.functions import TruncDay
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.timezone import now
from .forms import ProductForm, InventoryRequestForm
from .models import Company, Product, Staff, Order, InventoryRequest, OrderProduct, AuditTrail,User
from user.forms import StaffCreateForm
#create your views here
# .
from django.contrib.auth import get_user_model
User = get_user_model()


@login_required(login_url='user-login')
def index(request):
    print("Type of request.user.company:", type(request.user.company), request.user.company)

    company = request.user.company

    # Safety check: if company is not a Company instance, fetch it
    if not isinstance(company, Company):
        company = Company.objects.get(pk=company)

    # Counts
    products_count = Product.objects.filter(company=company).count()
    orders_count = Order.objects.filter(order_status='Pending', staff__company=company).count()
    staff_count = Staff.objects.filter(user__company=company).count()

    # Staff by role (filtered by company)
    staff_roles = User.ROLE_CHOICES
    staff_by_role = {
        role_key: Staff.objects.filter(user__role=role_key, user__company=company).count()
        for role_key, _ in staff_roles
    }

    # Products by category
    categories = Product._meta.get_field('category').choices
    products_by_category = {
        cat_key: Product.objects.filter(category=cat_key, company=company).count()
        for cat_key, _ in categories
    }

    # Orders by status (filtered by company)
    order_status_choices = ['Pending', 'Processed', 'Shipped', 'Completed']
    orders_by_status = {
        status: Order.objects.filter(order_status=status, staff__company=company).count()
        for status in order_status_choices
    }

    # Low stock products
    low_stock_products = Product.objects.filter(quantity__lte=50, quantity__gt=0, company=company)
    low_stock_alerts = low_stock_products.count()

    # Generate colors for product categories (make sure this function exists)
    product_categories_labels = list(products_by_category.keys())
    product_category_colors = generate_unique_colors(len(product_categories_labels))

    context = {
        'company_name': company.name if company else 'Your Company',
        'company_logo_url': company.logo.url if company and company.logo else '/static/default_logo.png',

        'products_count': products_count,
        'low_stock_alerts': low_stock_alerts,
        'orders_count': orders_count,
        'staff_count': staff_count,
        'low_stock_products': low_stock_products,

        # Chart data (JSON encoded for JS usage)
        'staff_roles_labels': json.dumps(list(staff_by_role.keys())),
        'staff_roles_data': json.dumps(list(staff_by_role.values())),

        'product_categories_labels': json.dumps(product_categories_labels),
        'product_categories_data': json.dumps(list(products_by_category.values())),
        'product_category_colors': json.dumps(product_category_colors),

        'order_status_labels': json.dumps(list(orders_by_status.keys())),
        'order_status_data': json.dumps(list(orders_by_status.values())),
    }

    return render(request, 'dashboard/index.html', context)

def generate_unique_colors(n):
    """
    Generate n visually distinct colors using HSL.
    Returns list of hex color strings.
    """
    colors = []
    for i in range(n):
        hue = i / n
        # Convert HSL to RGB (colorsys uses values between 0-1)
        rgb = colorsys.hls_to_rgb(hue, 0.5, 0.7)  # lightness=0.5, saturation=0.7
        # Convert RGB from 0-1 to 0-255 and format to hex
        hex_color = '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0]*255),
            int(rgb[1]*255),
            int(rgb[2]*255)
        )
        colors.append(hex_color)
    return colors


@login_required(login_url='user-login')
def products(request):
   company = request.user.company
  # get user's company

   products = Product.objects.filter(company=company)  #

 # Handle search functionality
   search_query = request.GET.get('search', '')
   if search_query:
        products = products.filter(name__icontains=search_query)

    # Handle category filter
   category_id = request.GET.get('category', '')
   if category_id:
        products = products.filter(category=category_id)


 # Pagination setup
   page = request.GET.get('page', 1)  # current page number from query params
   paginator = Paginator(products, 10)  # Show 10 products per page

   try:
        paginated_products = paginator.page(page)
   except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_products = paginator.page(1)
   except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated_products = paginator.page(paginator.num_pages)

    # Provide product category choices for the filter dropdown
   product_category_choices = Product._meta.get_field('category').choices
   products_count = Product.objects.count()
   

   context = {
       'products': paginated_products,
       'products_count': products_count,
       'product_category_choices': product_category_choices,
       'search_query': search_query,  # preserve search in template
        'category_id': category_id,
   }
   return render(request,'dashboard/products.html', context)


@login_required(login_url='user-login')
def product_add(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        product = form.save(commit=False)
        product.company = request.user.company
        product.added_by = request.user

  # assign company
        
        product.save()
        messages.success(request,f'{product.name} has been added')
        return redirect('dashboard:products')
    return render(request, 'dashboard/product_add.html', {'form': form})


@login_required(login_url='user-login')
def product_delete(request, pk):
    company = request.user.company

    item = get_object_or_404(Product, id=pk,company=company)
    
    if request.method == 'POST':
        item.delete()
        return redirect('dashboard:products')  # ✅ Fix the URL name here too
    
    return render(request, 'dashboard/product_delete.html', {'item': item})  # ✅ Pass context


@login_required(login_url='user-login')
def product_update(request,pk):
        company = request.user.company


        item = get_object_or_404(Product, id=pk, company=company)
        if request.method =="POST":
            form = ProductForm(request.POST,instance=item)
            if form.is_valid():
             product = form.save(commit=False)
             product.company = company  # reinforce company assignment
             product.save()
             return redirect('dashboard:products')
        else:
            form = ProductForm(instance=item)

        context ={
'form':form
        }
        return render(request , 'dashboard/product_update.html',context)


# def generate_temp_password(length=10):
#     characters = string.ascii_letters + string.digits + string.punctuation
#     return ''.join(secrets.choice(characters) for _ in range(length))

@login_required(login_url='user-login')
def approve_requests(request):
    # Only managers and admins can approve/reject requests
    if request.user.role not in ['manager', 'admin']:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:index')
    
    company = request.user.company


    requests = InventoryRequest.objects.filter(product__company=company).order_by('-created_at')

    return render(request, 'dashboard/approve_requests.html', {'requests': requests})


@login_required(login_url='user-login')
def approve_inventory_request(request, pk):
    # Permission check
    if request.user.role not in ['manager', 'Admin']:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard:index')
    
    company = request.user.company


    inv_request = get_object_or_404(InventoryRequest, pk=pk, status='PENDING', product__company=company)

    if request.method == 'POST':
     try:
        # Update quantity if new_quantity provided
        new_quantity = request.POST.get('new_quantity')
        if new_quantity:
            inv_request.quantity = int(new_quantity)
            inv_request.save()

        inv_request.process_approval(approved=True, reviewer=request.user)

        order_created = False  # Flag

        if not inv_request.order:
            with transaction.atomic():
                order = Order.objects.create(
                    staff=inv_request.requested_by,
                    reviewed_by=request.user,
                    order_status='Pending',
                    company=company
                )
                OrderProduct.objects.create(
                    order=order,
                    product=inv_request.product,
                    quantity=inv_request.quantity
                )
                inv_request.order = order
                inv_request.save()
                order_created = True

        if order_created:
            messages.success(request, f"Request approved and Order #{order.company_order_id} created successfully.")
        else:
            messages.success(request, "Request approved successfully.")

     except ValueError as ve:
      messages.error(request, f'Error approving request: {ve}')
     except Exception as e:
        messages.error(request, f'Unexpected error: {e}')


    return redirect('dashboard:approve_requests')


@login_required(login_url='user-login')
def reject_inventory_request(request, pk):
    if request.user.role not in ['manager', 'admin']:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard:index')
    
    company = request.user.company

    inv_request = get_object_or_404(InventoryRequest, pk=pk, status='PENDING',product__company=company)
    
    inv_request.process_approval(approved=False, reviewer=request.user)
    messages.success(request, 'Request rejected.')
    
    return redirect('dashboard:approve_requests')


@login_required(login_url='user-login')
def staffs(request):
    # Get the company of the currently logged-in user
    company = request.user.company

    # Base queryset: only staff belonging to the current user's company
    staff_queryset = Staff.objects.filter(user__company=company)

    # Filters from GET parameters
    search_query = request.GET.get('search', '').strip()
    role_filter = request.GET.get('role', '').strip()

    # Apply search filter
    if search_query:
        staff_queryset = staff_queryset.filter(
            user__first_name__icontains=search_query
        )

    # Apply role filter
    if role_filter:
        staff_queryset = staff_queryset.filter(user__role=role_filter)

    # Pagination setup (10 per page)
    paginator = Paginator(staff_queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Role of the logged-in user's staff profile
    try:
        user_role = getattr(request.user, 'role', 'employee')
    except Staff.DoesNotExist:
        user_role = 'employee'  # default fallback if not linked to Staff

    # Role-based permissions
    can_add_staff = user_role in ['admin', 'manager']
    show_password_column = user_role == 'admin'
    show_actions_column = user_role in ['admin', 'manager']

    # Role choices for dropdown filtering
    roles = User.ROLE_CHOICES

    context = {
        'page_obj': page_obj,  # paginated staff list
        'staff_count': staff_queryset.count(),
        'roles': roles,
        'search_query': search_query,
        'role_filter': role_filter,
        'user_role': user_role,
        'can_add_staff': can_add_staff,
        'show_password_column': show_password_column,
        'show_actions_column': show_actions_column,
        'company_name': company.name , # or str(company) depending on your model

    }

    return render(request, 'dashboard/staffs.html', context)

@login_required(login_url='user-login')
def staff_add(request):
      # Check if user belongs to a company and has role admin/manager
    if not hasattr(request.user, 'company') or request.user.company is None:
        messages.error(request, "You must belong to a company to add staff.")
        return redirect('dashboard:staffs')
    
    if request.method == 'POST':
        form = StaffCreateForm(request.POST, request.FILES,company=request.user.company)
        if form.is_valid():
            staff = form.save()

            # if Staff.objects.filter(user=staff.user).exists():
            #     messages.error(request, f"User {staff.user.username} is already a staff member.")
            #     return redirect('dashboard:staffs')
            
           
            messages.success(
                request,
                f"Staff member '{staff.user.get_full_name() or staff.user.username}' added successfully. Share the password manually."
            )
            return redirect('dashboard:staffs')
    else:
        form = StaffCreateForm(company=request.user.company)

    return render(request, 'dashboard/staff_add.html', {'form': form})

@login_required(login_url='user:login')
def staff_edit(request, id):
    company = request.user.company


    staff = get_object_or_404(Staff, id=id,user__company = company)
    user = staff.user  # Related User model instance

    if request.method == 'POST':
        # Extract first and last names from the 'name' field by splitting on space
        full_name = request.POST.get('name', '').strip()
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Update user fields
        user.first_name = first_name
        user.last_name = last_name
        user.email = request.POST.get('email', '').strip()
        user.save()

        # Update staff fields
        staff.phone = request.POST.get('phone', '').strip()
        staff.role = request.POST.get('role', '').strip()
        staff.address = request.POST.get('address', '').strip()
        staff.join_date = request.POST.get('join_date', '') or None

        # Handle password change if provided
        password = request.POST.get('password', '').strip()
        if password:
            user.set_password(password)
            user.save()

        # Handle profile picture update if any
        if request.FILES.get('profile_picture'):
            staff.profile_picture = request.FILES['profile_picture']

        staff.save()

        messages.success(request, "Staff details updated successfully!")
        return redirect('dashboard:staffs')

    # For GET request, render the form with staff data
    context = {'staff': staff}
    return render(request, 'dashboard/staff_edit.html', context)

@login_required(login_url='user-login') 
def staff_delete(request, id):
    company = request.user.company

    # Retrieve the staff instance with the matching company and id
    staff = get_object_or_404(Staff, id=id, user__company=company)

    if request.method == 'POST':
        try:
            username = staff.user.username
            full_name = staff.user.get_full_name() or username
            
            staff.delete()  # This triggers the signal to delete the user too
            
            messages.success(request, f"Staff '{full_name}' and associated user have been deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error occurred while deleting: {e}")

        return redirect('dashboard:staffs')  

    return render(request, 'dashboard/staff_delete_confirm.html', {'staff': staff})

@login_required(login_url='user-login') 
def staff_detail(request, id):
    company = request.user.company


    staff = get_object_or_404(Staff, id=id,user__company=company)
    return render(request, 'dashboard/staff_detail.html', {'staff': staff})


import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
@login_required(login_url='user-login')
def order_update(request, order_id):
    company = request.user.company
    order = get_object_or_404(Order, id=order_id, company=company)
    order_products = order.order_products.select_related('product').all()

    if request.method == 'POST':
        order_status = request.POST.get('order_status')
        valid_statuses = ['Pending', 'Processed', 'Shipped', 'Completed']

        if order_status not in valid_statuses:
            messages.error(request, "Invalid order status selected.")
            return redirect('dashboard:order_update', order_id=order_id)

        if order.order_status == 'Completed' and order_status != 'Completed':
            messages.error(request, "You cannot change the status of a completed order.")
            return redirect('dashboard:order_update', order_id=order_id)

        try:
            with transaction.atomic():
                original_status = order.order_status  # Capture the current status

                user_role = (getattr(request.user, 'role', '') or '').lower()

                logger.info(f"User role: {user_role}")
                logger.info(f"Order status transition: {original_status} → {order_status}")

                if user_role in ['manager', 'admin'] and original_status != 'Completed' and order_status == 'Completed':
                    approved_reqs = order.inventory_requests.filter(status='APPROVED').select_related('product')
                    logger.info(f"Approved inventory requests count: {approved_reqs.count()}")

                    if approved_reqs.count() == 0:
                        messages.warning(request, "No approved inventory requests found for this order.")

                    for inv_req in approved_reqs:
                        product = inv_req.product
                        logger.info(f"Product before update: {product.name}, Quantity: {product.quantity}")

                        if inv_req.request_type == 'RESTOCK':
                            product.quantity += inv_req.quantity
                            logger.info(f"Restocking {inv_req.quantity}, new quantity: {product.quantity}")
                        elif inv_req.request_type == 'CUSTOMER_ORDER':
                            if product.quantity >= inv_req.quantity:
                                product.quantity -= inv_req.quantity
                                logger.info(f"Shipping {inv_req.quantity}, new quantity: {product.quantity}")
                            else:
                                messages.error(request, f"Not enough stock for product '{product.name}'.")
                                return redirect('dashboard:order_update', order_id=order_id)

                        product.save()
                        logger.info(f"Product after update: {product.name}, Quantity: {product.quantity}")

                else:
                    logger.info("Inventory adjustments skipped: either order is not being completed or user is not allowed.")

                order.order_status = order_status
                order.reviewed_by = request.user
                order.save()
                messages.success(request, f"Order #{order_id} status updated to '{order_status}'.")
                return redirect('dashboard:orders')

        except Exception as e:
            logger.exception("Exception occurred while updating order")
            messages.error(request, f"Error updating order: {e}")
            return redirect('dashboard:order_update', order_id=order_id)

    context = {
        'order': order,
        'order_products': order_products,
    }
    return render(request, 'dashboard/order_update.html', context)

 
@login_required(login_url='user-login')
@transaction.atomic
def create_inventory_request(request):
    staff = request.user.staff
    company = request.user.company

    products = Product.objects.filter(company=company)

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        request_type = request.POST.get('request_type')
        reason = request.POST.get('reason', '')

        # Form validation
        if not all([product_id, quantity, request_type]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('dashboard:create_inventory_request')

        try:
            product = Product.objects.get(id=product_id)
            quantity = int(quantity)

            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")

            if request_type == 'CUSTOMER_ORDER' and quantity > product.quantity:
                raise ValueError(f"Requested quantity ({quantity}) exceeds available stock ({product.quantity}) for {product.name}.")

            # Create inventory request with transaction safety
            with transaction.atomic():
                inv_request = InventoryRequest.objects.create(
                    product=product,
                    quantity=quantity,
                    request_type=request_type,
                    reason=reason,
                    requested_by=staff.user,
                    status='PENDING',
                    company = company,
                )

                # Audit trail logging
                AuditTrail.objects.create(
                    user=request.user,
                    action='create',
                    model='InventoryRequest',
                    object_id=inv_request.company_request_id,
                    summary=f"InventoryRequest #{inv_request.company_request_id} created for '{product.name}' ({quantity}) by {request.user.get_full_name()}",
                )

            messages.success(request, f"Request for '{product.name}' submitted successfully.")
            return redirect('dashboard:my_requests')

        except Product.DoesNotExist:
            messages.error(request, "The selected product does not exist.")
        except ValueError as ve:
            messages.error(request, str(ve))
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")

    return render(request, 'dashboard/create_inventory_request.html', {'products': products})

@login_required(login_url='user-login')
def my_inventory_requests(request):
    staff = request.user.staff
    requests = InventoryRequest.objects.filter(requested_by=staff.user).order_by("-created_at")

    search_query = request.GET.get('search', '')
    if search_query:
        requests = requests.filter(product__name__icontains=search_query)

    status_filter = request.GET.get('status', '')
    if status_filter:
        requests = requests.filter(status=status_filter)

    context = {
        'requests': requests,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'dashboard/my_inventory_requests.html', context)

@login_required
def orders(request):
    company = request.user.company


    # Base queryset: orders linked to at least one approved inventory request
    orders = Order.objects.filter(
        inventory_requests__product__company=company,
        inventory_requests__status='APPROVED'
    ).distinct().order_by('-created_at')
    pending_requests_count = InventoryRequest.objects.filter(status='PENDING',company=company).count()

    # Search filter: by order ID or requested_by username
    search_query = request.GET.get('search', '').strip()
    if search_query:
        orders = orders.filter(
            Q(id__icontains=search_query) |
            Q(inventory_requests__requested_by__user__username__icontains=search_query)
        )

    # Status filter
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        orders = orders.filter(order_status__iexact=status_filter)

    orders_count = orders.count()

    context = {
        'orders': orders,
        'orders_count': orders_count,
        'search_query': search_query,
        'status_filter': status_filter,
        'pending_requests_count': pending_requests_count,
    }

    return render(request, "dashboard/orders.html", context)

@login_required(login_url='user-login')
def order_detail(request, order_id):
    company = request.user.company

    order = get_object_or_404(
        Order.objects.select_related('staff', 'company'),
        id=order_id,
        inventory_requests__product__company=company
    )

    order_products = OrderProduct.objects.filter(order=order).select_related('product')

    inventory_requests = InventoryRequest.objects.filter(order=order).select_related(
        'requested_by',  # if requested_by is Staff FK
        'product',
    )

    

    context = {
        'order': order,
        'order_products': order_products,
        'inventory_requests': inventory_requests,  # note plural
    }

    return render(request, 'dashboard/order_detail.html', context)


@login_required(login_url='user-login')
def order_delete(request, order_id):

    company = request.user.company
    order = get_object_or_404(Order, id=order_id, inventory_requests__product__company=company)

    if request.method == 'POST':
        try:
            order.delete()  # Signal handles the log
            messages.success(request, "Order deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error occurred while deleting: {e}")

        return redirect('dashboard:orders')

    return render(request, 'dashboard/order_delete_confirm.html', {'order': order})

# approve_requests for the manager aand admin
@login_required(login_url='user-login')
def delete_inventory_request(request, pk):
    # Only managers and admins can delete requests
    if request.user.role not in ['Manager', 'Admin']:
        messages.error(request, 'You do not have permission to delete requests.')
        return redirect('dashboard:approve_requests')  # Redirect to the approve requests page

    # Retrieve the request object, or return 404 if not found
    req = get_object_or_404(InventoryRequest, pk=pk)
    
    # Delete the request
    req.delete()
    messages.success(request, f"Inventory request #{pk} has been deleted.")
    
    # Redirect to the page showing requests for approval
    return redirect('dashboard:approve_requests') 


@login_required(login_url='user-login')
def inventory_request_update(request, pk):
    # Get the request object and check ownership
    inventory_request = get_object_or_404(InventoryRequest, pk=pk, requested_by=request.user)

    if request.method == "POST":
        form = InventoryRequestForm(request.POST, instance=inventory_request)
        if form.is_valid():
            form.save()
            messages.success(request, "Request updated successfully.")
            return redirect('dashboard:my_requests')
    else:
        form = InventoryRequestForm(instance=inventory_request)

    return render(request, 'dashboard/inventory_request_form.html', {'form': form})


@login_required(login_url='user-login')
def inventory_request_delete(request, pk):
    inventory_request = get_object_or_404(InventoryRequest, pk=pk, requested_by=request.user)

    if request.method == 'POST':
        inventory_request.delete()
        messages.success(request, "Request deleted successfully.")
        return redirect('dashboard:my_requests')

    return render(request, 'dashboard/inventory_request_confirm_delete.html', {'request_obj': inventory_request})


from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from dashboard.models import AuditTrail, Order

from django.core.paginator import Paginator
from .models import Order, AuditTrail

from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import AuditTrail, Order

@login_required
def order_logs(request):
    company = request.user.company

    logs_list = AuditTrail.objects.filter(
        model='Order',
        company=company
    ).select_related('user').order_by('-timestamp')

    paginator = Paginator(logs_list, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Fetch existing orders in one query
    existing_orders = Order.objects.filter(company=company)
    order_map = {order.company_order_id: order for order in existing_orders}

    # Add the order to each log entry if it still exists
    for log in page_obj:
        log.order = order_map.get(log.object_id)  # None if deleted

    context = {
        'logs': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'dashboard/order_logs.html', context)



@login_required
def post_login_redirect(request):
    user = request.user
    if user.is_superuser:
        return redirect('/admin/')  # Redirect superuser to Django admin panel
    else:
        return redirect('index')
    
from django.views import View
from django.db import transaction
from .forms import CompanyRegistrationForm, UserRegistrationForm


class RegisterCompanyAndAdminView(View):
    template_name = 'user/register.html'

    def get(self, request):
        company_form = CompanyRegistrationForm()
        user_form = UserRegistrationForm()
        return render(request, self.template_name, {'company_form': company_form, 'user_form': user_form})

    def post(self, request):
        company_form = CompanyRegistrationForm(request.POST)
        user_form = UserRegistrationForm(request.POST)

        if company_form.is_valid() and user_form.is_valid():
            try:
                with transaction.atomic():
                    # Create Company
                    company = company_form.save()

                    # Create User
                    user = user_form.save(commit=False)
                    user.company = company
                    user.role = 'admin'
                    # user.is_superuser = True     # <--- Allow access to Django admin
                    user.is_staff = True 
                    user.set_password(user_form.cleaned_data['password1'])  # set password properly
                    user.save()

                    if not hasattr(user, 'staff'):
                        Staff.objects.create(user=user)
                    else:
                        messages.warning(request, "Staff profile already exists for this user.")

                    messages.success(request, 'Company and Admin user registered successfully! Please log in.')
                    return redirect('user:login')
                
            except Exception as e:
                messages.error(request, f"Registration failed: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")

        return render(request, self.template_name, {'company_form': company_form, 'user_form': user_form})