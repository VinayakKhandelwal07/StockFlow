from django.contrib import admin
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html
from .models import Company, Product, Order, InventoryRequest, Staff, AuditTrail, OrderProduct

class StaffInline(admin.TabularInline):
    model = Staff
    extra = 0
    show_change_link = True

class ProductInline(admin.TabularInline):
    model = Product
    extra = 0

class OrderInline(admin.TabularInline):
    model = Order
    extra = 0

class InventoryRequestInline(admin.TabularInline):
    model = InventoryRequest
    extra = 0

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'created_at',
        'staff_count',
        'product_count',
        'order_count',
        'request_count',
        'view_link'
    ]
    inlines = [ ProductInline, OrderInline, InventoryRequestInline]
    search_fields = ['name']
    ordering = ['-created_at']

    def staff_count(self, obj):
        count = Staff.objects.filter(user__company=obj).count()
        url = (
            reverse("admin:dashboard_staff_changelist")
            + "?"
            + urlencode({"user__company__id": str(obj.id)})
        )
        return format_html('<a href="{}">{} Staff</a>', url, count)
    staff_count.short_description = 'Staff'

    def product_count(self, obj):
        count = Product.objects.filter(company=obj).count()
        return count
    product_count.short_description = 'Products'

    def order_count(self, obj):
        count = Order.objects.filter(company=obj).count()
        return count
    order_count.short_description = 'Orders'

    def request_count(self, obj):
        count = InventoryRequest.objects.filter(company=obj).count()
        return count
    request_count.short_description = 'Inventory Requests'

    def view_link(self, obj):
        url = reverse("admin:dashboard_company_change", args=[obj.pk])
        return format_html('<a href="{}">View</a>', url)
    view_link.short_description = 'Details'


# ========== COMMON BASE TO LOCK COMPANY FIELD ON UPDATE ==========
class CompanyScopedAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Lock company field after creation
            return self.readonly_fields + ('company',)
        return self.readonly_fields


@admin.register(Product)
class ProductAdmin(CompanyScopedAdmin):
    list_display = ['name', 'category', 'quantity', 'company', 'view_company']
    list_filter = ['company', 'category']
    search_fields = ['name']

    def view_company(self, obj):
        url = reverse("admin:dashboard_company_change", args=[obj.company.id])
        return format_html(f'<a href="{url}">View</a>')
    view_company.short_description = "Company"


@admin.register(Order)
class OrderAdmin(CompanyScopedAdmin):
    list_display = ['company_order_id', 'company', 'order_status', 'created_at']
    list_filter = ['company', 'order_status']
    search_fields = ['company_order_id']
    date_hierarchy = 'created_at'


@admin.register(InventoryRequest)
class InventoryRequestAdmin(CompanyScopedAdmin):
    list_display = ['product', 'company', 'quantity', 'request_type', 'status', 'requested_by', 'created_at']
    list_filter = ['company', 'request_type', 'status']
    search_fields = ['product__name', 'requested_by__username']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_company', 'phone', 'get_role', 'must_update_profile']

    # For filters, use the related field notation:
    list_filter = ['user__company', 'user__role']

    search_fields = ['user__username', 'user__email']

    def get_company(self, obj):
        return obj.user.company if obj.user else None
    get_company.short_description = 'Company'
    get_company.admin_order_field = 'user__company'

    def get_role(self, obj):
        return obj.user.role if obj.user else None
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'user__role'

@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'action', 'model', 'object_id', 'method', 'timestamp']
    list_filter = ['company', 'action', 'model']
    search_fields = ['user__username', 'model', 'object_id']
    readonly_fields = [field.name for field in AuditTrail._meta.fields]


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity']
    search_fields = ['order__company_order_id', 'product__name']
