from django.db import models
from django.conf import settings
import jsonfield
from django_fsm import FSMIntegerField, transition, FSMField, get_available_FIELD_transitions, get_available_user_FIELD_transitions
# Create your models here.

class BaseModel(models.Model):
	created = models.DateTimeField(editable=False)
	updated = models.DateTimeField()

	class Meta:
		abstract = True

	def save(self, *args, **kwargs):
		if not self.id:
			self.created = timezone.now()
		self.updated = timezone.now()
		return super(BaseModel, self).save(*args, **kwargs)


class Hub(BaseModel):
	MINOR_HUB = 0
	MAJOR_HUB = 1

	hub_type_choices = (
		(MAJOR_HUB, 'MAJOR_HUB'),
		(MINOR_HUB, 'MINOR_HUB'),
	)
	name = models.CharField(max_length=50, unique=True)
	hub_type = models.IntegerField(choices=hub_type_choices, null=True, blank=True)
	address = models.CharField(max_length=50, null=True, blank=True)
	latitude = models.FloatField(null=True, blank=True)
	longitude = models.FloatField(null=True, blank=True)

	def __str__(self):
		return self.id

class SellerShops(BaseModel):
	name = models.CharField(max_length=50, unique=True)
	contact = models.CharField(max_length=20, null=False)
	address = models.CharField(max_length=50, null=True, blank=True)
	latitude = models.FloatField(null=True, blank=True)
	longitude = models.FloatField(null=True, blank=True)
	hub = models.ForeignKey(Hub, on_delete=models.CASCADE)

class Society(BaseModel):
	name = models.CharField(max_length=50, unique=True)
	address = models.CharField(max_length=50, null=True, blank=True)
	latitude = models.FloatField(null=True, blank=True)
	longitude = models.FloatField(null=True, blank=True)
	mygate_id = models.IntegerField(null=True, blank=True)
	hub = models.ForeignKey(Hub, on_delete=models.CASCADE)

class Transporter(BaseModel):
	name = models.CharField(max_length=50, unique=True)
	contact = models.CharField(max_length=50, null=False)
	cost = models.IntegerField(null=True, blank=True)
	start_times = jsonfield.JSONField(max_length=500, default={}, blank=True, null=True)
	travel_time = models.IntegerField(null=True, blank=True)
	vehicle_number = models.CharField(max_length=20, unique=True)

class Order(BaseModel):
	NEW = 0
	SELLER_ACCEPTED = 1
	SELLER_IN_TRANSIT = 2
	RECEIVED_AT_HUB = 3
	TRANSIT_WITHIN_HUBS = 4
	RECEIVED_AT_DESTINATION_HUB = 5
	DELIVERED = 6

	status_choices = (
		(NEW, 'New'),
		(SELLER_ACCEPTED, 'Seller Received Order'),
		(SELLER_IN_TRANSIT, 'Seller On the Way'),
		(RECEIVED_AT_HUB, 'Order Received at Hub'),
		(TRANSIT_WITHIN_HUBS, 'Order transit within hubs'),
		(RECEIVED_AT_DESTINATION_HUB, 'Order Received at Destination Hub'),
		(DELIVERED, 'Order Delivered')
		)

	order_number = models.CharField(max_length=50, unique=True)
	seller_shop = models.ForeignKey(SellerShops, on_delete=models.CASCADE)
	society = models.ForeignKey(Society, on_delete=models.CASCADE)
	current_hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
	order_status = FSMIntegerField(choices=status_choices, default=0, db_index=True)


class Tracking(BaseModel):
	order = models.ForeignKey(Order,on_delete=models.CASCADE)
	status = models.IntegerField(choices=Order.status_choices)
