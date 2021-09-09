# Generated by Django 3.2.7 on 2021-09-07 11:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('single_day_delivery', '0007_alter_user_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False)),
                ('updated', models.DateTimeField()),
                ('bin_category', models.IntegerField(choices=[(0, 'Minor to Major'), (1, 'Major to Major'), (2, 'Major to Minor')], default=0)),
                ('bin_origin_hub', models.IntegerField(blank=True, null=True)),
                ('bin_destination_hub', models.IntegerField(blank=True, null=True)),
                ('current_capacity', models.IntegerField(default=0)),
            ],
            options={
                'unique_together': {('bin_origin_hub', 'bin_destination_hub')},
            },
        ),
        migrations.CreateModel(
            name='BinBagMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False)),
                ('updated', models.DateTimeField()),
                ('bin_id', models.IntegerField()),
                ('bag_id', models.IntegerField()),
                ('active', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False)),
                ('updated', models.DateTimeField()),
                ('cost', models.IntegerField(blank=True, null=True)),
                ('filling_time', models.IntegerField(blank=True, null=True)),
                ('capacity', models.IntegerField(blank=True, null=True)),
                ('vehicle_number', models.CharField(max_length=20, unique=True)),
                ('current_hub_id', models.IntegerField()),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='single_day_delivery.user')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VehicleTransitDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False)),
                ('updated', models.DateTimeField()),
                ('transit_time', models.DateTimeField(editable=False)),
                ('received_time', models.DateTimeField(editable=False)),
                ('origin', models.IntegerField(blank=True, null=True)),
                ('destination', models.IntegerField(blank=True, null=True)),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='single_day_delivery.vehicle')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='Transporter',
        ),
        migrations.AddField(
            model_name='bag',
            name='weight',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='expected_delivery_hour',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='weight',
            field=models.FloatField(default=0, null=True),
        ),
    ]