from django.db import models
from django.conf import settings
from django.db.models.deletion import RestrictedError
from django.utils import timezone
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

class User(BaseModel):
	CUSTOMER = 0
	SELLER = 1
	TRUCK_DRIVER = 2
	RIDER = 3

	user_type = (
		(CUSTOMER, 'CUSTOMER'),
		(SELLER, 'SELLER'),
		(TRUCK_DRIVER, 'TRUCK_DRIVER'),
		(RIDER, 'RIDER')
	)
	name = models.CharField(max_length=50, unique=True)
	type = models.IntegerField(choices=user_type, null=True, blank=True)
	society = models.ForeignKey("Society", on_delete=models.CASCADE, null=True, blank=True)
	address = models.CharField(max_length=50, null=True, blank=True)
	latitude = models.FloatField(null=True, blank=True)
	longitude = models.FloatField(null=True, blank=True)
	phone_number = models.IntegerField(max_length=10, null=True, blank=True)

	def __str__(self):
		return self.name

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
	major_hub = models.ForeignKey("Hub", on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return self.name

class SellerShops(BaseModel):
	name = models.CharField(max_length=50, unique=True)
	contact = models.CharField(max_length=20, null=False)
	address = models.CharField(max_length=50, null=True, blank=True)
	latitude = models.FloatField(null=True, blank=True)
	longitude = models.FloatField(null=True, blank=True)
	delivery_partner = models.BooleanField()
	hub = models.ForeignKey(Hub, on_delete=models.CASCADE)

	def __str__(self):
		return self.name

class Society(BaseModel):
	name = models.CharField(max_length=50, unique=True)
	address = models.CharField(max_length=50, null=True, blank=True)
	latitude = models.FloatField(null=True, blank=True)
	longitude = models.FloatField(null=True, blank=True)
	mygate_id = models.IntegerField(null=True, blank=True)
	delivery_partner = models.BooleanField()
	hub = models.ForeignKey(Hub, on_delete=models.CASCADE)

	def __str__(self):
		return self.name

class Transporter(BaseModel):
	name = models.CharField(max_length=50, unique=True)
	contact = models.CharField(max_length=50, null=False)
	cost = models.IntegerField(null=True, blank=True)
	start_times = jsonfield.JSONField(max_length=500, default={}, blank=True, null=True)
	travel_time = models.IntegerField(null=True, blank=True)
	vehicle_number = models.CharField(max_length=20, unique=True)


class Bag(BaseModel):
	NEW = 0
	IN_TRANSIT = 1
	RECEIVED = 2
	CLOSED = 3

	UPSTREAM = 0
	DOWNSTREAM = 1

	bag_type_choices = (
		(UPSTREAM, 'Forward'),
		(DOWNSTREAM, 'Reverse')
		)

	status_choices = (
		(NEW, 'New'),
		(IN_TRANSIT, 'In Transit'),
		(RECEIVED, 'Bag Received')
		)

	SOCIETY = 0
	HUB = 1

	destination_type_choices = (
		(SOCIETY, 'Society'),
		(HUB, 'Hub')
		)

	code = models.CharField(max_length=50, unique=True)
	bag_type = models.IntegerField(choices = bag_type_choices, default = UPSTREAM)
	origin = models.IntegerField(null=True, blank=True)
	destination = models.IntegerField(null=True, blank = True)
	destination_type = models.IntegerField(choices= destination_type_choices, default=1)
	status = FSMIntegerField(choices=status_choices, default=0, db_index=True)

	@transition(field=status, source=[NEW, RECEIVED], target=IN_TRANSIT)
	def to_transit(self):
		pass

	@transition(field=status, source=[IN_TRANSIT], target=RECEIVED)
	def to_received(self):
		pass

	@transition(field=status, source=[RECEIVED], target=CLOSED)
	def to_closed(self):
		pass

class Order(BaseModel):
	NEW = 0
	SELLER_RECEIVED = 1
	IN_TRANSIT = 2
	RECEIVED_AT_HUB = 3
	OFD = 4
	DELIVERED = 5

	status_choices = (
		(NEW, 'New'),
		(SELLER_RECEIVED, 'Seller Received Order'),
		(IN_TRANSIT, 'In Transit'),
		(RECEIVED_AT_HUB, 'Order Received at Hub'),
		(OFD, 'Out for Delivery'),
		(DELIVERED, 'Order Delivered')
		)

	order_number = models.CharField(max_length=50, unique=True)
	bag_id = models.IntegerField(null=True, blank=True)
	seller_shop = models.ForeignKey(SellerShops, on_delete=models.CASCADE)
	society = models.ForeignKey(Society, on_delete=models.CASCADE)
	current_hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
	order_status = FSMIntegerField(choices=status_choices, default=NEW, db_index=True)
	rider_assigned = models.BooleanField()

	@transition(field=rider_assigned, source=False, target=True)
	def rider_assigned_to_order(self):
		pass

	@transition(field=order_status, source=NEW, target=SELLER_RECEIVED)
	def to_seller_received(self):
		pass

	@transition(field=order_status, source=[SELLER_RECEIVED, RECEIVED_AT_HUB], target=IN_TRANSIT)
	def to_transit(self):
		pass

	@transition(field=order_status, source=[IN_TRANSIT], target=RECEIVED_AT_HUB)
	def to_received_at_hub(self):
		pass

	@transition(field=order_status, source=RECEIVED_AT_HUB, target=OFD)
	def to_ofd(self):
		pass

	@transition(field=order_status, source=OFD, target=DELIVERED)
	def to_delivered(self):
		pass

	def get_status_display(self):
		for status in status_choices:
			if status[0]==self.order_status:
				return status[1]

	def save(self, *args, **kwargs):
		super(Order, self).save(*args, **kwargs)
		from .tasks import create_entry_in_tracking
		create_entry_in_tracking(self)

class Tracking(BaseModel):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	status = models.IntegerField(choices=Order.status_choices)

