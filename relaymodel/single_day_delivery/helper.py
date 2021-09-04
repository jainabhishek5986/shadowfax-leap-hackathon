from .models import *
from .serializers import *

def get_order_tracking_details(order_id):
	order = Order.objects.get(id = order_id)
	tracking_details = Tracking.objects.filter(order_id=order_id).order_by('-id')
	serialized_data = TrackingSerializer(tracking_details, many=True)

	return serialized_data