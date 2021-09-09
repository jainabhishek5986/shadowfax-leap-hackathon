from django.db import models
from django.conf import settings
from django.db.models.deletion import RestrictedError
from django.utils import timezone
import jsonfield
from django_fsm import FSMIntegerField, transition, FSMField, get_available_FIELD_transitions, get_available_user_FIELD_transitions
# Create your models here.

class Constants(models.Model):
	name = models.CharField(max_length=50, unique=True)
	value = jsonfield.JSONField(default={})

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
	HUB_INCHARGE = 0
	CUSTOMER = 1
	TRANSIT_PARTNER = 2
	DELIVERY_PARTNER = 3
	SHOP_PARTNER = 4
	SOCIETY_PARTNER = 5

	user_type_choices = (
		(HUB_INCHARGE, 'Hub Incharge'),
		(CUSTOMER, 'Customer'),
		(TRANSIT_PARTNER, 'Driver'),
		(DELIVERY_PARTNER, 'Delivery Partner'),
		(SHOP_PARTNER, 'Shop Partner'),
		(SOCIETY_PARTNER, 'Society Partner')
	)

	partner_type_choices = (
		(TRANSIT_PARTNER, 'Driver'),
		(DELIVERY_PARTNER, 'Delivery Partner'),
		(SHOP_PARTNER, 'Shop Partner'),
		(SOCIETY_PARTNER, 'Society Partner')
	)

	name = models.CharField(max_length=50)
	user_type = models.IntegerField(choices=user_type_choices, null=True, blank=True)
	location_id = models.IntegerField(null=True, blank=True)
	address = models.CharField(max_length=100, null=True, blank=True)
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
	pincode = models.IntegerField(max_length=6, null=True, blank=True)

	def __str__(self):
		return self.name

class SellerShops(BaseModel):
	name = models.CharField(max_length=50, unique=False)
	contact = models.CharField(max_length=20, null=False)
	address = models.CharField(max_length=100, null=True, blank=True)
	latitude = models.FloatField(null=True, blank=True)
	longitude = models.FloatField(null=True, blank=True)
	partner_id = models.IntegerField(null=True, blank=True)
	hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
	pincode = models.IntegerField(max_length=6, null=True, blank=True)

	def __str__(self):
		return self.name

class Society(BaseModel):
	name = models.CharField(max_length=50, unique=True)
	address = models.CharField(max_length=100, null=True, blank=True)
	latitude = models.FloatField(null=True, blank=True)
	longitude = models.FloatField(null=True, blank=True)
	mygate_id = models.IntegerField(null=True, blank=True)
	partner_id = models.IntegerField(null=True, blank=True)
	hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
	pincode = models.IntegerField(max_length=6, null=True, blank=True)

	def __str__(self):
		return self.name

class Vehicle(BaseModel):
	partner = models.ForeignKey(User, on_delete=models.CASCADE)
	cost = models.IntegerField(null=True, blank=True)
	filling_time = models.IntegerField(null=True, blank=True)
	capacity = models.IntegerField(null=True, blank=True)
	vehicle_number = models.CharField(max_length=20, unique=True)
	current_hub_id = models.IntegerField(null=False)

	def __str__(self):
		return self.vehicle_number

class VehicleTransitDetails(BaseModel):
	vehicle_number = models.CharField(max_length=20)
	transit_time = models.DateTimeField(editable=False, null=True)
	received_time = models.DateTimeField(editable=False, null=True)
	origin = models.IntegerField(null=True, blank=True)
	destination = models.IntegerField(null=True, blank=True)

class VehicleBagMapping(BaseModel):
	bag_code = models.CharField(max_length=10)
	vehicle_number = models.CharField(max_length=20)
	status = models.BooleanField(default=True)

class BinBagMapping(BaseModel):
	bin_id = models.IntegerField(null=False)
	bag_id = models.IntegerField(null=False)
	active = models.IntegerField(null=False, default=1)

	class Meta:
		unique_together = ('bin_id', 'bag_id')

