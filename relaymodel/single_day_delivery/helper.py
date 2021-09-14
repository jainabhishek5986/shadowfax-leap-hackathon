from pdb import set_trace
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

def get_order_details_from_society(society_id):
	orders = Order.objects.filter(society_id = society_id)
	serialized_data = OrderSerializer(orders, many = True)
	return serialized_data.data

def get_order_from_seller(seller_shop_id):
	orders = Order.objects.filter(seller_shop_id = seller_shop_id)
	serialized_data = OrderSerializer(orders, many = True)
	return serialized_data.data

def get_all_sellers():
	sellers_shops = SellerShops.objects.filter().all()
	serialized_data = SellerShopSerializer(sellers_shops, many = True)
	return serialized_data.data

def get_all_hubs():
	hubs = Hub.objects.filter().all()
	serialized_data = HubSerializer(hubs, many = True)
	return serialized_data.data

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
	bag, created = Bag.objects.get_or_create(origin=order.seller_shop.hub_id, destination= order.society.hub_id, destination_type =1, status=0)
	if created:
		bag_code = "BAG-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k = 5))
		bag.code = bag_code
		bag.weight = 0
	order.bag_id = bag.id
	order.save()
	# bag.weight = update_weight_capacity_bag(bag)
	bag.current_hub_id = order.seller_shop.hub_id
	bag.save()
	print("LOGGING ==== Order - {} added to Bag - {}".format(order_number, bag.code))
	return bag.id

def receive_order_at_seller(order_number):
	try:
		order = Order.objects.get(order_number=order_number)
		order.to_seller_received()
		order.save(location_name = order.seller_shop.name)
		print("LOGGING ==== Order - {} marked Seller Received".format(order_number))
		serialized_data = OrderSerializer(order)
		return True, serialized_data.data
	except Exception as e:
		return False, None

def get_delivery_partner(order):
	return random.choice(list(User.objects.filter(user_type = User.DELIVERY_PARTNER)))

def get_shop_partner(order):
	return random.choice(list(User.objects.filter(user_type = User.SHOP_PARTNER, location_id=order.seller_shop_id)))

def mark_order_transit_from_seller(order_number, partner_required):
	try:
		order = Order.objects.get(order_number=order_number)
		partner_details = {}
		if partner_required:
			partner = get_delivery_partner(order)
			partner_details["partner_id"] = partner.id
			partner_details["partner_type"] = User.DELIVERY_PARTNER
			print("LOGGING ==== Delivery Partner - {} marked ofd".format(partner.name))
		else:
			partner = get_shop_partner(order)
			partner_details["partner_id"] = partner.id
			partner_details["partner_type"] = User.SHOP_PARTNER
		order.to_transit(partner_details)
		order.save(location_name = order.seller_shop.name)
		print("LOGGING ==== Order - {} marked Transit By Seller".format(order_number))
		serialized_data = OrderSerializer(order)
		return True, serialized_data.data
	except Exception as e:
		return False, str(e)

def mark_order_received_at_hub(order_number):
	with transaction.atomic():
		try:
			bag_id = create_bag_for_order(order_number)
			order = Order.objects.get(order_number=order_number)
			# order.bag_id = bag_id
			# order.save(location_name = order.seller_shop.hub.name)
			order.to_received_at_hub()
			order.save(location_name = order.seller_shop.hub.name)
			print("LOGGING ==== Order - {} marked Received at Seller Hub".format(order_number))
			serialized_data = OrderSerializer(order)
			return True, serialized_data.data
		except Exception as e:
			return False, print(str(e))


def get_transit_partner(vehicle_number):
	try:
		vehicle = Vehicle.objects.get(vehicle_number=vehicle_number)
		return vehicle.partner
	except:
		print("LOGGING ==== Transit Partner Does Not Exist")
		return None

def mark_orders_transit_with_bag(bag, partner_details):
	try:
		orders = Order.objects.filter(bag_id=bag.id)
		for order in orders:
			order.to_transit(partner_details)
			# print("LOGGING ==== Transit Partner - {} marked ofd".format(partner_details.id))
			order.save(location_name = order.current_hub.name)
		print("LOGGING ==== Marked all order Transit inside Bag - {}".format(bag.code))
	except:
		pass

def create_vehicle_details(bag, vehicle_number):
	vehicle_mapping = VehicleBagMapping.objects.create(bag_code=bag.code, vehicle_number=vehicle_number)
	vehicle_mapping.save()
	mapping = BinBagMapping.objects.filter(bag_id=bag.id, active=1).first()
	current_bin = Bin.objects.get(id=mapping.bin_id)
	transit_details = VehicleTransitDetails.objects.create(origin=current_bin.bin_origin_hub, destination=current_bin.bin_destination_hub, 
		transit_time=timezone.now(), vehicle_number=vehicle_number)
	transit_details.save()

def mark_bag_transit(bag_code, vehicle_number):
	with transaction.atomic():
		try:
			bag = Bag.objects.get(code=bag_code)
			partner = get_transit_partner(vehicle_number)
			partner_details = {}
			partner_details["partner_id"] = partner.id
			partner_details["partner_type"] = User.TRANSIT_PARTNER
			bag.to_transit()
			bag.save()
			print("LOGGING ==== Bag - {} marked transit".format(bag_code))
			mark_orders_transit_with_bag(bag, partner_details)
			create_vehicle_details(bag, vehicle_number)
			serialized_data = BagSerializer(bag)
			return True, serialized_data.data
		except Exception as e:
			print(str(e))
			return False, None

