from django.urls import path
from . import views

urlpatterns = [
    path('stocks/initialize/', views.initialize_view, name='initialize'),
    path('stocks/update/', views.update_view, name='update'),
    path('stocks/', views.stocks, name="stocks"),
    path('stocks/<str:symbol>/', views.stock, name="stock"),
    path('stocks/<str:symbol>/<str:timestamp>',
         views.stockPrice, name="stockprice"),
    path('stockfavor/<str:symbol>', views.favor, name="favor"),
    path('stocks/<str:symbol>/<str:timestamp>/buystock/', views.buystock, name="buy_stock"),
    path('market/<int:pageNum>/<int:numPerPage>/', views.stocks, name="get_stocks"),
    path('market/<str:symbol>/', views.stock, name="stock"),
    path('market/price/<str:symbol>/<str:timestamp>', views.stockPrice, name="stock_price"),
    path('market/favor/<str:symbol>/', views.favor, name="favor"),
    path('market/buy/<str:symbol>/', views.buystock, name="buy_stock"),
    path('market/sell/<str:symbol>/', views.sellstock, name="sell_stock")
]
