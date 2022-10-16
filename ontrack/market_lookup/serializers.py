from rest_framework import serializers

from .models import MarketDay, MarketDayCategory, MarketDayType, MarketExchange


class MarketDaySerilizer(serializers.ModelSerializer):
    class Meta:
        model = MarketDay
        fields = "__all__"


class MarketDayCategorySerilizer(serializers.ModelSerializer):
    days = MarketDaySerilizer(many=True)

    class Meta:
        model = MarketDayCategory
        fields = "__all__"


class MarketDayTypeSerilizer(serializers.ModelSerializer):
    categories = MarketDayCategorySerilizer(many=True)

    class Meta:
        model = MarketDayType
        fields = "__all__"


class MarketExchangeSerilizer(serializers.ModelSerializer):
    day_types = MarketDayTypeSerilizer(many=True)

    class Meta:
        model = MarketExchange
        fields = "__all__"
