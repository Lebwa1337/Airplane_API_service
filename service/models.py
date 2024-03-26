import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.text import slugify

from user.models import User


class Country(models.Model):
    name = models.CharField(max_length=65)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=65)
    population = models.IntegerField()
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")

    def __str__(self):
        return self.name


class AirplaneType(models.Model):
    name = models.CharField(max_length=65)

    def __str__(self):
        return self.name


def create_custom_path(instance, filename):
    _, extension = os.path.splitext(filename)
    return os.path.join(
        "uploads", "img",
        f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"
    )


class Airplane(models.Model):
    name = models.CharField(max_length=65)
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE, related_name="airplanes")
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    image = models.ImageField(
        upload_to=create_custom_path,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=65)
    closest_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="airports")

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="source_routes")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="destination_routes")
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.distance}"


class Crew(models.Model):
    first_name = models.CharField(max_length=65)
    last_name = models.CharField(max_length=65)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="flights")
    crew = models.ManyToManyField(Crew)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return (f"{self.departure_time},"
                f"{self.arrival_time}")


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        constraints = [
            UniqueConstraint(fields=["row", "seat", "flight"], name="unique_tickets"),
        ]

    @staticmethod
    def validate_ticket(row, seat, airplane):
        if not (1 <= row <= airplane.rows):
            raise ValidationError(f"Incorrect row. Row must be between "
                                  f"1 and {airplane.rows} for this flight")
        if not (1 <= seat <= airplane.seats_in_row):
            raise ValidationError(f"Incorrect seat. Row must be between "
                                  f"1 and {airplane.seats_in_row} for this flight")

    def clean(self):
        Ticket.validate_ticket(self.row, self.seat, self.flight.airplane)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"Row:{self.row}; Seat:{self.seat}"
