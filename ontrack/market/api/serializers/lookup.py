from rest_framework import serializers

from ontrack.market.models.lookup import (
    Exchange,
    MarketDay,
    MarketDayCategory,
    MarketDayType,
)


class MarketDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketDay
        fields = "__all__"


class MarketDayCategorySerializer(serializers.ModelSerializer):
    days = MarketDaySerializer(many=True)

    class Meta:
        model = MarketDayCategory
        fields = "__all__"


class MarketDayTypeSerializer(serializers.ModelSerializer):
    categories = MarketDayCategorySerializer(many=True)

    class Meta:
        model = MarketDayType
        fields = "__all__"


class ExchangeSerializer(serializers.ModelSerializer):
    day_types = MarketDayTypeSerializer(many=True)

    class Meta:
        model = Exchange
        fields = "__all__"
