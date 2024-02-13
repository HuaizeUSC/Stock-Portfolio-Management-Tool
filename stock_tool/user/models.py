from tokenize import blank_re
import black
from django.db import models
from django.contrib.auth.models import User
from matplotlib.pyplot import cla
from traitlets import default
# Create your models here.
from stock.models import Stock, StockPrice
import uuid


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(max_length=500, blank=True, null=True)
    username = models.CharField(max_length=200, blank=True, null=True)

    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    def __str__(self):
        return str(self.username)


class Trade(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    stockinfo = models.ForeignKey(
        StockPrice, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField()

    def __str__(self):
        return f'Trade of {str(self.owner.username)} for {str(self.stockinfo.stock.symbol)}'


class FavoriteStock(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)

    def __str__(self):
        return f'{str(self.owner.username)} favors {str(self.stock.symbol)}'


class VirtualFunds(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)
    balance = models.DecimalField(
        max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username}'s Virtual Funds"
