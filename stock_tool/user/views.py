import math

from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from .models import FavoriteStock, Profile, VirtualFunds, Trade
from django.contrib import messages
from stock.models import Stock
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .serializers import ProfileSerializer, TradeSerializer, FavoriteStockSerializer, VirtualFundsSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

databases = ['mysql1', 'mysql2', 'mysql3']


# Create your views here.
def get_database(string):
    return databases[ord(string[0]) % len(databases)]


@api_view(['POST'])
@authentication_classes([])
def registeUser(request):
    data = {
        'username': request.data.get('username', ''),
        'password1': request.data.get('password1', ''),
        'password2': request.data.get('password2', '')
    }
    form = UserCreationForm(data)
    if form.is_valid():
        user = form.save()
        db = get_database(request.data.get('username'))
        profile = Profile.objects.using(db).create(username=user.username)
        return Response({"user_id": profile.id}, status=status.HTTP_200_OK)
    else:
        print(form.errors)
        return Response({"error": form.errors}, status=status.HTTP_400_BAD_REQUEST)


# def registeUser(request):
#     form = UserCreationForm(request.POST)
#     if form.is_valid():
#         user = form.save()
#         db = get_database(request.POST['username'])
#         Profile.objects.using(db).create(username=user.username)
#         return redirect('login')
#     return render(request, 'user/register.html', {'form': form})

@api_view(['POST'])
@authentication_classes([])
def loginUser(request):
    data = {
        'username': request.data.get('username', ''),
        'password': request.data.get('password', '')
    }
    form = AuthenticationForm(data=data)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        db = get_database(request.data.get('username'))
        profile = Profile.objects.using(db).get(username=user.username)
        token = RefreshToken.for_user(user)
        return Response({"id": profile.id, "username": profile.username, "access_token": str(token.access_token),
                         "refresh_token": str(token)}, status=status.HTTP_200_OK)
    else:
        return Response({"error": form.errors}, status=status.HTTP_400_BAD_REQUEST)


# def loginUser(request):
#     if request.user.is_authenticated:
#         return redirect('stocks')
#
#     if request.method == 'POST':
#         form = AuthenticationForm(data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect('stocks')
#     else:
#         form = AuthenticationForm()
#     return render(request, 'user/login.html', {'form': form})

@api_view(['GET'])
@authentication_classes([])
def logoutUser(request):
    logout(request)
    messages.info(request, 'User was logged out!')
    return Response({"message": "Logout successfully"}, status=status.HTTP_200_OK)


# def logoutUser(request):
#     logout(request)
#     messages.info(request, 'User was logged out!')
#     return redirect('stocks')

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def deleteFavor(request, symbol):
    db = get_database(symbol)
    with transaction.atomic(using=db):
        stock = Stock.objects.using(db).get(symbol=symbol)
    dbUser = get_database(request.user.username)
    with transaction.atomic(using=dbUser):
        user = Profile.objects.using(dbUser).get(username=request.user.username)
        FavoriteStock.objects.using(dbUser).get(user=user, stock=symbol).delete()
    return Response({"message": "successfully delete this stock!"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def favors(request, pageNum, numPerPage):
    db = get_database(request.user.username)
    profile = Profile.objects.using(db).get(username=request.user.username)
    favors = []
    try:
        favors += list(FavoriteStock.objects.using(db).filter(user=profile))
    except:
        favors = []
    if pageNum * numPerPage > len(favors):
        favors = favors[(pageNum - 1) * numPerPage:]
    else:
        favors = favors[(pageNum - 1) * numPerPage:pageNum * numPerPage]
    context = {'profile': ProfileSerializer(profile).data, 'favors': FavoriteStockSerializer(favors, many=True).data,
               'pageNum': math.ceil(len(favors) / numPerPage)}
    return Response(context, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def trades(request, pageNum, numPerPage):
    db = get_database(request.user.username)
    profile = Profile.objects.using(db).get(username=request.user.username)
    trades = []
    trades += list(Trade.objects.using(db).filter(user=profile))
    if pageNum * numPerPage > len(trades):
        trades = trades[(pageNum - 1) * numPerPage:]
    else:
        trades = trades[(pageNum - 1) * numPerPage:pageNum * numPerPage]
    funds = VirtualFunds.objects.using(db).get(user=profile)
    context = {'profile': ProfileSerializer(profile).data, 'trades': TradeSerializer(trades, many=True).data,
               'funds': VirtualFundsSerializer(funds).data,
               'pageNum': math.ceil(len(trades) / numPerPage)}
    return Response(context, status=status.HTTP_200_OK)


# @login_required(login_url='login')
# def profile(request, id):
#     profile = Profile.objects.using(get_database(request.user.username)).get(id=id)
#     trades = profile.trade_set.all()
#     favors = profile.favoritestock_set.all()
#     funds = profile.virtualfunds
#
#     context = {'profile': profile, 'trades': trades,
#                'funds': funds, 'favors': favors}
#     return render(request, 'user/profile.html', context)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def deregister(request):
    logout(request)
    db = get_database(request.user.username)
    Profile.objects.using(db).get(username=request.user.username).delete()
    user = User.objects.get(username=request.user.username)
    user.delete()
    return Response({"message": "Deregister successfully"}, status=status.HTTP_200_OK)
