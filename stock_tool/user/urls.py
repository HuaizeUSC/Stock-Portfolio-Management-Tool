from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', views.registeUser, name='register'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('profile/<str:id>', views.profile, name='profile'),
    path('deleteFavor/<str:id>/<str:symbol>', views.deleteFavor, name='deleteFavor'),
    path('deregister/<str:id>/<str:username>', views.deregister, name='deregister')
]