class Bin(BaseModel):
	MINOR_TO_MAJOR = 0
	MAJOR_TO_MAJOR = 1
	MAJOR_TO_MINOR = 2

	bin_type_choices = (
		(MINOR_TO_MAJOR, 'Minor to Major'),
		(MAJOR_TO_MAJOR, 'Major to Major'),
		(MAJOR_TO_MINOR, 'Major to Minor')
	)

	bin_category = models.IntegerField(choices=bin_type_choices, default=MINOR_TO_MAJOR)
	bin_origin_hub = models.IntegerField(null=True, blank=True)
	bin_destination_hub = models.IntegerField(null=True, blank=True)
	current_capacity = models.FloatField(default=0.0, null=True, blank=True)

	def get_hub_name(self, hub_id):
		return Hub.objects.get(id=hub_id).name

	def __str__(self):
		return self.get_bin_category_display() + self.get_hub_name(self.bin_origin_hub) + "to" + self.get_hub_name(self.bin_destination_hub)

	class Meta:
		unique_together = ('bin_origin_hub', 'bin_destination_hub')

	def save(self, *args, **kwargs):
		from .tasks import get_current_capacity_bin
		self.current_capacity = get_current_capacity_bin(self)
		super(Bin, self).save(*args, **kwargs)

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
	weight = models.FloatField(null=True, default=0)
	current_hub_id = models.IntegerField(null=True, blank = True)

	@transition(field=status, source=[NEW, RECEIVED], target=IN_TRANSIT)
	def to_transit(self):
		from .tasks import update_weight_after_bag_transit
		update_weight_after_bag_transit(self)

	@transition(field=status, source=[IN_TRANSIT], target=RECEIVED)
	def to_received(self, current_hub_id):
		from .tasks import allocate_bin_to_bag, inactivate_current_mapping
		self.current_hub_id = current_hub_id
		inactivate_current_mapping(self.id)
		allocate_bin_to_bag(self.id, current_hub_id)

	@transition(field=status, source=[RECEIVED], target=CLOSED)
	def to_closed(self):
		pass

	def save(self, *args, **kwargs):
		from .tasks import update_weight_capacity_bag
		self.weight = update_weight_capacity_bag(self)
		super(Bag, self).save(*args, **kwargs)

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
	partner_type = models.IntegerField(choices=User.partner_type_choices, null=True, blank=True)
	partner_id = models.IntegerField(null=True, blank=True)
	expected_delivery_hour = models.IntegerField(null=True, blank=True)
	weight = models.FloatField(null=True, default=0)

	@transition(field=order_status, source=NEW, target=SELLER_RECEIVED)
	def to_seller_received(self):
		pass

	@transition(field=order_status, source=[SELLER_RECEIVED, RECEIVED_AT_HUB], target=IN_TRANSIT)
	def to_transit(self, partner_details={}):
		self.partner_id = partner_details.get("partner_id", None)
		self.partner_type = partner_details.get("partner_type", None)

	@transition(field=order_status, source=[IN_TRANSIT], target=RECEIVED_AT_HUB)
	def to_received_at_hub(self, bag_receive=False):
		self.partner_id = None
		self.partner_type = None 
		from .tasks import allocate_bin_to_bag
		if not bag_receive:
			allocate_bin_to_bag(self.bag_id, self.current_hub_id)

	@transition(field=order_status, source=RECEIVED_AT_HUB, target=OFD)
	def to_ofd(self, partner_details={}):
		self.partner_id = partner_details.get("partner_id", None)
		self.partner_type = partner_details.get("partner_type", None)
		pass

	@transition(field=order_status, source=OFD, target=DELIVERED)
	def to_delivered(self):
		pass

	def get_status_display(self):
		for status in self.status_choices:
			if status[0]==self.order_status:
				return status[1]

	def save(self,location_name = None, *args, **kwargs,):
		super(Order, self).save(*args, **kwargs)
		from .tasks import create_entry_in_tracking
		create_entry_in_tracking(self, location_name)

class Tracking(BaseModel):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	status = models.IntegerField(choices=Order.status_choices)
	current_location_name = models.CharField(null = True, blank = True, max_length= 50)

