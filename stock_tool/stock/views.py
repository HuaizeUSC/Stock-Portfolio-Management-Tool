from datetime import datetime
from decimal import Decimal

import math

from django.db.models import Case, When, Exists, OuterRef, Value, BooleanField
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from os import execv

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect
from .models import Stock, StockPrice
import requests
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from user.models import Profile, Trade, FavoriteStock, VirtualFunds

from .serializers import StockSerializer, StockPriceSerializer, StockWithFavorSerializer
from user.serializers import ProfileSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

# Create your views here.
ALPHAVANTAGE_API = 'ATY7R49Z6YQ679WR'
POLYGON_API = '7sDFU1hnKlUhRDSY7kKTmE4hMwrfpyLo'
NASDAQ100 = ['AAL', 'AAPL', 'ADBE', 'ADI', 'ADP', 'ADSK', 'AKAM', 'ALXN', 'AMAT', 'AMGN', 'AMZN', 'AVGO', 'BBBY',
             'BIDU', 'BIIB', 'BMRN', 'CA', 'CHKP', 'CHTR', 'CMCSA', 'COST', 'CSCO', 'CSX', 'CTSH', 'DLTR', 'EA', 'EBAY',
             'EXPE', 'FAST', 'FOX', 'FOXA', 'GILD', 'GOOGL', 'HSIC', 'ILMN', 'INCY', 'INTC', 'INTU', 'ISRG', 'JD',
             'KHC',
             'LBTYA', 'LBTYK', 'LLTC', 'LRCX', 'MAR', 'MAT', 'MCHP', 'MDLZ', 'MNST', 'MSFT', 'MU', 'NCLH', 'NFLX',
             'NTAP', 'NTES', 'NVDA', 'NXPI', 'ORLY', 'PAYX', 'PCAR', 'PYPL', 'QCOM', 'REGN', 'ROST', 'SBAC', 'SBUX',
             'SIRI', 'SRCL', 'STX', 'SWKS', 'TMUS', 'TRIP', 'TSCO', 'TSLA', 'TXN', 'ULTA', 'VOD', 'VRSK', 'VRTX', 'WBA',
             'WDC', 'XRAY']
databases = ['mysql1', 'mysql2', 'mysql3']
querysets = []


# hidden function only vistied by urls

def get_database(string):
    return databases[ord(string[0]) % len(databases)]


def initialize_view(request):
    if request.method == 'POST':
        initialize_system()
        return redirect('stocks')
    else:
        return render(request, 'stock/initialize.html')


def update_view(request):
    if request.method == 'POST':
        update_stock_client()
        return redirect('stocks')
    else:
        return render(request, 'stock/update.html')


def initialize_system():
    endday = datetime.now()
    startday = endday - relativedelta(years=2)
    startday, endday = startday.strftime(
        "%Y-%m-%d"), endday.strftime("%Y-%m-%d")
    for symbol in NASDAQ100:
        db = get_database(symbol)
        if (create_stock(symbol)):
            stock_model = Stock.objects.using(db).get(symbol=symbol)
            response_newstock = requests.get(
                url=f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{startday}/{endday}?adjusted=true&sort=asc&apiKey=7sDFU1hnKlUhRDSY7kKTmE4hMwrfpyLo"
            )
            if response_newstock.status_code == 200:
                aggregates = response_newstock.json()['results']
                for dayinfo in aggregates:
                    create_time_stamp(stock_model, dayinfo)


def create_2_year_history(stock):
    endday = datetime.now()
    startday = endday - relativedelta(years=2)
    startday, endday = startday.strftime(
        "%Y-%m-%d"), endday.strftime("%Y-%m-%d")
    response_newstock = requests.get(
        url=f"https://api.polygon.io/v2/aggs/ticker/{stock.symbol}/range/1/day/{startday}/{endday}?adjusted=true&sort=asc&apiKey=7sDFU1hnKlUhRDSY7kKTmE4hMwrfpyLo"
    )
    if response_newstock.status_code == 200:
        aggregates = response_newstock.json()['results']
        for dayinfo in aggregates:
            create_time_stamp(stock, dayinfo)


def update_stock_client():
    for db in databases:
        stocks = Stock.objects.using(db).all()
        endday = datetime.now().strftime('%Y-%m-%d')
        for st in stocks:
            timestamp = st.latestupdatetime // 10 ** 9
            startday = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
            response_newstock = requests.get(
                url=f"https://api.polygon.io/v2/aggs/ticker/{st.symbol}/range/1/day/{startday}/{endday}?adjusted=true&sort=asc&apiKey=7sDFU1hnKlUhRDSY7kKTmE4hMwrfpyLo"
            )
            if response_newstock.status_code == 200:
                aggregates = response_newstock.json()['results']
                print(aggregates)
                for dayinfo in aggregates:
                    create_time_stamp(st, dayinfo)
    return redirect('stocks')


def create_time_stamp(stock_model, st):
    timestamp_ms = st['t']
    db = get_database(stock_model.symbol)
    try:
        existing_record = StockPrice.objects.using(db).get(
            stock=stock_model, timestamp=timestamp_ms)
        existing_record.lowprice = st['l']
        existing_record.highprice = st['h']
        existing_record.openprice = st['o']
        existing_record.closeprice = st['c']
        existing_record.save()
    except StockPrice.DoesNotExist:
        StockPrice.objects.using(db).create(
            stock=stock_model,
            lowprice=st['l'],
            highprice=st['h'],
            openprice=st['o'],
            closeprice=st['c'],
            timestamp=timestamp_ms
        )
    except IntegrityError as e:
        print(f"IntegrityError: {e}")


def create_stock(symbol):
    db = get_database(symbol)
    try:
        existing_stock = Stock.objects.using(db).get(symbol=symbol)
        existing_stock.save()
        return True
    except Stock.DoesNotExist:
        response = requests.get(
            f"https://api.polygon.io/v3/reference/tickers/{symbol}", params={"apiKey": POLYGON_API})
        if response.status_code == 200:
            responsejson = response.json()
            if responsejson['status'] == 'OK':
                # get today's price information

                dailyresponse = requests.get(
                    url=f'https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}?apiKey=7sDFU1hnKlUhRDSY7kKTmE4hMwrfpyLo')
                daily = dailyresponse.json()['ticker']
                dailyjson = daily['day']
                # get basic information
                stock_info = responsejson['results']
                print(daily['updated'])
                stock = Stock.objects.using(db).create(
                    symbol=stock_info.get('ticker', ''),
                    name=stock_info.get('name', ''),
                    location=stock_info.get('locale', ''),
                    description=stock_info.get('description', ''),
                    homepage=stock_info.get('homepage_url', ''),
                    iconurl=stock_info.get('branding', {}).get('icon_url', ''),
                    companytype=stock_info.get('type', ''),
                    latestopenprice=dailyjson['o'],
                    latestcloseprice=dailyjson['c'],
                    latestupdatetime=daily['updated'],
                    latesthighprice=dailyjson['h'],
                    latestlowprice=dailyjson['l'],
                )
                create_2_year_history(stock)
                return True
            else:
                return False
        else:
            return False


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def stocks(request, pageNum, numPerPage):
    if request.user.is_authenticated:
        profile = Profile.objects.using(get_database(request.user.username)).get(username=request.user.username)
    else:
        profile = None
    context = {'stocks': StockSerializer(get_combined_queryset(profile, pageNum, numPerPage), many=True).data,
               'profile': ProfileSerializer(profile).data,
               'pageNum': math.ceil(len(querysets) / numPerPage)}
    return Response(context, status=status.HTTP_200_OK)


# def stocks(request):
#     if request.user.is_authenticated:
#         try:
#             profile = Profile.objects.using(get_database(request.user.username)).using(
#                 get_database(request.user.username)).get(username=request.user.username)
#         except Profile.DoesNotExist:
#             profile = None
#     else:
#         profile = None
#     context = {'stocks': get_combined_queryset(), 'profile': profile, 'error': None}
#     # if request.method == 'POST':
#     if request.method == 'GET':
#         symbol = request.GET.get('symbol')
#         if symbol:
#             symbol = symbol.upper()
#             try:
#                 db = get_database(symbol)
#                 stock = Stock.objects.using(db).get(symbol=symbol)
#                 return redirect('stock', symbol=symbol)
#             except Stock.DoesNotExist:
#                 if create_stock(symbol):
#                     return redirect('stock', symbol=symbol)
#                 else:
#                     context['error'] = f'Stock with symbol {symbol} not found.'
#                     # context['stocks'] = Stock.objects.all().order_by(
#                     #     '-latestcloseprice')
#                     return render(request, 'stock/stocks.html', context)
#
#     return render(request, 'stock/stocks.html', context)


