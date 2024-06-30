from django.urls import path, include
from . import views

app_name = 'shoppingcart'
urlpatterns = [
    path('', views.viewShoppingCart, name ='shoppingCart'),
    path('update_quantity/', views.updateQuantity, name='updateQuantity'),
    path('create_bill/', views.createBill, name='createBill'),
    path('payment/<int:bill_id>/', views.Payment.as_view(), name='paymentPage'),
    path('cancelpayment/<int:bill_id>/', views.cancelPayment, name = 'cancelPayment'),
    path('timeoutpayment/<int:bill_id>/', views.timeoutPayment, name = 'timeoutPayment'),
    path('orderlist/', views.OrderList.as_view(), name= 'orderList'),
    path('addToCart/', views.addToCart, name='addItem'),

]