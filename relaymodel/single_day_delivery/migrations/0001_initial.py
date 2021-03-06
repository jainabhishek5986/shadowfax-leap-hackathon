# Generated by Django 3.2.7 on 2021-09-04 11:02

from django.db import migrations, models
import django.db.models.deletion
import django_fsm
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hub',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False)),
                ('updated', models.DateTimeField()),
                ('name', models.CharField(max_length=50, unique=True)),
                ('hub_type', models.IntegerField(blank=True, choices=[(1, 'MAJOR_HUB'), (0, 'MINOR_HUB')], null=True)),
                ('address', models.CharField(blank=True, max_length=50, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False)),
                ('updated', models.DateTimeField()),
                ('order_number', models.CharField(max_length=50, unique=True)),
                ('order_status', django_fsm.FSMIntegerField(choices=[(0, 'New'), (1, 'Seller Received Order'), (2, 'Seller On the Way'), (3, 'Order Received at Hub'), (4, 'Order transit within hubs'), (5, 'Order Received at Destination Hub'), (6, 'Order Delivered')], db_index=True, default=0)),
                ('current_hub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='single_day_delivery.hub')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transporter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False)),
                ('updated', models.DateTimeField()),
                ('name', models.CharField(max_length=50, unique=True)),
                ('contact', models.CharField(max_length=50)),
                ('cost', models.IntegerField(blank=True, null=True)),
                ('start_times', jsonfield.fields.JSONField(blank=True, default={}, max_length=500, null=True)),
                ('travel_time', models.IntegerField(blank=True, null=True)),
                ('vehicle_number', models.CharField(max_length=20, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tracking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False)),
                ('updated', models.DateTimeField()),
                ('status', models.IntegerField(choices=[(0, 'New'), (1, 'Seller Received Order'), (2, 'Seller On the Way'), (3, 'Order Received at Hub'), (4, 'Order transit within hubs'), (5, 'Order Received at Destination Hub'), (6, 'Order Delivered')])),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='single_day_delivery.order')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Society',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False)),
                ('updated', models.DateTimeField()),
                ('name', models.CharField(max_length=50, unique=True)),
                ('address', models.CharField(blank=True, max_length=50, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('mygate_id', models.IntegerField(blank=True, null=True)),
                ('hub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='single_day_delivery.hub')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SellerShops',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False)),
                ('updated', models.DateTimeField()),
                ('name', models.CharField(max_length=50, unique=True)),
                ('contact', models.CharField(max_length=20)),
                ('address', models.CharField(blank=True, max_length=50, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('hub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='single_day_delivery.hub')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='order',
            name='seller_shop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='single_day_delivery.sellershops'),
        ),
        migrations.AddField(
            model_name='order',
            name='society',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='single_day_delivery.society'),
        ),
    ]
