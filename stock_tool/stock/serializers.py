from rest_framework import serializers
from .models import Stock, StockPrice


class StockWithFavorSerializer(serializers.ModelSerializer):
    favor = serializers.BooleanField()
    class Meta:
        model = Stock
        fields = ['symbol', 'name', 'location', 'companytype', 'description', 'homepage', 'iconurl', 'latestupdatetime',
         'latestopenprice', 'latestcloseprice', 'latesthighprice', 'latestlowprice', 'favor']


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'


class StockPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockPrice
        fields = '__all__'
