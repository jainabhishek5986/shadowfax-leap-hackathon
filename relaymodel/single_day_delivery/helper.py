from .models import *
from .serializers import *
from .tasks import *
import string
import random
from django.db import transaction
import logging

def get_order_details(order_number):
	order = Order.objects.get(order_number= order_number)
	serialized_data = OrderSerializer(order)
	return serialized_data.data

def get_order_tracking_details(order_number):
	order = Order.objects.get(order_number = order_number)
	tracking_details = Tracking.objects.filter(order_id=order.id).order_by('-id')
	serialized_data = TrackingSerializer(tracking_details, many=True)
	return serialized_data

def create_order(order_details, count):
	current_orders = []
	while(count > 0):
		order_number = "ODR-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k = 7))
		society_id = order_details.get("society_id", None)
		seller_id = order_details.get("seller_id", None)
		weight = order_details.get("weight", 0)
		current_hub_id = SellerShops.objects.get(id=seller_id).hub_id
		order = Order.objects.create(order_number=order_number, society_id=society_id, seller_shop_id=seller_id, current_hub_id=current_hub_id, weight = weight)
		current_orders.append(order)
		count-=1 

	serialized_data = OrderSerializer(current_orders, many=True)
	return serialized_data

def generate_random_order(count):
	current_orders = []
	while(count > 0):
		order_number = "ODR-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k = 7))
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
	bag, _ = Bag.objects.get_or_create(origin=order.seller_shop.hub_id, destination= order.society.hub_id, destination_type =1, status=0)
	bag.code = bag_code
	order.bag_id = bag.id
	order.save()
	# bag.weight = update_weight_capacity_bag(bag)
	bag.save()
	print("LOGGING ==== Order - {} added to Bag - {}".format(order_number, bag_code))

def receive_order_at_seller(order_number):
	try:
		order = Order.objects.get(order_number=order_number)
		order.to_seller_received()
		order.save()
		print("LOGGING ==== Order - {} marked Seller Received".format(order_number))
		serialized_data = OrderSerializer(order)
		return True, serialized_data.data
	except Exception as e:
		# logging.error()
		return False, None

def get_delivery_partner(order):
	return random.choice(list(User.objects.filter(user_type = User.DELIVERY_PARTNER)))

def get_shop_partner(order):
	return random.choice(list(User.objects.filter(user_type = User.SHOP_PARTNER, id=order.seller_shop_id)))

def mark_order_transit_from_seller(order_number, partner_required):
	try:
		order = Order.objects.get(order_number=order_number)
		partner_details = {}
		if partner_required:
			partner = get_delivery_partner(order)
			partner_details["partner_id"] = partner.id
			partner_details["partner_type"] = User.DELIVERY_PARTNER
			print("LOGGING ==== Delivery Partner Partner - {} marked ofd".format(partner.name))
		else:
			partner = get_shop_partner(order)
			partner_details["partner_id"] = partner.id
			partner_details["partner_type"] = User.SHOP_PARTNER
		order.to_transit(partner_details)
		order.save()
		print("LOGGING ==== Order - {} marked Transit By Seller".format(order_number))
		serialized_data = OrderSerializer(order)
		return True, serialized_data.data
	except:
		return False, None

def mark_order_received_at_hub(order_number):
	with transaction.atomic():
		try:
			# import pdb ; pdb.set_trace()
			create_bag_for_order(order_number)
			order = Order.objects.get(order_number=order_number)
			order.to_received_at_hub()
			order.save()
			print("LOGGING ==== Order - {} marked Received at Seller Hub".format(order_number))
			serialized_data = OrderSerializer(order)
			return True, serialized_data.data
		except Exception as e:
			print(str(e))
			return False, None


def get_transit_partner(order):
	return random.choice(list(User.objects.filter(user_type = User.TRANSIT_PARTNER).values_list('id', flat=True)))

def mark_orders_transit_with_bag(bag):
	with transaction.atomic():
		try:
			orders = Order.objects.filter(bag_id=bag.id)
			for order in orders:
				partner_details = {}
				partner = get_transit_partner(order)
				partner_details["partner_id"] = partner.id
				partner_details["partner_type"] = User.TRANSIT_PARTNER
				order.to_transit(partner_details)
				print("LOGGING ==== Transit Partner Partner - {} marked ofd".format(partner.name))
				order.save()
			print("LOGGING ==== Marked all order Transit inside Bag - {}".format(bag.code))
			return True
		except:
			return False

