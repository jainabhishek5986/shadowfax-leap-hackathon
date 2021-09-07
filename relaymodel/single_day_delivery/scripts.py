from .models import *
import string
import random

def create_multiple_users(user_type, count):
	names = ["Abhishek", "Kunal", "Sushant", "Vaibhav", "Motwani", "Ravi", "Jain", "Tyagi", "Sameer", "Abdul", "Aman", "Zeeshan", "Shivam", "Arpit", "Verma"]
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