from .models import *
import string
import random

def create_multiple_users(user_type, count):
	names = ["sawan", "shivam", "nobita", "gian", "ash", "john", "johnny", "brad", "shardul", "jimmy", "james", "joe", "bob", "brian", "donald", "biden", "barak", "obama", "elon", "n modi"]
	number = User.objects.filter().last().phone_number
	objects = None
	if user_type == 0:
		objects = Hub.objects.filter().all()
	elif user_type == 4:
		objects = SellerShops.objects.filter().all()
	elif user_type == 5:
		objects = Society.objects.filter().all()
	elif user_type == 3:
		objects = Transporter.objects.filter().all()
	while(count>0):
		if objects:
			for obj in objects:
				user = User.objects.create(user_type=user_type, name = random.choice(names), phone_number=number+1, location_id=obj.id, address=obj.name)
				number+=1
				user.save()
		else:
			user = User.objects.create(user_type=user_type, name = random.choice(names), phone_number=number+1, location_id=None, address=None)
		count -=1

def create_multiple_sellers():
	names = ["Abhishek", "Kunal", "Sushant", "Vaibhav", "Motwani", "Ravi", "Jain", "Tyagi", "Sameer", "Abdul", "Aman", "Zeeshan", "Shivam", "Arpit", "Verma"]
	hubs = Hub.objects.all().exclude(id__in=[7,8,80])
	types = ["Groceries", "Stationary", "Automobiles", "Textiles", "Electronics"]
	for hub in hubs:
		for t in types:
			s = SellerShops.objects.create(name = random.choice(names) + " " + t, address = hub.name + ", Bangalore, Karnataka", latitude = hub.latitude, longitude = hub.longitude, pincode = hub.pincode, contact = 9999999999, hub_id =hub.id)
			s.save()

sellers = SellerShops.objects.filter(hub_id__in=[73,74,75,76,77,78,79])

for seller in sellers:
	seller.address = seller.hub.name[:-4] + ", Bangalore, Karnataka"
	seller.save()

def create_multiple_shop_partners():
	sellers = SellerShops.objects.filter().all()
	for seller in sellers:
		names = ["sawan", "shivam", "nobita", "gian", "ash", "john", "johnny", "brad", "shardul", "jimmy", "james", "joe", "bob", "brian", "donald", "biden", "barak", "obama", "elon", "n modi"]
		user = User.objects.create(user_type=4, name = random.choice(names), location_id=seller.id, address=seller.address, latitude=seller.latitude, longitude= seller.longitude)
		user.save()
		seller.partner_id = user.id
		seller.save()

def create_multiple_travel_partners(count):
	partner_ids = []
	while(count>0):
		names = ["sawan", "shivam", "nobita", "gian", "ash", "john", "johnny", "brad", "shardul", "jimmy", "james", "joe", "bob", "brian", "donald", "biden", "barak", "obama", "elon", "n modi"]
		user = User.objects.create(user_type=2, name = random.choice(names), location_id=None, address=None)
		user.save()
		partner_ids.append(user.id)
		count-=1
	return partner_ids

def assign_major_hubs():
	counts = 8
	hubs = Hub.objects.all()
	major_hub_id = 8
	for hub in hubs:
		if hub.id %8 == 0:
			hub.hub_type = 1
			major_hub_id = hub.id
		else:
			hub.hub_type = 1
			hub.major_hub_id = major_hub_id
		hub.address = hub.name[:-4] + ", Bangalore, Karnataka"
		hub.save()

def create_multiple_vehicles():
	hubs = Hub.objects.filter().exclude(id=80)
	for hub in hubs:
		partner_ids = create_multiple_travel_partners(1)
		for partner_id in partner_ids:
			vehicle_number = "KA" +''.join(random.choices(string.digits, k = 2))+ ''.join(random.choices(string.ascii_uppercase, k = 2)) + ''.join(random.choices(string.digits, k = 4))
			vehicle = Vehicle.objects.create(vehicle_number=vehicle_number, capacity=50, cost=2, filling_time=120, partner_id=partner_id, current_hub_id=hub.id)
			vehicle.save()
			partner = User.objects.get(id=partner_id)
			partner.location_id = vehicle.id
			partner.save()


