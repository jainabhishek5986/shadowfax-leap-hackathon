from rest_framework import serializers
from .models import *

class TrackingSerializer(serializers.ModelSerializer):

	class Meta:
		model = Tracking
		fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):

	class Meta:
		model = Order
		fields = '__all__'