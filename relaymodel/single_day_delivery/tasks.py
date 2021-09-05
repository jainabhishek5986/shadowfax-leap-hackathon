from .models import *

def create_entry_in_tracking(order):
	t = Tracking.objects.create(order_id= order.id, status=order.order_status)
	t.save()
