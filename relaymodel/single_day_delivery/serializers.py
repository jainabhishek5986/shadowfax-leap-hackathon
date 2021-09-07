from rest_framework import serializers
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
	# hub_name = serializers.SerializerMethodField()

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
			mapping = BinBagMapping.objects.filter(bag_id=obj.bag_id, active=1).first()
			if mapping :
				bin_id = mapping.bin_id
				current_bin = Bin.objects.get(id=bin_id)
				return current_bin.get_bin_category_display() + "-" +self.get_hub_name(self, current_bin.bin_origin_hub).upper()[:3] + "-" + self.get_hub_name(self, current_bin.bin_destination_hub).upper()[:3]
		return None

	class Meta:
		model = Order
		fields = ('order_number', 'bag_code', 'order_status', 'society_name', 'seller_name', 'partner_id', 'partner_name', 'weight', 'current_bin')

class BagSerializer(serializers.ModelSerializer):

	class Meta:
		model = Bag
		fields = '__all__'