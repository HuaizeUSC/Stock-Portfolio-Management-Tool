from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout

from .models import FavoriteStock, Profile, VirtualFunds
from django.contrib import messages

from stock.models import Stock

databases = ['mysql1', 'mysql2', 'mysql3']


# Create your views here.
def get_database(string):
    return databases[ord(string[0]) % len(databases)]


def registeUser(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            db = get_database(request.POST['username'])
            Profile.objects.using(db).create(username=user.username)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'user/register.html', {'form': form})


def loginUser(request):
    if request.user.is_authenticated:
        return redirect('stocks')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('stocks')
    else:
        form = AuthenticationForm()
    return render(request, 'user/login.html', {'form': form})


def logoutUser(request):
    logout(request)
    messages.info(request, 'User was logged out!')
    return redirect('stocks')


@login_required(login_url='login')
def deleteFavor(request, id, symbol):
    user = request.user.profile
    db = get_database(symbol)
    dbUser = get_database(user.username)
    stock = Stock.objects.using(db).get(symbol=symbol)

    FavoriteStock.objects.using(dbUser).get(owner=user, stock=stock).delete()
    return redirect('profile', id=id)


@login_required(login_url='login')
def profile(request, id):
    profile = Profile.objects.using(get_database(request.user.username)).get(id=id)
    trades = profile.trade_set.all()
    favors = profile.favoritestock_set.all()
    funds = profile.virtualfunds

    context = {'profile': profile, 'trades': trades,
               'funds': funds, 'favors': favors}
    return render(request, 'user/profile.html', context)


def deregister(request, id, username):
    logout(request)
    db = get_database(username)
    Profile.objects.using(db).get(id=id).delete()
    return redirect('stocks')
