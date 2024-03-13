from django.db import models

from user.models import User


class Country(models.Model):
    name = models.CharField(max_length=65)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=65)
    population = models.IntegerField()
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="countries")

    def __str__(self):
        return self.name


class AirplaneType(models.Model):
    name = models.CharField(max_length=65)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=65)
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE, related_name="type")
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    def __str__(self):
        return f"Airplane {self.name} with capacity {self.rows * self.seats_in_row}"


class Airport(models.Model):
    name = models.CharField(max_length=65)
    closest_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="closest_cities")

    def __str__(self):
        return f"Airport {self.name} with nearby city:{self.closest_city}"


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="source_route")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="destination_route")
    distance = models.IntegerField()

    def __str__(self):
        return (f"Flight from {self.source.closest_city.name} "
                f"to {self.destination.closest_city.name}")


class Crew(models.Model):
    first_name = models.CharField(max_length=65)
    last_name = models.CharField(max_length=65)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="routes")
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="airplanes")
    crew = models.ManyToManyField(Crew)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return (f"{self.route},"
                f"departure time: {self.departure_time},"
                f"arrival time: {self.arrival_time}")


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="flights")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="orders")

    def __str__(self):
        return f"Row:{self.row}; Seat:{self.seat}"
