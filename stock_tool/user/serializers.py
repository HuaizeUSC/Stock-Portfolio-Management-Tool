from rest_framework import serializers
from .models import Profile, Trade, FavoriteStock, VirtualFunds


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = '__all__'


class FavoriteStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteStock
        fields = '__all__'


class VirtualFundsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualFunds
        fields = '__all__'
