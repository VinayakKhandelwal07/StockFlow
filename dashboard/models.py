from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from django.db.models import Max
from django.db import models, transaction


class Company(models.Model):
    """
    Represents a company/tenant in the system.
    """
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)

    def __str__(self):
        return self.name
    
    def logo_url(self):
        if self.logo:
            return f"{settings.MEDIA_URL}{self.logo}"
        else:
            return '/static/default_logo.png'  # fallback default logo


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')

    def save(self, *args, **kwargs):
        """
        Enforce that non-superusers must have a company.
        First user of a company is assigned 'admin' role automatically.
        """
        if not self.is_superuser:
            if not self.company:
                raise ValueError("Non-superusers must be assigned a company.")
            # Assign admin role to first user of company
            if not self.pk and not User.objects.filter(company=self.company).exists():
                self.role = 'admin'
        super().save(*args, **kwargs)

    def __str__(self):
        company_name = self.company.name if self.company else "No Company"
        return f"{self.username} ({self.get_role_display()}) - {company_name}"


class Staff(models.Model):
    """
    Extra profile info for a User who is staff.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff')
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    join_date = models.DateField(auto_now_add=True, editable=False, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    must_update_profile = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # def delete(self, *args, **kwargs):
    #     """
    #     Delete both Staff and linked User
    #     """
    #     self.user.delete()
    #     super().delete(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


CATEGORY_CHOICES = (
    ('Stationary', 'Stationary'),
    ('Food', 'Food'),
    ('Toy', 'Toy'),
    ('Electronics', 'Electronics'),
    ('Clothing', 'Clothing'),
    ('Furniture', 'Furniture'),
    ('Books', 'Books'),
    ('Sports', 'Sports'),
    ('Beauty', 'Beauty & Personal Care'),
    ('Health', 'Health & Wellness'),
    ('Automotive', 'Automotive'),
    ('Jewelry', 'Jewelry'),
)


class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_quantity = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return f'{self.name} ({self.company.name}) - Qty: {self.quantity}'

    @property
    def stock_status(self):
        if self.quantity is None:
            return "No Data"
        elif self.quantity > 500:
            return "Over Stock"
        elif self.quantity > 50:
            return "In Stock"
        elif 5 <= self.quantity <= 50:
            return "Low Stock"
        else:
            return "Out of Stock"


class Order(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='orders')
    company_order_id = models.PositiveIntegerField(editable=False,null=False, blank=False)

    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_orders')
    order_status = models.CharField(
        max_length=50,
        choices=[
            ('Pending', 'Pending'),
            ('Processed', 'Processed'),
            ('Shipped', 'Shipped'),
            ('Completed', 'Completed'),
            ('Rejected', 'Rejected'),
        ],
        default='Pending'
    )
    products = models.ManyToManyField(Product, through='OrderProduct', related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company', 'company_order_id')  # unique order IDs per company

    def save(self, *args, **kwargs):
     if not self.pk and not self.company_order_id:
        with transaction.atomic():
            last_id = Order.objects.filter(company=self.company).aggregate(
                Max('company_order_id')
            )['company_order_id__max']
            self.company_order_id = 1 if last_id is None else last_id + 1

     super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.company_order_id} by {self.staff.username} ({self.company.name})"
    
    @property
    def order_type(self):
        # Returns the request_type of first linked inventory_request if any
        if self.inventory_requests.exists():
            return self.inventory_requests.first().request_type
        return "N/A"

    @property
    def reason(self):
        # Returns the reason of first linked inventory_request if any
        if self.inventory_requests.exists():
            return self.inventory_requests.first().reason
        return ""


class InventoryRequest(models.Model):
    REQUEST_TYPES = (
        ('RESTOCK', 'Restock'),
        ('CUSTOMER_ORDER', 'Customer Order'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='inventory_requests')
    company_request_id = models.PositiveIntegerField(editable=False,null=False, blank=False)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='inventory_requests')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_requests')
    quantity = models.PositiveIntegerField()
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_requests')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_inventory_requests')
    reason = models.TextField(blank=True, help_text="Optional: explain why this request is needed")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('company', 'company_request_id')

    def process_approval(self, approved, reviewer):
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.status = 'APPROVED' if approved else 'REJECTED'
        self.save()

    def save(self, *args, **kwargs):
        if not self.pk and not self.company_request_id:
          with transaction.atomic():
           last_id = InventoryRequest.objects.filter(company=self.company).aggregate(
          Max('company_request_id'))['company_request_id__max']            
          self.company_request_id = 1 if last_id is None else last_id + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Request #{self.company_request_id} ({self.request_type}) by {self.requested_by.username}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_products')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('order', 'product')

    def __str__(self):
        return f"{self.product.name} (x{self.quantity}) in Order #{self.order.company_order_id}"


class AuditTrail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    event_category = models.CharField(max_length=255)
    method = models.CharField(max_length=50)
    summary = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    object_id = models.PositiveBigIntegerField(null=True, blank=True)

    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_trails'  # Optional: makes reverse lookups cleaner
    )

    def __str__(self):
        return f"{self.timestamp} - {self.user.username} - {self.action}"