def mark_bag_transit(bag_code):
	with transaction.atomic():
		try:
			bag = Bag.objects.get(code=bag_code)
			bag.to_transit()
			bag.save()
			print("LOGGING ==== Bag - {} marked transit".format(bag_code))
			mark_orders_transit_with_bag(bag)
			serialized_data = BagSerializer(bag)
			return True, serialized_data.data
		except Exception as e:
			print(str(e))
			return False, None

def mark_orders_received_with_bag(bag_id, current_hub_id):
	with transaction.atomic():
		try:
			orders = Order.objects.filter(bag_id=bag_id)
			for order in orders:
				order.to_received_at_hub()
				order.current_hub_id = current_hub_id
				order.save()
				print("LOGGING ==== Order - {} marked received at {} hub with bag".format(order.order_number, Hub.objects.get(id=current_hub_id).name))
			return True
		except:
			return False

def create_society_bag_for_order(order):
	bag_code = "BAG-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k = 5))
	bag, created = Bag.objects.get_or_create(code=bag_code, origin=order.current_hub_id, destination=order.society_id, destination_type=0)
	bag.save()
	order.bag_id= bag.id
	order.save()
	print("LOGGING ==== LM Bag - {} created for order {}".format(bag_code, order.order_number))

def sort_bag_at_destination_hub(bag):
	orders = Order.objects.filter(bag_id=bag.id)
	for order in orders:
		create_society_bag_for_order(order)
	bag.to_closed()
	bag.save()
	print("LOGGING ==== Bag - {} marked Closed".format(bag.code))

def mark_bag_received(bag_code, current_hub_id):
	with transaction.atomic():
		try:
			bag = Bag.objects.get(code=bag_code)
			bag.to_received(current_hub_id=current_hub_id)
			bag.save()
			print("LOGGING ==== Bag - {} marked received at {} hub".format(bag_code, Hub.objects.get(id=current_hub_id).name))
			success = mark_orders_received_with_bag(bag.id, current_hub_id)
			if current_hub_id == bag.destination:
				sort_bag_at_destination_hub(bag)
			if not success:
				return False, None
			serialized_data = BagSerializer(bag)
			return True, serialized_data.data
		except Exception as e:
			print(str(e))
			return False, None

def get_shop_partner(order):
	return random.choice(list(User.objects.filter(user_type = User.SHOP_PARTNER, location_id=order.society_id)))

def mark_bag_ofd(bag_code, partner_required):
	with transaction.atomic():
		try:
			bag = Bag.objects.get(code=bag_code)
			orders = Order.objects.filter(bag_id=bag.id)
			partner_required_society_list = Constant.objects.get(name = "partner_required_list").value
			for order in orders:
				partner_details = {}
				if order.society_id in partner_required_society_list:
					partner = get_delivery_partner(order)
					partner_details["partner_id"] = partner.id
					partner_details["partner_type"] = User.DELIVERY_PARTNER
					print("LOGGING ==== Delivery Partner Partner - {} marked ofd".format(partner.name))
				else:
					partner = get_shop_partner(order)
					partner_details["partner_id"] = partner.id
					partner_details["partner_type"] = User.SHOP_PARTNER
					print("LOGGING ==== Shop Partner - {} marked ofd".format(partner.name))
				order.to_ofd(partner_details)
				order.save()
				print("LOGGING ==== Order - {} marked ofd".format(order.order_number))
			print("LOGGING ==== All orders inside Bag - {} marked ofd".format(bag_code))
			serialized_data = BagSerializer(bag)
			return True, serialized_data.data
		except:
			return False, None

def mark_order_delivered(order_number):
	try:
		order = Order.objects.get(order_number=order_number)
		order.to_delivered()
		order.save()
		print("LOGGING ==== Order - {} marked delivered".format(order_number))
		serialized_data = OrderSerializer(order)
		return True, serialized_data.data
	except:
		return False, None
