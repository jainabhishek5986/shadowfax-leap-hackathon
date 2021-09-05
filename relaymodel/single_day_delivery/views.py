from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed, ValidationError
import single_day_delivery.helper as helper 
import string
import random


def index(request):
    return HttpResponse("Hello, world. You're at the single_day_delivery index.")

# Create your views here.
class TrackOrder(APIView):
	def get(self, request):
		order_number = request.GET.get('order_number', None)
		if not order_number:
			return Response({"message": "Invalid order_id"}, status=status.HTTP_400_BAD_REQUEST)
		tracking_data = helper.get_order_tracking_details(order_number)
		return Response({"message": "Success", "data": tracking_data.data}, status=status.HTTP_200_OK)

class OrderCreation(APIView):
	def post(self, request):
		order_details = request.data.get('order_details', None)
		count = request.data.get('count', 1)
		if not order_details:
			orders_data = helper.generate_random_order(count)
		return Response({"message": "Success", "data": orders_data.data}, status=status.HTTP_200_OK)

class SellerReceive(APIView):
	def post(self, request):
		order_number = request.data.get('order_number', None)

		if not order_number:
			return Response({"message": "Invalid order_id"}, status=status.HTTP_400_BAD_REQUEST)

		success = helper.receive_order_at_seller(order_number)
		if success:
			return Response({"message": "Success"}, status=status.HTTP_200_OK)
		return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

class OrderTransit(APIView):
	def post(self, request):
		order_number = request.data.get('order_number', None)
		if not order_number:
			return Response({"message": "Invalid order_id"}, status=status.HTTP_400_BAD_REQUEST)

		success = helper.mark_order_transit_from_seller(order_number)
		if success:
			return Response({"message": "Success"}, status=status.HTTP_200_OK)
		return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

class HubReceive(APIView):
	def post(self, request):
		order_number = request.data.get('order_number', None)
		if not order_number:
			return Response({"message": "Invalid order_id"}, status=status.HTTP_400_BAD_REQUEST)

		success = helper.mark_order_received_at_hub(order_number)
		if success:
			return Response({"message": "Success"}, status=status.HTTP_200_OK)
		return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

class BagTransit(APIView):
	def post(self, request):
		bag_code = request.data.get('bag_code', None)
		if not bag_code:
			return Response({"message": "Invalid order_id"}, status=status.HTTP_400_BAD_REQUEST)

		success = helper.mark_bag_transit(bag_code)
		if success:
			return Response({"message": "Success"}, status=status.HTTP_200_OK)
		return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

class BagReceive(APIView):
	def post(self, request):
		bag_code = request.data.get('bag_code', None)
		hub_id = request.data.get('hub_id', None)
		if not bag_code:
			return Response({"message": "Invalid order_id"}, status=status.HTTP_400_BAD_REQUEST)

		success = helper.mark_bag_received(bag_code, hub_id)
		if success:
			return Response({"message": "Success"}, status=status.HTTP_200_OK)
		return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


