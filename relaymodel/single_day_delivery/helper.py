from .models import *
from .serializers import *
import string
import random
from django.db import transaction

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
	bag, _ = Bag.objects.get_or_create(code = bag_code, origin=order.seller_shop.hub_id, destination= order.society.hub_id, status=0)
	bag.save()
	order.bag_id = bag.id
	order.save()

def receive_order_at_seller(order_number):
	try:
		order = Order.objects.get(order_number=order_number)
		order.to_seller_received()
		order.save()
		return True
	except:
		return False

def mark_order_transit_from_seller(order_number):
	try:
		order = Order.objects.get(order_number=order_number)
		order.to_transit()
		order.save()
		return True
	except:
		return False

def mark_order_received_at_hub(order_number):
	with transaction.atomic():
		try:
			create_bag_for_order(order_number)
			order = Order.objects.get(order_number=order_number)
			order.to_received_at_hub()
			order.save()
			return True
		except:
			return False

def mark_orders_transit_with_bag(bag):
	with transaction.atomic():
		try:
			orders = Order.objects.filter(bag_id=bag.id)
			for order in orders:
				order.to_transit()
				order.save()
			return True
		except:
			return False

def mark_bag_transit(bag_code):
	with transaction.atomic():
		try:
			bag = Bag.objects.get(code=bag_code)
			bag.to_transit()
			bag.save()

			mark_orders_transit_with_bag(bag)
			return True
		except:
			return False

def mark_orders_received_with_bag(bag_id, current_hub_id):
	with transaction.atomic():
		try:
			orders = Order.objects.filter(bag_id=bag_id)
			# import pdb; pdb.set_trace()
			for order in orders:
				order.to_received_at_hub()
				order.current_hub_id = current_hub_id
				order.save()
			return True
		except:
			return False


def mark_bag_received(bag_code, current_hub_id):
	with transaction.atomic():
		try:
			bag = Bag.objects.get(code=bag_code)
			bag.to_received()
			bag.save()
			success = mark_orders_received_with_bag(bag.id, current_hub_id)
			if not success:
				return False
			return True
		except:
			return False




