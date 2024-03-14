from django.db import transaction
from django.utils.text import slugify
from rest_framework import serializers

from service.models import (
    Country,
    City,
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Crew,
    Flight,
    Ticket,
    Order
)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ["name", "population", "country"]


class CityListRetrieveSerializer(CitySerializer):
    country = serializers.CharField(source='country.name', read_only=True)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = "__all__"


class UploadImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ["id", "image"]


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = serializers.CharField(source='airplane_type.name', read_only=True)
    capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Airplane
        fields = ["name", "airplane_type", "rows", "seats_in_row", "capacity", "image"]


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "name", "closest_city"]


class AirportListRetrieveSerializer(AirportSerializer):
    closest_city = serializers.CharField(
        source='closest_city.name',
        read_only=True
    )


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["id", "distance", "source", "destination"]


class RouteListRetrieveSerializer(RouteSerializer):
    source = serializers.StringRelatedField()
    destination = serializers.StringRelatedField()


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name", "full_name"]


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = [
            "id",
            "departure_time",
            "arrival_time",
            "route",
            "airplane",
            "crew"
        ]


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField(read_only=True)
    airplane = serializers.CharField(source="airplane.name", read_only=True)
    crew = serializers.SlugRelatedField(
        many=True,
        slug_field="full_name",
        read_only=True
    )


class FlightDetailSerializer(FlightListSerializer):
    airplane = AirplaneSerializer(read_only=True)
    route = RouteListRetrieveSerializer(read_only=True)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "seat", "row", "flight"]


class TicketListSerializer(TicketSerializer):
    movie_session = FlightListSerializer(many=False, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ["id", "created_at", "tickets"]

    def create(self, validated_data):
        with transaction.atomic():
            tickets = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket in tickets:
                Ticket.objects.create(order=order, **ticket)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
