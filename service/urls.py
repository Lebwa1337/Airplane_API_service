from django.urls import path, include
from rest_framework import routers

from service import views

router = routers.DefaultRouter()
router.register("countries", views.CountryViewSet)
router.register("cities", views.CityViewSet)
router.register("airplanes_type", views.AirplaneTypeViewSet)
router.register("airplanes", views.AirplaneViewSet)
router.register("airports", views.AirportViewSet)
router.register("routes", views.RouteViewSet)
router.register("crews", views.CrewViewSet)
router.register("flights", views.FlightViewSet)
router.register("tickets", views.TicketViewSet)
router.register("orders", views.OrderViewSet)


urlpatterns = [
    path("", include(router.urls))
]

app_name = "service"
