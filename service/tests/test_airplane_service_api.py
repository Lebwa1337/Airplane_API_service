import os
import tempfile
from datetime import datetime

from PIL import Image
from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from service.models import (
    AirplaneType,
    Airplane,
    Country,
    City,
    Route,
    Crew,
    Flight,
    Airport,
    Ticket,
    Order,
)
from service.serializers import (
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
)

AIRPLANE_URL = reverse("service:airplane-list")


def sample_airplane_type(**params):
    defaults = {"name": "test_airplane_type"}
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params):
    defaults = {
        "name": "test_airplane",
        "airplane_type": sample_airplane_type(),
        "rows": 10,
        "seats_in_row": 10,
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


def sample_city(**params):
    defaults = {
        "name": "test_city",
        "population": 100,
        "country": Country.objects.create(name="test_country"),
    }
    defaults.update(params)
    return City.objects.create(**defaults)


def sample_airport(**params):
    defaults = {"name": "test_airport", "closest_city": sample_city()}
    defaults.update(params)
    return Airport.objects.create(**defaults)


def image_upload_url(airplane_id):
    return reverse("service:airplane-upload-image", args=[airplane_id])


def airplane_detail_url(airplane_id):
    return reverse("service:airplane-detail", args=[airplane_id])


class MovieImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.airplane_type = sample_airplane_type()
        self.airplane = sample_airplane()

    def tearDown(self):
        self.airplane.image.delete()

    def test_upload_image_to_airplane(self):
        """Test uploading an image to movie"""
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.airplane.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airplane.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.airplane.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_image_url_is_shown_on_airplane_detail(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(airplane_detail_url(self.airplane.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_airplane_list(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(AIRPLANE_URL)

        self.assertIn("image", res.data[0].keys())


class UnauthorizedTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(AIRPLANE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "testpassword123"
        )
        self.client.force_authenticate(self.user)

        self.route = Route.objects.create(
            source=sample_airport(), destination=sample_airport(), distance=5000
        )
        self.airplane = sample_airplane()
        self.crew = Crew.objects.create(first_name="test_f", last_name="test_l")
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=datetime.now(),
            arrival_time=datetime.now(),
        )
        self.flight.crew.add(self.crew)

    def test_list_flight(self):
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(flight=self.flight, row=10, seat=10, order=order)
        flights = Flight.objects.all().annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")
            )
        )
        res = self.client.get(reverse("service:flight-list"))
        serializer = FlightListSerializer(flights, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_flight_query_params_departure_date_filtering(self):
        flight1 = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=datetime(2024, 2, 15, 10, 30, 0),
            arrival_time=datetime(2024, 2, 16, 11, 35, 0),
        )
        flight1.crew.add(self.crew)
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(flight=flight1, row=10, seat=10, order=order)
        flight2 = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=datetime(2023, 5, 10, 15, 50, 0),
            arrival_time=datetime(2023, 5, 1, 16, 55, 0),
        )
        flight2.crew.add(self.crew)
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(flight=flight2, row=10, seat=10, order=order)
        flights = (
            Flight.objects.all()
            .annotate(
                tickets_available=(
                    F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")
                )
            )
            .filter(departure_time__date="2024-02-15")
        )
        query_res = self.client.get(
            reverse("service:flight-list"), {"dep_date": "2024-02-15"}
        )
        serializer1 = FlightListSerializer(flights, many=True)
        serializer2 = FlightSerializer(flight2)

        self.assertEqual(query_res.status_code, status.HTTP_200_OK)
        self.assertNotEqual(query_res.data, serializer2.data)
        self.assertEqual(query_res.data, serializer1.data)

    def test_flight_query_params_arrival_date_filtering(self):
        flight1 = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=datetime(2024, 2, 15, 10, 30, 0),
            arrival_time=datetime(2024, 2, 16, 11, 35, 0),
        )
        flight1.crew.add(self.crew)
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(flight=flight1, row=10, seat=10, order=order)
        flight2 = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=datetime(2023, 5, 10, 15, 50, 0),
            arrival_time=datetime(2023, 5, 1, 16, 55, 0),
        )
        flight2.crew.add(self.crew)
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(flight=flight2, row=10, seat=10, order=order)
        flights = (
            Flight.objects.all()
            .annotate(
                tickets_available=(
                    F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")
                )
            )
            .filter(arrival_time__date="2024-02-16")
        )
        query_res = self.client.get(
            reverse("service:flight-list"), {"arr_date": "2024-02-16"}
        )
        serializer1 = FlightListSerializer(flights, many=True)
        serializer2 = FlightSerializer(flight2)

        self.assertEqual(query_res.status_code, status.HTTP_200_OK)
        self.assertNotEqual(query_res.data, serializer2.data)
        self.assertEqual(query_res.data, serializer1.data)

    def test_flight_retrieve(self):

        order = Order.objects.create(user=self.user)
        Ticket.objects.create(flight=self.flight, row=10, seat=10, order=order)
        flights = Flight.objects.first()

        res = self.client.get(reverse("service:flight-detail", args=[flights.id]))
        serializer = FlightDetailSerializer(flights)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_ticket_forbidden(self):
        order = Order.objects.create(user=self.user)
        payload = {"flight": self.flight, "row": 10, "seat": 10, "order": order}
        res = self.client.post(reverse("service:ticket-list"), payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
