from datetime import datetime
from django.db import models
from numpy import unicode_

# Create your models here.

class Stock(models.Model):
  symbol = models.CharField(max_length=40, unique=True)
  name = models.CharField(max_length=100, null = True, blank=True)
  location = models.CharField(max_length = 100,null = True, blank=True)
  companytype = models.CharField(max_length = 100,null=True, blank=True)
  description = models.TextField(null=True,blank=True)
  homepage  = models.URLField(max_length=200, null=True,blank=True)
  iconurl = models.URLField(max_length=1200, null=True,blank=True)
  latestupdatetime = models.IntegerField(null=True, blank=True)
  latestopenprice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  latestcloseprice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  latesthighprice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  latestlowprice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  def __str__(self):
    return f"{self.symbol}-{self.name}"


class StockPrice(models.Model):
  stock = models.ForeignKey(Stock, on_delete=models.CASCADE,null=True, blank=True)
  timestamp = models.IntegerField(null=True, blank=True)
  openprice = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
  closeprice = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
  highprice = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
  lowprice = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
  
  def __str__(self):
    return f"{self.stock.symbol}-{self.timestamp}"
  