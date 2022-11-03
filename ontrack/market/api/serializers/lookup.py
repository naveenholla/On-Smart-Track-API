from collections import OrderedDict

from rest_framework import serializers

from ontrack.market.models.lookup import (
    Equity,
    Exchange,
    MarketDay,
    MarketDayCategory,
    MarketDayType,
)


class NonNullModelSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        result = super().to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None]
        )


class MarketDaySerializer(NonNullModelSerializer):
    day_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MarketDay
        fields = [
            "id",
            "day_type",
            "date",
            "day",
            "description",
            "is_working_day",
            "start_time",
            "end_time",
        ]

    def get_day_type(self, obj: Exchange):
        return obj.daytype.name


class MarketDayCategorySerializer(NonNullModelSerializer):
    days = MarketDaySerializer(many=True)

    class Meta:
        model = MarketDayCategory
        fields = [
            "id",
            "parent_name",
            "display_name",
            "code",
            "days",
        ]


class MarketDayTypeSerializer(NonNullModelSerializer):
    categories = MarketDayCategorySerializer(many=True)

    class Meta:
        model = MarketDayType
        fields = [
            "id",
            "name",
            "categories",
        ]


class ExchangeListCreateSerializer(NonNullModelSerializer):
    class Meta:
        model = Exchange
        fields = ["id", "name", "symbol", "start_time", "end_time", "data_refresh_time"]


class ExchangeDetailsSerializer(NonNullModelSerializer):
    holiday_categories = MarketDayCategorySerializer(many=True)
    timezone = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Exchange
        fields = [
            "id",
            "name",
            "symbol",
            "start_time",
            "end_time",
            "data_refresh_time",
            "timezone",
            "holiday_categories",
        ]

    def get_timezone(self, obj: Exchange):
        return obj.timezone_name


class EquityListCreateSerializer(NonNullModelSerializer):
    class Meta:
        model = Equity
        fields = [
            "id",
            "name",
            "symbol",
            "chart_symbol",
            "slug",
            "lot_size",
            "date",
            "isin_number",
            "industry",
            "exchange",
        ]
