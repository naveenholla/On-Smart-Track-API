from rest_framework import serializers

from ..models.lookup import Exchange, MarketDay, MarketDayCategory, MarketDayType


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


class ExchangeSerilizer(serializers.ModelSerializer):
    day_types = MarketDayTypeSerilizer(many=True)

    class Meta:
        model = Exchange
        fields = "__all__"
