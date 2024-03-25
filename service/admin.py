from django.contrib import admin

from service.models import (
    AirplaneType,
    Airplane,
    Crew,
    Route,
    Airport,
    Ticket,
    Order,
    Flight,
    Country,
    City,
)

admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Crew)
admin.site.register(Route)
admin.site.register(Airport)
admin.site.register(Ticket)
admin.site.register(Order)
admin.site.register(Flight)
admin.site.register(Country)
admin.site.register(City)