def mark_orders_received_with_bag(bag_id, current_hub_id):
	try:
		orders = Order.objects.filter(bag_id=bag_id)
		for order in orders:
			order.to_received_at_hub(bag_receive=True)
			order.current_hub_id = current_hub_id
			order.save(location_name = order.current_hub.name)
			print("LOGGING ==== Order - {} marked received at {} hub with bag".format(order.order_number, Hub.objects.get(id=current_hub_id).name))
	except:
		pass

def create_society_bag_for_order(order):
	bag_code = "BAG-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k = 5))
	bag, created = Bag.objects.get_or_create(origin=order.current_hub_id, destination=order.society_id, destination_type=0)
	if created:
		bag.code = bag_code
	bag.save()
	order.bag_id= bag.id
	order.save(location_name = order.current_hub.name)
	print("LOGGING ==== LM Bag - {} created for order {}".format(bag_code, order.order_number))

def sort_bag_at_destination_hub(bag):
	orders = Order.objects.filter(bag_id=bag.id)
	for order in orders:
		create_society_bag_for_order(order)
	bag.to_closed()
	bag.save()
	print("LOGGING ==== Bag - {} marked Closed".format(bag.code))

def mark_vehicle_bag_received(bag_code, vehicle_number, current_hub_id):
	if vehicle_number:
		vehicle_mapping = VehicleBagMapping.objects.filter(bag_code=bag_code, vehicle_number=vehicle_number, status=True).update(status=False)
		print("LOGGING ==== Vehicle Mapping Inactivated")

		vehicle = Vehicle.objects.get(vehicle_number=vehicle_number)
		vehicle.current_hub_id = current_hub_id
		vehicle.save()
		print("LOGGING ==== Vehicle Current Hub Updated")

		transit_details = VehicleTransitDetails.objects.filter(vehicle_number=vehicle_number, destination=current_hub_id).last()
		transit_details.received_time = timezone.now()
		transit_details.save()
		print("LOGGING ==== VehicleTransitDetails received time updated")

def mark_bag_received(bag_code, current_hub_id, vehicle_number):
	with transaction.atomic():
		try:
			bag = Bag.objects.get(code=bag_code)
			bag.to_received(current_hub_id=current_hub_id)
			bag.save()
			print("LOGGING ==== Bag - {} marked received at {}".format(bag_code, Hub.objects.get(id=current_hub_id).name))
			mark_orders_received_with_bag(bag.id, current_hub_id)
			mark_vehicle_bag_received(bag_code, vehicle_number, current_hub_id)
			if current_hub_id == bag.destination:
				bag.bag_type=Bag.SOCIETY
				bag.to_closed()
				bag.save()
			# 	sort_bag_at_destination_hub(bag)
			serialized_data = BagSerializer(bag)
			return True, serialized_data.data
		except Exception as e:
			print(str(e))
			return False, None

def mark_bag_ofd(bag_code, partner_required):
	with transaction.atomic():
		try:
			bag = Bag.objects.get(code=bag_code)
			orders = Order.objects.filter(bag_id=bag.id, order_status=Order.RECEIVED_AT_HUB)
			partner_required_society_list = Constants.objects.get(name = "partner_required_list").value
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
				order.save(location_name=order.society.hub.name)
				print("LOGGING ==== Order - {} marked ofd".format(order.order_number))
			print("LOGGING ==== All orders inside Bag - {} marked ofd".format(bag_code))
			serialized_data = BagSerializer(bag)
			return True, serialized_data.data
		except Exception as e:
			print(str(e))
			return False, None

def mark_order_delivered(order_number):
	try:
		order = Order.objects.get(order_number=order_number)
		order.to_delivered()
		order.save(location_name = "Partner Delivered Order")
		print("LOGGING ==== Order - {} marked delivered".format(order_number))
		serialized_data = OrderSerializer(order)
		return True, serialized_data.data
	except Exception as e:
		print(str(e))
		return False, None

class HubDashboardHelper(object):
	def __init__(self, hub_id):
		self.hub_id = hub_id
	
	def get_order_to_be_received(self):
		orders = Order.objects.filter(seller_shop__hub_id=self.hub_id, bag_id=None).order_by('-id')
		serialized_data = OrderSerializer(orders, many=True)
		return serialized_data.data

	def get_bags_to_be_received(self):
		bins_reaching_hub = list(Bin.objects.filter(bin_destination_hub=self.hub_id).values_list('id', flat=True))
		bag_ids = BinBagMapping.objects.filter(bin_id__in=bins_reaching_hub).values_list('bag_id', flat=True)
		# vehicle_numbers = list(VehicleTransitDetails.objects.filter(destination=self.hub_id, received_time=None).values_list('vehicle_number', flat=True).distinct())
		# bag_codes = list(VehicleBagMapping.objects.filter(vehicle_number__in=vehicle_numbers, status=True).values_list('bag_code', flat=True).distinct())
		bags = Bag.objects.filter(id__in = bag_ids, status=Bag.IN_TRANSIT).order_by('-id')
		serialized_data = BagSerializer(bags, many=True)
		return serialized_data.data

	def get_bags_to_transit(self):
		bags = Bag.objects.filter(current_hub_id = self.hub_id, status__in=[Bag.NEW, Bag.RECEIVED]).order_by('-id')
		serialized_data = BagSerializer(bags, many=True)
		return serialized_data.data

	def get_bags_to_ofd(self):
		bags = Bag.objects.filter(destination = self.hub_id, status__in=[Bag.NEW, Bag.RECEIVED]).order_by('-id')
		serialized_data = BagSerializer(bags, many=True)
		return serialized_data.data


