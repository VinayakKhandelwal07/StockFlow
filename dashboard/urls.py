from django.urls import path 
from . import views

app_name = 'dashboard'  # THIS LINE IS REQUIRED FOR namespacing

urlpatterns = [
    # Dashboard home
    path('', views.index, name='index'),

    # Product URLs
    path('products/', views.products, name='products'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('products/updates/<int:pk>/', views.product_update, name='product_update'),

    # Staff URLs
    path('staffs/', views.staffs, name='staffs'),
    path('staffs/add/', views.staff_add, name='staff_add'),
    path('staff/edit/<int:id>/', views.staff_edit, name='staff_edit'), 
    path('staff/delete/<int:id>/', views.staff_delete, name='staff_delete'),
    path('staff/detail/<int:id>/', views.staff_detail, name='staff_detail'),

    # Request/Order Management (staff "My Requests")
    path('my_inventory_requests/', views.my_inventory_requests, name='my_requests'),  # staff own requests
    path('order/create/', views.create_inventory_request, name='create_inventory_request'),

    # Orders URLs — IMPORTANT: use actual PK (order.id) here for lookups
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/update/', views.order_update, name='order_update'),
    path('order/<int:order_id>/delete/', views.order_delete, name='order_delete'),

    # Admin/Manager Dashboard Views
    path('orders/', views.orders, name='orders'),  # all orders listing
    path('order/logs/', views.order_logs, name='order_logs'),  # logs/history
    path('inventory-requests/', views.approve_requests, name='approve_requests'),  # approval list
    path('inventory-request/<int:pk>/approve/', views.approve_inventory_request, name='approve_inventory_request'),
    path('inventory-request/<int:pk>/reject/', views.reject_inventory_request, name='reject_inventory_request'),
    path('inventory-request/<int:pk>/edit/', views.inventory_request_update, name='edit_inventory_request'),

    # Staff request deletion (own requests)
    path('my-inventory-request/<int:pk>/delete/', views.inventory_request_delete, name='inventory_request_delete'),

    # Admin/Manager can delete any request
    path('inventory-request/<int:pk>/delete/', views.delete_inventory_request, name='delete_inventory_request'),

    # Company registration
    path('register/', views.RegisterCompanyAndAdminView.as_view(), name='RegisterCompanyAndAdminView'),

    # Post-login redirect
    path('dashboard/', views.post_login_redirect, name='post_login_redirect'),
]
