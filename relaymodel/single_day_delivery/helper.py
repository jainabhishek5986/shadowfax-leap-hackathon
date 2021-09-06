from .models import *
from .serializers import *
import string
import random
from django.db import transaction
import logging

def get_order_tracking_details(order_number):
	order = Order.objects.get(order_number = order_number)
	tracking_details = Tracking.objects.filter(order_id=order.id).order_by('-id')
	serialized_data = TrackingSerializer(tracking_details, many=True)
	return serialized_data

def generate_random_order(count):
	N = 7
	current_orders = []
	while(count > 0):
		order_number = "ODR-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k = N))
		# if not hub_id:
		society_id = random.choice(list(Society.objects.filter().values_list('id', flat=True)))
		seller_id = random.choice(list(SellerShops.objects.filter().values_list('id', flat=True)))
		current_hub_id = SellerShops.objects.get(id=seller_id).hub_id
		order = Order.objects.create(order_number=order_number, society_id=society_id, seller_shop_id=seller_id, current_hub_id=current_hub_id)
		current_orders.append(order)
		count-=1 

	serialized_data = OrderSerializer(current_orders, many=True)
	return serialized_data

def create_bag_for_order(order_number):
	order = Order.objects.get(order_number= order_number)
	bag_code = "BAG-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k = 5))
	bag, _ = Bag.objects.get_or_create(code = bag_code, origin=order.seller_shop.hub_id, destination= order.society.hub_id, destination_type =1, status=0)
	bag.save()
	order.bag_id = bag.id
	order.save()
	logging.info("Order - {} added to Bag - {}".format(order_number, bag_code))

def receive_order_at_seller(order_number):
	try:
		order = Order.objects.get(order_number=order_number)
		order.to_seller_received()
		order.save()
		logging.info("Order - {} marked Seller Received".format(order_number))
		serialized_data = OrderSerializer(order)
		return True, serialized_data.data
	except Exception as e:
		# logging.error()
		return False, None

def mark_order_transit_from_seller(order_number,delivery_partner):
	try:
		order = Order.objects.get(order_number=order_number)
		if(not delivery_partner) :
			order.rider_assigned_to_order()
		order.to_transit()
		order.save()
		logging.info("Order - {} marked Transit By Seller".format(order_number))
		serialized_data = OrderSerializer(order)
		return True, serialized_data.data
	except:
		return False, None

def mark_order_received_at_hub(order_number):
	with transaction.atomic():
		try:
			create_bag_for_order(order_number)
			order = Order.objects.get(order_number=order_number)
			order.to_received_at_hub()
			order.save()
			logging.info("Order - {} marked Received at Seller Hub".format(order_number))
			serialized_data = OrderSerializer(order)
			return True, serialized_data.data
		except:
			return False, None

def mark_orders_transit_with_bag(bag):
	with transaction.atomic():
		try:
			orders = Order.objects.filter(bag_id=bag.id)
			for order in orders:
				order.to_transit()
				order.save()
			logging.info("Marked all order Transit inside Bag - {}".format(bag.code))
			return True
		except:
			return False

def mark_bag_transit(bag_code):
	with transaction.atomic():
		try:
			bag = Bag.objects.get(code=bag_code)
			bag.to_transit()
			bag.save()
			logging.info("Bag - {} marked transit".format(bag_code))
			mark_orders_transit_with_bag(bag)
			serialized_data = BagSerializer(bag)
			return True, serialized_data.data
		except:
			return False, None

def mark_orders_received_with_bag(bag_id, current_hub_id):
	with transaction.atomic():
		try:
			orders = Order.objects.filter(bag_id=bag_id)
			for order in orders:
				order.to_received_at_hub()
				order.current_hub_id = current_hub_id
				order.save()
				logging.info("Order - {} marked received at {} hub with bag".format(order.order_number, Hub.objects.get(id=current_hub_id).name))
			return True
		except:
			return False

def create_society_bag_for_order(order):
	bag_code = "BAG-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k = 5))
	bag, created = Bag.objects.get_or_create(code=bag_code, origin=order.current_hub_id, destination=order.society_id, destination_type=0)
	bag.save()
	order.bag_id= bag.id
	order.save()
	logging.info("LM Bag - {} created for order {}".format(bag_code, order.order_number))

def sort_bag_at_destination_hub(bag):
	# bag = Bag.objects.get(code=bag_code)
	orders = Order.objects.filter(bag_id=bag.id)
	for order in orders:
		create_society_bag_for_order(order)
	bag.to_closed()
	bag.save()
	logging.info("Bag - {} marked Closed".format(bag_code))

def mark_bag_received(bag_code, current_hub_id):
	with transaction.atomic():
		try:
			bag = Bag.objects.get(code=bag_code)
			bag.to_received()
			bag.save()
			logging.info("Bag - {} marked received at {} hub".format(bag_code, Hub.objects.get(id=current_hub_id).name))
			success = mark_orders_received_with_bag(bag.id, current_hub_id)
			if current_hub_id == bag.destination:
				sort_bag_at_destination_hub(bag)
			if not success:
				return False, None
			serialized_data = BagSerializer(bag)
			return True, serialized_data.data
		except:
			return False, None

def mark_bag_ofd(bag_code):
	with transaction.atomic():
		try:
			bag = Bag.objects.get(code=bag_code)
			orders = Order.objects.filter(bag_id=bag.id)
			for order in orders:
				order.to_ofd()
				order.save()
				logging.info("Order - {} marked ofd".format(order.order_number))
			logging.info("All orders inside Bag - {} marked ofd".format(bag_code))
			serialized_data = BagSerializer(bag)
			return True, serialized_data.data
		except:
			return False, None

def mark_order_delivered(order_number):
	try:
		order = Order.objects.get(order_number=order_number)
		order.to_delivered()
		order.save()
		logging.info("Order - {} marked delivered".format(order_number))
		serialized_data = OrderSerializer(order)
		return True, serialized_data.data
	except:
		return False, None
