from django.db.models import F
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from service.models import (
    Country,
    City,
    AirplaneType,
    Airplane,
    Airport,
    Crew,
    Flight,
    Ticket,
    Order,
    Route
)
from service.serializers import (
    CountrySerializer,
    CitySerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirportSerializer,
    RouteSerializer,
    CrewSerializer,
    FlightSerializer,
    TicketSerializer,
    OrderSerializer,
    AirportListRetrieveSerializer,
    CityListRetrieveSerializer,
    RouteListRetrieveSerializer,
    FlightListSerializer,
    FlightDetailSerializer, OrderListSerializer, UploadImageSerializer, AirplaneListSerializer,
)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")

        if name:
            return Country.objects.filter(name__icontains=name)
        return self.queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                description="Filter by name"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all().select_related("country")

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CityListRetrieveSerializer
        return CitySerializer

    def get_queryset(self):
        city_name = self.request.query_params.get("city_name")
        country = self.request.query_params.get("country")
        if city_name:
            return City.objects.filter(name__icontains=city_name)
        if country:
            return City.objects.filter(country__name__icontains=country)
        return self.queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="city_name",
                type=OpenApiTypes.STR,
                description="Filter by city_name"
            ),
            OpenApiParameter(
                name="country",
                type=OpenApiTypes.STR,
                description="Filter by country"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")
        if name:
            return AirplaneType.objects.filter(name__icontains=name)
        return self.queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                description="Filter by name"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().annotate(
        capacity=(F("rows") * F("seats_in_row"))
    ).select_related("airplane_type")
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return AirplaneListSerializer
        if self.action == "upload_image":
            return UploadImageSerializer
        return AirplaneSerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")
        airplane_type = self.request.query_params.get("type")
        capacity = self.request.query_params.get("capacity")
        if name:
            self.queryset = self.queryset.filter(name__icontains=name)
        if airplane_type:
            self.queryset = self.queryset.filter(airplane_type__name__icontains=airplane_type)
        if capacity:
            self.queryset = self.queryset.filter(capacity__lte=capacity)
        return self.queryset

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        plane = self.get_object()
        serializer = self.get_serializer(plane, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                description="Filter by name",
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name="type",
                description="Filter by type",
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name="capacity",
                description="Filter by capacity",
                type=OpenApiTypes.INT
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all().select_related("closest_city")

    def get_queryset(self):
        name = self.request.query_params.get("name")
        closest_city = self.request.query_params.get("city")
        if name:
            self.queryset = self.queryset.filter(name__icontains=name)
        if closest_city:
            self.queryset = self.queryset.filter(closest_city__name__icontains=closest_city)
        return self.queryset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return AirportListRetrieveSerializer
        return AirportSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                description="Filter by name"
            ),
            OpenApiParameter(
                name="city",
                type=OpenApiTypes.STR,
                description="Filter by city"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().prefetch_related(
        "source"
    )

    # TODO N+1 (Route + flight)
    def get_queryset(self):
        source_city = self.request.query_params.get("source_city")
        destination_city = self.request.query_params.get("destination_city")
        if source_city:
            self.queryset = self.queryset.filter(source__closest_city__name__icontains=source_city)
        if destination_city:
            self.queryset = self.queryset.filter(destination__closest_city__name__icontains=destination_city)
        return self.queryset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return RouteListRetrieveSerializer
        return RouteSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="source_city",
                type=OpenApiTypes.STR,
                description="Filter by source city"
            ),
            OpenApiParameter(
                name="destination_city",
                type=OpenApiTypes.STR,
                description="Filter by destination city"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all().select_related(
        "route",
        "airplane",
        "route__source"
    ).prefetch_related("crew")

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="dep_date",
                type=OpenApiTypes.DATE,
                description="Filter by source departure date"
            ),
            OpenApiParameter(
                name="dep_hour",
                type=OpenApiTypes.INT,
                description="Filter by departure hour"
            ),
            OpenApiParameter(
                name="dep_minute",
                type=OpenApiTypes.INT,
                description="Filter by departure minute"
            ),
            OpenApiParameter(
                name="arr_date",
                type=OpenApiTypes.DATE,
                description="Filter by arrival date"
            ),
            OpenApiParameter(
                name="arr_hour",
                type=OpenApiTypes.INT,
                description="Filter by arrival hour"
            ),
            OpenApiParameter(
                name="arr_minute",
                type=OpenApiTypes.INT,
                description="Filter by arrival minute"
            ),
            OpenApiParameter(
                name="s_route",
                type=OpenApiTypes.STR,
                description="Filter by source route"
            ),
            OpenApiParameter(
                name="d_route",
                type=OpenApiTypes.STR,
                description="Filter by destination route"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        dep_date = self.request.query_params.get("dep_date")
        dep_hour = self.request.query_params.get("dep_hour")
        dep_minute = self.request.query_params.get("dep_minute")

        arr_date = self.request.query_params.get("arr_date")
        arr_hour = self.request.query_params.get("arr_hour")
        arr_minute = self.request.query_params.get("arr_minute")

        s_route = self.request.query_params.get("s_route")
        d_route = self.request.query_params.get("d_route")
        if dep_date:
            self.queryset = self.queryset.filter(departure_time__date=dep_date)
        if dep_hour:
            self.queryset = self.queryset.filter(departure_time__hour=dep_hour)
        if dep_minute:
            self.queryset = self.queryset.filter(departure_time__minute=dep_minute)

        if arr_date:
            self.queryset = self.queryset.filter(arrival_time__date=arr_date)
        if arr_hour:
            self.queryset = self.queryset.filter(arrival_time__hour=arr_hour)
        if arr_minute:
            self.queryset = self.queryset.filter(arrival_time__minute=arr_minute)

        if s_route:
            self.queryset = self.queryset.filter(
                route__source__closest_city__name__icontains=s_route
            )
        if d_route:
            self.queryset = self.queryset.filter(
                route__destination__closest_city__name__icontains=d_route
            )
        return self.queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_queryset(self):
        return self.queryset.filter(order__user=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related(
        "tickets__flight",
        "tickets__flight__crew",
        "tickets__flight__route",
        "tickets__flight__airplane",
        "tickets__flight__route__source__closest_city"
    )
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="s_route",
                type=OpenApiTypes.STR,
                description="Filter by source route",
            ),
            OpenApiParameter(
                name="d_route",
                type=OpenApiTypes.STR,
                description="Filter by destination route",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        s_route = self.request.query_params.get("s_route")
        d_route = self.request.query_params.get("d_route")
        if s_route:
            self.queryset = self.queryset.filter(
                tickets__flight__route__source__closest_city__name__icontains=s_route
            )
        if d_route:
            self.queryset = self.queryset.filter(
                tickets__flight__route__destination__closest_city__name__icontains=d_route
            )
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer
