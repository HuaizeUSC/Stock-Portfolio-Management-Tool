from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

urlpatterns = [
    path('register/', views.registeUser, name='register'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('trades/<int:pageNum>/<int:numPerPage>/', views.trades, name='profile'),
    path('favors/<int:pageNum>/<int:numPerPage>/', views.favors, name='profile'),
    path('deleteFavor/<str:symbol>/', views.deleteFavor, name='deleteFavor'),
    path('deregister/', views.deregister, name='deregister'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
