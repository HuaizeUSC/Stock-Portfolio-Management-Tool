from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout

from stock.models import Stock
from .models import FavoriteStock, Profile, VirtualFunds
from django.contrib import messages
# Create your views here.


def registeUser(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, username=user.username)
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
def profile(request, id):
    profile = request.user.profile

    trades = profile.trade_set.all()
    favors = profile.favoritestock_set.all()
    funds = profile.virtualfunds

    context = {'profile': profile, 'trades': trades,
               'funds': funds, 'favors': favors}
    return render(request, 'user/profile.html', context)
