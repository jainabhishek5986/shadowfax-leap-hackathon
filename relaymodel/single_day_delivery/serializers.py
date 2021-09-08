from rest_framework import serializers
from .tasks import *
from .models import *

class TrackingSerializer(serializers.ModelSerializer):
	order_number = serializers.SerializerMethodField()
	order_status = serializers.SerializerMethodField()

	def get_order_number(self, obj):
		return obj.order.order_number

	def get_order_status(self, obj):
		for status in Order.status_choices:
			if status[0]==obj.status:
				return status[1]

	class Meta:
		model = Tracking
		fields = ('updated', 'order_number', 'order_status')

class OrderSerializer(serializers.ModelSerializer):
	bag_code = serializers.SerializerMethodField()
	order_status = serializers.SerializerMethodField()
	society_name = serializers.SerializerMethodField()
	seller_name = serializers.SerializerMethodField()
	partner_name = serializers.SerializerMethodField()
	current_bin = serializers.SerializerMethodField()
	next_destination = serializers.SerializerMethodField()
	vehicle_numbers = serializers.SerializerMethodField()

	def get_bag_code(self, obj):
		if obj.bag_id:
			return Bag.objects.get(id=obj.bag_id).code
		return None

	def get_order_status(self, obj):
		return obj.get_status_display()

	def get_society_name(self, obj):
		return obj.society.name

	def get_seller_name(self, obj):
		return obj.seller_shop.name

	def get_partner_name(self, obj):
		if obj.partner_id:
			try:
				partner_name = User.objects.get(id = obj.partner_id).name
				return partner_name
			except:
				return None
	def get_hub_name(self, obj, hub_id):
		return Hub.objects.get(id=hub_id).name

	def get_current_bin(self, obj):
		if obj.bag_id:
			self.mapping = BinBagMapping.objects.filter(bag_id=obj.bag_id, active=1).first()
			if self.mapping :
				bin_id = self.mapping.bin_id
				self.current_bin = Bin.objects.get(id=bin_id)
				return self.current_bin.get_bin_category_display().upper() + "-" + self.get_hub_name(self, self.current_bin.bin_destination_hub).upper()
		return None

	def get_next_destination(self, obj):
		next_hub_id = get_next_destination_hub(obj, obj.current_hub_id)
		next_hub = Hub.objects.get(id=next_hub_id)
		return next_hub.name

	def get_vehicle_numbers(self, obj):
		if self.mapping and self.current_bin.current_capacity > 0.85*Constants.objects.get(name="vehicle_capacity").value:
			vehicles = Vehicle.objects.filter(current_hub_id=obj.current_hub_id).values_list('vehicle_number', flat=True)
			return vehicles
		return None

	class Meta:
		model = Order
		fields = ('order_number', 'bag_code', 'order_status', 'society_name', 'seller_name', 'partner_id', 'partner_name', 
					'weight', 'current_bin','current_hub_id', 'next_destination', 'vehicle_numbers')

class BagSerializer(serializers.ModelSerializer):
	destination_name = serializers.SerializerMethodField()
	bag_type = serializers.SerializerMethodField()
	origin_name = serializers.SerializerMethodField()
	vehicle_numbers = serializers.SerializerMethodField()
	current_bin = serializers.SerializerMethodField()

	def get_destination_name(self, obj):
		if obj.destination_type == Bag.HUB:
			next_hub = Hub.objects.get(id=obj.destination)
			return next_hub.name
		else:
			society = Society.objects.get(id=obj.destination)
			return society.name + " Society"

	def get_bag_type(self, obj):
		if obj.destination_type == Bag.HUB:
			return "HUB BAG"
		else:
			society = Society.objects.get(id=obj.destination)
			return "SOCIETY BAG"

	def get_origin_name(self, obj):
		origin_hub = Hub.objects.get(id=obj.origin)
		return origin_hub.name

	def get_hub_name(self, obj, hub_id):
		return Hub.objects.get(id=hub_id).name

	def get_current_bin(self, obj):
		mapping = BinBagMapping.objects.filter(bag_id=obj.id, active=1).last()
		if mapping :
			bin_id = mapping.bin_id
			self.current_bin = Bin.objects.get(id=bin_id)
			return self.current_bin.get_bin_category_display().upper() + "-" + self.get_hub_name(self, self.current_bin.bin_destination_hub).upper()

	def get_vehicle_numbers(self, obj):
		if obj.status==Bag.RECEIVED:
			self.get_current_bin(obj)
			vehicles=None
			if self.current_bin.current_capacity > 0.85*Constants.objects.get(name="vehicle_capacity").value:
				vehicles = Vehicle.objects.filter(current_hub_id=self.current_bin.bin_origin_hub).values_list('vehicle_number', flat=True)
			return vehicles
		return None


	class Meta:
		model = Bag
		fields = ('code', 'destination_name', 'bag_type', 'weight', 'origin_name', 'vehicle_numbers', 'current_hub_id', 'current_bin')



