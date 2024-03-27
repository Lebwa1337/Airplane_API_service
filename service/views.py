from django.db.models import F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, mixins, permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

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
    FlightDetailSerializer,
    OrderListSerializer,
    UploadImageSerializer,
    AirplaneListSerializer,
    TicketDetailSerializer,
)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get("name")

        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

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
        queryset = super().get_queryset()
        city_name = self.request.query_params.get("city_name")
        country = self.request.query_params.get("country")
        if city_name:
            queryset = queryset.filter(name__icontains=city_name)
        if country:
            queryset = queryset.filter(country__name__icontains=country)
        return queryset

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
        queryset = super().get_queryset()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

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
        queryset = super().get_queryset()
        name = self.request.query_params.get("name")
        airplane_type = self.request.query_params.get("type")
        capacity = self.request.query_params.get("capacity")
        if name:
            queryset = queryset.filter(name__icontains=name)
        if airplane_type:
            queryset = queryset.filter(airplane_type__name__icontains=airplane_type)
        if capacity:
            queryset = queryset.filter(capacity__lte=capacity)
        return queryset

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[permissions.IsAdminUser]
    )
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
        queryset = super().get_queryset()
        name = self.request.query_params.get("name")
        closest_city = self.request.query_params.get("city")
        if name:
            queryset = queryset.filter(name__icontains=name)
        if closest_city:
            queryset = queryset.filter(closest_city__name__icontains=closest_city)
        return queryset

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
    queryset = Route.objects.select_related(
        "source__closest_city",
        "destination__closest_city"
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        source_city = self.request.query_params.get("source_city")
        destination_city = self.request.query_params.get("destination_city")
        if source_city:
            queryset = queryset.filter(source__closest_city__name__icontains=source_city)
        if destination_city:
            queryset = queryset.filter(destination__closest_city__name__icontains=destination_city)
        return queryset

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
    queryset = Flight.objects.prefetch_related("crew").annotate(
        tickets_available=(F("airplane__rows") * F("airplane__seats_in_row")
                           - Count("tickets"))
    )

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
        queryset = super().get_queryset()
        dep_date = self.request.query_params.get("dep_date")
        dep_hour = self.request.query_params.get("dep_hour")
        dep_minute = self.request.query_params.get("dep_minute")

        arr_date = self.request.query_params.get("arr_date")
        arr_hour = self.request.query_params.get("arr_hour")
        arr_minute = self.request.query_params.get("arr_minute")

        s_route = self.request.query_params.get("s_route")
        d_route = self.request.query_params.get("d_route")
        if dep_date:
            queryset = queryset.filter(departure_time__date=dep_date)
        if dep_hour:
            queryset = queryset.filter(departure_time__hour=dep_hour)
        if dep_minute:
            queryset = queryset.filter(departure_time__minute=dep_minute)

        if arr_date:
            queryset = queryset.filter(arrival_time__date=arr_date)
        if arr_hour:
            queryset = queryset.filter(arrival_time__hour=arr_hour)
        if arr_minute:
            queryset = queryset.filter(arrival_time__minute=arr_minute)

        if s_route:
            queryset = queryset.filter(
                route__source__closest_city__name__icontains=s_route
            )
        if d_route:
            queryset = queryset.filter(
                route__destination__closest_city__name__icontains=d_route
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer


class TicketViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    queryset = Ticket.objects.prefetch_related(
        "flight__route__source__closest_city"
    )
    serializer_class = TicketSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(order__user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TicketDetailSerializer
        return TicketSerializer


class OrderPagination(PageNumberPagination):
    page_size = 4
    max_page_size = 100


class OrderViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin
):
    queryset = Order.objects.all().prefetch_related(
        "tickets__flight",
        "tickets__flight__crew",
        "tickets__flight__route",
        "tickets__flight__airplane",
        "tickets__flight__route__source__closest_city"
    )
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = [IsAuthenticated]

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
        queryset = super().get_queryset()
        s_route = self.request.query_params.get("s_route")
        d_route = self.request.query_params.get("d_route")
        if s_route:
            queryset = queryset.filter(
                tickets__flight__route__source__closest_city__name__icontains=s_route
            )
        if d_route:
            queryset = queryset.filter(
                tickets__flight__route__destination__closest_city__name__icontains=d_route
            )
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return OrderListSerializer

        return OrderSerializer
