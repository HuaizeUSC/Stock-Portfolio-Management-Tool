from datetime import datetime
from os import execv
from django.db import IntegrityError
from django.shortcuts import render, redirect
from more_itertools import quantify
from pandas import Timestamp
from .models import Stock, StockPrice
import requests
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from user.models import Profile, Trade, FavoriteStock
# Create your views here.
ALPHAVANTAGE_API = 'ATY7R49Z6YQ679WR'
POLYGON_API = '7sDFU1hnKlUhRDSY7kKTmE4hMwrfpyLo'
NASDAQ100 = ['AAL', 'AAPL', 'ADBE', 'ADI', 'ADP', 'ADSK', 'AKAM', 'ALXN', 'AMAT', 'AMGN', 'AMZN', 'AVGO', 'BBBY', 'BIDU', 'BIIB', 'BMRN', 'CA', 'CHKP', 'CHTR', 'CMCSA', 'COST', 'CSCO', 'CSX', 'CTSH', 'DLTR', 'EA', 'EBAY', 'EXPE', 'FAST', 'FOX', 'FOXA', 'GILD', 'GOOGL', 'HSIC', 'ILMN', 'INCY', 'INTC', 'INTU', 'ISRG', 'JD', 'KHC',
             'LBTYA', 'LBTYK', 'LLTC', 'LRCX', 'MAR', 'MAT', 'MCHP', 'MDLZ', 'MNST', 'MSFT', 'MU', 'NCLH', 'NFLX', 'NTAP', 'NTES', 'NVDA', 'NXPI', 'ORLY', 'PAYX', 'PCAR', 'PYPL', 'QCOM', 'REGN', 'ROST', 'SBAC', 'SBUX', 'SIRI', 'SRCL', 'STX', 'SWKS', 'TMUS', 'TRIP', 'TSCO', 'TSLA', 'TXN', 'ULTA', 'VOD', 'VRSK', 'VRTX', 'WBA', 'WDC', 'XRAY']

# hidden function only vistied by urls


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
    startday = endday-relativedelta(years=2)
    startday, endday = startday.strftime(
        "%Y-%m-%d"), endday.strftime("%Y-%m-%d")
    for symbol in NASDAQ100:
        print(symbol)
        if (create_stock(symbol)):
            print(symbol)
            stock_model = Stock.objects.get(symbol=symbol)
            response_newstock = requests.get(
                url=f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{startday}/{endday}?adjusted=true&sort=asc&apiKey=7sDFU1hnKlUhRDSY7kKTmE4hMwrfpyLo"
            )
            if response_newstock.status_code == 200:
                aggregates = response_newstock.json()['results']
                for dayinfo in aggregates:
                    create_time_stamp(stock_model, dayinfo)


def create_2_year_history(stock):
    endday = datetime.now()
    startday = endday-relativedelta(years=2)
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
    stocks = Stock.objects.all()
    endday = datetime.now().strftime('%Y-%m-%d')
    for st in stocks:
        timestamp = st.latestupdatetime//10**9
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

    try:
        existing_record = StockPrice.objects.get(
            stock=stock_model, timestamp=timestamp_ms)
        existing_record.lowprice = st['l']
        existing_record.highprice = st['h']
        existing_record.openprice = st['o']
        existing_record.closeprice = st['c']
        existing_record.save()
    except StockPrice.DoesNotExist:
        StockPrice.objects.create(
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
    try:
        existing_stock = Stock.objects.get(symbol=symbol)
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
                stock = Stock.objects.create(
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


def stocks(request):
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            profile = None
    else:
        profile = None
    context = {'stocks': Stock.objects.all().order_by(
        '-latestcloseprice'), 'profile': profile, 'error': None}
    # if request.method == 'POST':

    if request.method == 'GET':
        symbol = request.GET.get('symbol')
        if symbol:
            symbol = symbol.upper()
            try:
                stock = Stock.objects.get(symbol=symbol)
                return redirect('stock', symbol=symbol)
            except Stock.DoesNotExist:
                if create_stock(symbol):
                    return redirect('stock', symbol=symbol)
                else:
                    context['error'] = f'Stock with symbol {symbol} not found.'
                    context['stocks'] = Stock.objects.all().order_by(
                        '-latestcloseprice')
                    return render(request, 'stock/stocks.html', context)

    return render(request, 'stock/stocks.html', context)


def stock(request, symbol):
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            profile = None
    else:
        profile = None
    try:
        stock = Stock.objects.get(symbol=symbol)
        return render(request, 'stock/stock.html', {'stock': stock, 'prices': StockPrice.objects.filter(stock=stock).order_by('-timestamp'), 'profile': profile})
    except Stock.DoesNotExist:
        error = f'Stock with symbol {symbol} not found.'
        return render(request, 'stock/stocks.html', {'error': error, 'stocks': Stock.objects.all().order_by('-latestcloseprice'), 'profile': profile})


def stockprice(request, symbol, timestamp):
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            profile = None
    else:
        profile = None
    stock = Stock.objects.get(symbol=symbol)
    stockprice = StockPrice.objects.get(stock=stock, timestamp=timestamp)
    return render(request, 'stock/stockprice.html', {
        'profile': profile, 'price': stockprice
    })


@login_required(login_url='login')
def favor(request, symbol):
    print(21)
    stock = Stock.objects.get(symbol=symbol)
    if not FavoriteStock.objects.filter(owner=request.user.profile, stock=stock).exists():
        stock = Stock.objects.get(symbol=symbol)
        favorite_stock = FavoriteStock.objects.create(
            owner=request.user.profile,
            stock=stock
        )
    return redirect('stock', symbol=symbol)


@login_required(login_url='login')
def buystock(request, symbol, timestamp):
    stock = Stock.objects.get(symbol=symbol)
    profile = Profile.objects.get(user=request.user)
    stockprice = StockPrice.objects.get(stock=stock, timestamp=timestamp)
    if request.method == 'GET':
        quantity = request.GET.get('quantity')
        Trade.objects.create(
            owner=profile, stockinfo=stockprice, quantity=quantity)

    return render(request, 'stock/stockprice.html', {
        'profile': profile, 'price': stockprice
    })