def get_combined_queryset(profile, pageNum, numPerPage):
    global querysets
    querysets = []
    favorite_stocks = list(FavoriteStock.objects.using(get_database(profile.username)).filter(user=profile))
    for db in databases:
        # queryset = Stock.objects.using(db).annotate(
        #     favor=Case(
        #         When(id__in=[fs.id for fs in favorite_stocks], then=True),
        #         default=False,
        #         output_field=BooleanField()
        #     )
        # )
        queryset = Stock.objects.using(db).all()
        querysets += list(queryset)
    if pageNum * numPerPage > len(querysets):
        return querysets[(pageNum - 1) * numPerPage:]
    else:
        return querysets[(pageNum - 1) * numPerPage:pageNum * numPerPage]


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def stock(request, symbol):
    if request.user.is_authenticated:
        profile = Profile.objects.using(get_database(request.user.username)).get(username=request.user.username)
    else:
        profile = None
    symbol = symbol.upper()
    try:
        db = get_database(symbol)
        stock = Stock.objects.using(db).get(symbol=symbol)
        favorite_stock = FavoriteStock.objects.using(get_database(profile.username)).filter(user=profile,
                                                                                            stock=symbol).exists()
        if favorite_stock:
            setattr(stock, 'favor', True)
        else:
            setattr(stock, 'favor', False)
        stockPrice = StockPrice.objects.using(db).filter(stock=stock).order_by('-timestamp')
        context = {'stock': StockWithFavorSerializer(stock).data,
                   'stockPrice': StockPriceSerializer(stockPrice, many=True).data,
                   'profile': ProfileSerializer(profile).data}
        return Response(context, status=status.HTTP_200_OK)
    except Stock.DoesNotExist:
        if create_stock(symbol):
            db = get_database(symbol)
            stock = Stock.objects.using(db).get(symbol=symbol)
            setattr(stock, 'favor', False)
            stockPrice = StockPrice.objects.using(db).filter(stock=stock).order_by('-timestamp')
            context = {'stock': StockWithFavorSerializer(stock).data,
                       'stockPrice': StockPriceSerializer(stockPrice, many=True).data,
                       'profile': ProfileSerializer(profile).data}
            return Response(context, status=status.HTTP_200_OK)
        else:
            return Response({"error": f'Stock with symbol {symbol} not found.'}, status=status.HTTP_400_BAD_REQUEST)


# def stock(request, symbol):
#     if request.user.is_authenticated:
#         try:
#             db = get_database(request.user.username)
#             profile = Profile.objects.using(db).get(username=request.user.username)
#         except Profile.DoesNotExist:
#             profile = None
#     else:
#         profile = None
#     try:
#         db = get_database(symbol)
#         stock = Stock.objects.using(db).get(symbol=symbol)
#         return render(request, 'stock/stock.html',
#                       {'stock': stock,
#                        'prices': StockPrice.objects.using(db).filter(stock=stock).order_by('-timestamp'),
#                        'profile': profile})
#     except Stock.DoesNotExist:
#         db = get_database(symbol)
#         error = f'Stock with symbol {symbol} not found.'
#         return render(request, 'stock/stocks.html',
#                       {'error': error, 'stocks': Stock.objects.using(db).all().order_by('-latestcloseprice'),
#                        'profile': profile})

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def stockPrice(request, symbol, timestamp):
    if request.user.is_authenticated:
        profile = Profile.objects.using(get_database(request.user.username)).get(username=request.user.username)
    else:
        profile = None
    symbol = symbol.upper()
    db = get_database(symbol)
    stock = Stock.objects.using(db).get(symbol=symbol)
    stockprice = StockPrice.objects.using(db).get(stock=stock, timestamp=timestamp)
    context = {'stockPrice': StockPriceSerializer(stockprice).data,
               'profile': ProfileSerializer(profile).data}
    return Response(context, status=status.HTTP_200_OK)


