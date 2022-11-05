from collections import OrderedDict

from rest_framework import serializers
from rest_framework.reverse import reverse

from ontrack.market.models.lookup import (
    Equity,
    Exchange,
    MarketDay,
    MarketDayCategory,
    MarketDayType,
)

numeric_field_values = {
    "max_digits": 18,
    "decimal_places": 4,
}


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


class TradableEntitySerializer(serializers.Serializer):
    date = serializers.DateTimeField(read_only=True)
    prev_close = serializers.DecimalField(**numeric_field_values, read_only=True)
    open_price = serializers.DecimalField(**numeric_field_values, read_only=True)
    high_price = serializers.DecimalField(**numeric_field_values, read_only=True)
    low_price = serializers.DecimalField(**numeric_field_values, read_only=True)
    last_price = serializers.DecimalField(**numeric_field_values, read_only=True)
    close_price = serializers.DecimalField(**numeric_field_values, read_only=True)
    avg_price = serializers.DecimalField(**numeric_field_values, read_only=True)
    point_changed = serializers.DecimalField(**numeric_field_values, read_only=True)
    percentage_changed = serializers.DecimalField(
        **numeric_field_values, read_only=True
    )
    open_high = serializers.BooleanField(read_only=True)
    open_low = serializers.BooleanField(read_only=True)
    central_pivot_range = serializers.DecimalField(
        **numeric_field_values, read_only=True
    )
    top_central_pivot = serializers.DecimalField(**numeric_field_values, read_only=True)
    pivot = serializers.DecimalField(**numeric_field_values, read_only=True)
    bottom_central_pivot = serializers.DecimalField(
        **numeric_field_values, read_only=True
    )
    resistance_3 = serializers.DecimalField(**numeric_field_values, read_only=True)
    resistance_2 = serializers.DecimalField(**numeric_field_values, read_only=True)
    resistance_1 = serializers.DecimalField(**numeric_field_values, read_only=True)
    support_1 = serializers.DecimalField(**numeric_field_values, read_only=True)
    support_2 = serializers.DecimalField(**numeric_field_values, read_only=True)
    support_3 = serializers.DecimalField(**numeric_field_values, read_only=True)
    traded_quantity = serializers.DecimalField(**numeric_field_values, read_only=True)
    traded_value = serializers.DecimalField(**numeric_field_values, read_only=True)
    number_of_trades = serializers.DecimalField(**numeric_field_values, read_only=True)
    quantity_per_trade = serializers.DecimalField(
        **numeric_field_values, read_only=True
    )


class EquityDetailsSerializer(NonNullModelSerializer):
    price_info = serializers.SerializerMethodField(read_only=True)

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
            "price_info",
        ]

    def get_price_info(self, obj):
        eod_data = obj.eod_data.order_by("-date").first()
        return TradableEntitySerializer(eod_data).data


class EquityListCreateSerializer(NonNullModelSerializer):
    details_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Equity
        fields = [
            "id",
            "name",
            "symbol",
            "chart_symbol",
            "slug",
            "isin_number",
            "industry",
            "exchange",
            "details_url",
            "average_delivery_quantity",
        ]

    def get_details_url(self, obj):
        request = self.context.get("request")  # self.request
        if request is None:
            return None
        return reverse(
            "api_market:equity-detail",
            kwargs={"slug__iexact": obj.slug},
            request=request,
        )
