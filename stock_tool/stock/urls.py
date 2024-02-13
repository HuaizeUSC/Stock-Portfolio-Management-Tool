from django.urls import path
from . import views

urlpatterns = [
    path('stocks/initialize/', views.initialize_view, name='initialize'),
    path('stocks/update/', views.update_view, name='update'),
    path('stocks/', views.stocks, name="stocks"),
    path('stocks/<str:symbol>/', views.stock, name="stock"),
    path('stocks/<str:symbol>/<str:timestamp>',
         views.stockprice, name="stockprice"),
    path('stockfavor/<str:symbol>', views.favor, name="favor"),
    path('stocks/<str:symbol>/<str:timestamp>/buystock',
         views.buystock, name="buystock")
]
