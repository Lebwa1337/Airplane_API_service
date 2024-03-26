# Generated by Django 4.2 on 2024-03-26 18:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("service", "0003_alter_airplane_airplane_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flight",
            name="airplane",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="flights",
                to="service.airplane",
            ),
        ),
        migrations.AlterField(
            model_name="flight",
            name="route",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="flights",
                to="service.route",
            ),
        ),
        migrations.AlterField(
            model_name="route",
            name="destination",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="destination_routes",
                to="service.airport",
            ),
        ),
        migrations.AlterField(
            model_name="route",
            name="source",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="source_routes",
                to="service.airport",
            ),
        ),
        migrations.AlterField(
            model_name="ticket",
            name="flight",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tickets",
                to="service.flight",
            ),
        ),
        migrations.AlterField(
            model_name="ticket",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tickets",
                to="service.order",
            ),
        ),
        migrations.AddConstraint(
            model_name="ticket",
            constraint=models.UniqueConstraint(
                fields=("row", "seat", "flight"), name="unique_tickets"
            ),
        ),
    ]
