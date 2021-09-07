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

	def get_bag_code(self, obj):
		if obj.bag_id:
			return Bag.objects.get(id=bag_id).code
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
				partner_name = User.objects.get(id = partner_id).name
				return partner_name
			except:
				return None

	class Meta:
		model = Order
		fields = ('order_number', 'bag_code', 'order_status', 'society_name', 'seller_name', 'partner_id', 'partner_name', 'weight')

class BagSerializer(serializers.ModelSerializer):

	class Meta:
		model = Bag
		fields = '__all__'