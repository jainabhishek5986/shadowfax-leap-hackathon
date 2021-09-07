from django.db.models import Sum
from .models import *

def create_entry_in_tracking(order):
	t = Tracking.objects.create(order_id= order.id, status=order.order_status)
	t.save()

def get_current_capacity_bin(bin):
	bag_ids = BinBagMapping.objects.filter(bin_id=bin_id).values_list('bag_id', flat=True)
	total_weight = Bin.objects.filter(bag_id__in=bag_ids).aggregate(Sum('weight'))
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
		mapping = BinBagMapping.objects.create(bag_id=bag_id, bin_id=bin_id)
		mapping.save()
		return True
	except:
		return False

def allocate_bin_to_bag(bag, current_hub_id):
	inactivate_current_mapping(bag.id)
	random_order = Order.objects.filter(bag_id = bag.id).last()
	route_list = get_route_for_order(random_order)
	next_hub_location = get_next_destination(route_list, current_hub_id)
	current_bin , created = Bin.objects.get_or_create(bin_origin_hub = current_hub_id, bin_destination_hub=next_hub_location)
	if created:
		current_bin.bin_type = get_bin_type(current_bin, origin, destination)
	# current_bin.current_capacity = get_current_capacity_bin()
	current_bin.save()
	success = create_bin_bag_mapping(bag.id, current_bin.id)
	if success:
		print("LOGGING ==== Bag Bin Mapping Created")
		weight = get_current_capacity_bin(current_bin)
		current_bin.weight = weight
		current_bin.save()
	else:
		print("LOGGING ==== Failed : Bag Bin Mapping Creation")




