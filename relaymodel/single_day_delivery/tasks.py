from django.db.models import Sum
from .models import *
import random
def create_entry_in_tracking(order):
	t = Tracking.objects.create(order_id= order.id, status=order.order_status)
	t.save()

def get_route_for_order(order):
	route_list = []
	route_list.append(order.seller_shop.hub_id)
	if order.seller_shop.hub.major_hub :
		route_list.append(order.seller_shop.hub.major_hub)
	if order.society.hub.major_hub :
		route_list.append(order.society.hub.major_hub)
	route_list.append(order.society.hub_id)


def get_next_destination_hub(order, current_hub) :
	if current_hub == order.seller_shop.hub_id :
		if order.seller_shop.hub.major_hub :
			return order.seller_shop.hub.major_hub_id
		else:
			if order.society.hub.major_hub:
				return order.society.hub.major_hub_id
			else:
				return order.society.hub_id
	
	elif current_hub == order.seller_shop.hub.major_hub_id :
		if order.society.hub.major_hub:
			return order.society.hub.major_hub_id
		else:
			return order.society.hub_id

	elif current_hub == order.society.hub.major_hub_id:
		return order.society.hub_id
	else : 
		return None 
			
def get_current_capacity_bin(bin):
	bag_ids = list(BinBagMapping.objects.filter(bin_id=bin.id).values_list('bag_id', flat=True))
	total_weight = Bag.objects.filter(id__in=bag_ids).aggregate(Sum('weight'))
	return total_weight["weight__sum"]

def update_weight_capacity_bag(bag):
	weight = Order.objects.filter(bag_id = bag.id).aggregate(Sum('weight'))
	return weight["weight__sum"]

def get_bin_type(current_bin, origin, destination):
	origin_hub = Hub.objects.get(id=origin)
	destination_hub = Hub.objects.get(id=destination)

	if origin_hub.hub_type == Hub.MINOR_HUB and destination_hub.hub_type == Hub.MAJOR_HUB:
		return Bin.MINOR_TO_MAJOR
	elif origin_hub.hub_type == Hub.MAJOR_HUB and destination_hub.hub_type == Hub.MAJOR_HUB:
		return Bin.MAJOR_TO_MAJOR
	elif origin_hub.hub_type == Hub.MAJOR_HUB and destination_hub.hub_type == Hub.MINOR_HUB:
		return Bin.MAJOR_TO_MINOR

def inactivate_current_mapping(bag_id):
	mapping = BinBagMapping.objects.filter(bag_id=bag_id, active=1)
	mapping.update(active = 0)

	print("LOGGING ==== Inactivated exisiting Mapping Bag Bin")

def create_bin_bag_mapping(bag_id, bin_id):
	try:
		mapping , created = BinBagMapping.objects.get_or_create(bag_id=bag_id, bin_id=bin_id)
		if not created:
			mapping.active = 1 
			mapping.save()
		return True
	except:
		return False

def allocate_bin_to_bag(bag_id, current_hub_id):
	bag = Bag.objects.get(id=bag_id)
	if current_hub_id != bag.destination:
		random_order = Order.objects.filter(bag_id = bag_id).last()
		next_hub_location = get_next_destination_hub(random_order, current_hub_id)
		current_bin , created = Bin.objects.get_or_create(bin_origin_hub = current_hub_id, bin_destination_hub=next_hub_location)
		if created:
			current_bin.bin_type = get_bin_type(current_bin, current_hub_id, next_hub_location)
		success = create_bin_bag_mapping(bag_id, current_bin.id)
		if success:
			print("LOGGING ==== Bag Bin Mapping Created")
			weight = get_current_capacity_bin(current_bin)
			current_bin.current_capacity = weight
			current_bin.save()
		else:
			print("LOGGING ==== Failed : Bag Bin Mapping Creation")


def update_weight_after_bag_transit(bag):
	mapping = BinBagMapping.objects.filter(bag_id=bag.id, active=1)
	if mapping:
		bin_id = mapping[0].bin_id
		current_bin = Bin.objects.get(id=bin_id)
		current_bin.current_capacity -= bag.weight
		current_bin.save()