# def stockprice(request, symbol, timestamp):
#     if request.user.is_authenticated:
#         try:
#             db = get_database(request.user.username)
#             profile = Profile.objects.using(db).get(username=request.user.username)
#         except Profile.DoesNotExist:
#             profile = None
#     else:
#         profile = None
#     db = get_database(symbol)
#     stock = Stock.objects.using(db).get(symbol=symbol)
#     stockprice = StockPrice.objects.using(db).get(stock=stock, timestamp=timestamp)
#     return render(request, 'stock/stockprice.html', {
#         'profile': profile, 'price': stockprice
#     })


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def favor(request, symbol):
    symbol = symbol.upper()
    db = get_database(symbol)
    stock = Stock.objects.using(db).get(symbol=symbol)
    dbUser = get_database(request.user.username)
    user = Profile.objects.using(dbUser).get(username=request.user.username)
    if not FavoriteStock.objects.using(dbUser).filter(user=user, stock=symbol).exists():
        FavoriteStock.objects.using(dbUser).create(
            user=user,
            stock=symbol
        )
        return Response({"message": "Add successfully"}, status=status.HTTP_200_OK)
    else:
        return Response({"message": "Already in the favorite list"}, status=status.HTTP_400_BAD_REQUEST)


# def favor(request, symbol):
#     db = get_database(symbol)
#     stock = Stock.objects.using(db).get(symbol=symbol)
#     dbUser = get_database(request.user.username)
#     user = Profile.objects.using(dbUser).get(username=request.user.username)
#     if not FavoriteStock.objects.using(dbUser).filter(owner=user, stock=stock).exists():
#         FavoriteStock.objects.using(dbUser).create(
#             owner=user,
#             stock=stock
#         )
#     return redirect('stock', symbol=symbol)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def buystock(request, symbol):
    symbol = symbol.upper()
    db = get_database(symbol)
    with transaction.atomic(using=db):
        stock = Stock.objects.using(db).get(symbol=symbol)
        stockprice = StockPrice.objects.using(db).filter(stock=stock).order_by('-timestamp').first()
    dbUser = get_database(request.user.username)
    with transaction.atomic(using=dbUser):
        profile = Profile.objects.using(dbUser).get(username=request.user.username)
        quantity = request.data['quantity']
        try:
            trade = Trade.objects.using(dbUser).get(user=profile, stockinfo=symbol)
            trade.quantity += Decimal(quantity)
            trade.save()
        except ObjectDoesNotExist:
            Trade.objects.using(dbUser).create(
                user=profile, stockinfo=symbol, quantity=quantity, price=stockprice.closeprice,
                timestamp=stockprice.timestamp)
        virtualFund = VirtualFunds.objects.using(dbUser).get(user=profile)
        virtualFund.balance -= Decimal(quantity) * stockprice.closeprice
        virtualFund.save()
    return Response({"message": "Buy successfully"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def sellstock(request, symbol):
    symbol = symbol.upper()
    db = get_database(symbol)
    with transaction.atomic(using=db):
        stock = Stock.objects.using(db).get(symbol=symbol)
        stockprice = StockPrice.objects.using(db).filter(stock=stock).order_by('-timestamp').first()
    dbUser = get_database(request.user.username)
    with transaction.atomic(using=dbUser):
        profile = Profile.objects.using(dbUser).get(username=request.user.username)
        trade = Trade.objects.using(dbUser).get(user=profile, stockinfo=symbol)
        quantity = request.data['quantity']
        trade.quantity -= Decimal(quantity)
        if trade.quantity == 0:
            trade.delete()
        else:
            trade.save()
        virtualFund = VirtualFunds.objects.using(dbUser).get(user=profile)
        virtualFund.balance += Decimal(quantity) * stockprice.closeprice
        virtualFund.save()
    return Response({"message": "Sell successfully"}, status=status.HTTP_200_OK)

# @login_required(login_url='login')
# def buystock(request, symbol, timestamp):
#     db = get_database(symbol)
#     stock = Stock.objects.using(db).get(symbol=symbol)
#     dbUser = get_database(request.user.username)
#     profile = Profile.objects.using(dbUser).get(username=request.user.username)
#     stockprice = StockPrice.objects.using(db).get(stock=stock, timestamp=timestamp)
#     if request.method == 'GET':
#         quantity = request.GET.get('quantity')
#         try:
#             trade = Trade.objects.using(dbUser).get(owner=profile, stockinfo=stockprice)
#             trade.quantity += Decimal(quantity)
#             trade.save()
#         except ObjectDoesNotExist:
#             Trade.objects.using(dbUser).create(
#                 owner=profile, stockinfo=stockprice, quantity=quantity)
#         virtualFund = VirtualFunds.objects.using(dbUser).get(user=profile)
#         virtualFund.balance -= Decimal(quantity) * stockprice.closeprice
#         virtualFund.save()
#
#     return render(request, 'stock/stockprice.html', {
#         'profile': profile, 'price': stockprice
#     })
