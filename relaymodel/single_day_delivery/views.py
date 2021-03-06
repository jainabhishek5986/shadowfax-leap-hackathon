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

class OrderBySociety(APIView):
	def get(self, request):
		society_id = request.GET.get('society_id', None)
		if not society_id:
			return Response({"message": "Invalid society_id"}, status=status.HTTP_400_BAD_REQUEST)
		society_orders_from = helper.get_order_details_from_society(society_id)
		return Response({"message": "Success", "data": society_orders_from}, status=status.HTTP_200_OK)

class OrderDetailsSeller(APIView):
	def get(self, request):
		seller_shop_id = request.GET.get('seller_shop_id', None)
		if not seller_shop_id:
			return Response({"message": "Invalid seller"}, status=status.HTTP_400_BAD_REQUEST)
		seller_orders = helper.get_order_from_seller(seller_shop_id)
		return Response({"message": "Success", "data" : seller_orders}, status=status.HTTP_200_OK)

class SellerAll(APIView):
	def get(self, request):
		sellers_all = helper.get_all_sellers()
		return Response({"message": "Success", "data" : sellers_all}, status=status.HTTP_200_OK)

class HubAll(APIView):
	def get(self, request):
		hubs_all = helper.get_all_hubs()
		return Response({"message": "Success", "data" : hubs_all}, status=status.HTTP_200_OK)
		
class OrderCreation(APIView):
	def post(self, request):
		order_details = request.data.get('order_details', None)
		count = request.data.get('count', 1)
		if not order_details:
			orders_data = helper.generate_random_order(count)
		else:
			orders_data = helper.create_order(order_details, count)
		return Response({"message": "Success", "data": orders_data.data}, status=status.HTTP_200_OK)

class SellerReceive(APIView):
	def get(self, request):
		order_number = request.GET.get('order_number', None)

		if not order_number:
			return Response({"message": "Invalid order_id"}, status=status.HTTP_400_BAD_REQUEST)

		data = helper.get_order_details(order_number)
		return Response({"message": "Order Received", "data": data}, status=status.HTTP_200_OK)
	def post(self, request):
		order_number = request.data.get('order_number', None)

		if not order_number:
			return Response({"message": "Invalid order_id"}, status=status.HTTP_400_BAD_REQUEST)

		success, data = helper.receive_order_at_seller(order_number)
		if success:
			return Response({"message": "Order Accepted By Seller", "data": data}, status=status.HTTP_200_OK)
		return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

class OrderTransit(APIView):
	def post(self, request):
		order_number = request.data.get('order_number', None)
		partner_required = request.data.get('partner_required', False)
		if not order_number:
			return Response({"message": "Invalid order_id"}, status=status.HTTP_400_BAD_REQUEST)

		success, data = helper.mark_order_transit_from_seller(order_number, partner_required)
		if success:
			return Response({"message": "Success", "data": data}, status=status.HTTP_200_OK)
		return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

class HubReceive(APIView):
	def post(self, request):
		order_number = request.data.get('order_number', None)
		hub_id = request.data.get('hub_id', None)
		if not order_number:
			return Response({"message": "Invalid order_id"}, status=status.HTTP_400_BAD_REQUEST)

		success, data = helper.mark_order_received_at_hub(order_number, hub_id)
		if success:
			return Response({"message": "Success", "data": data}, status=status.HTTP_200_OK)
		return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

class BagTransit(APIView):
	def post(self, request):
		bag_code = request.data.get('bag_code', None)
		vehicle_number = request.data.get('vehicle_number', None)
		if not bag_code:
			return Response({"message": "Invalid order_id"}, status=status.HTTP_400_BAD_REQUEST)

		success, data = helper.mark_bag_transit(bag_code, vehicle_number)
		if success:
			return Response({"message": "Success", "data": data}, status=status.HTTP_200_OK)
		return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

class BagReceive(APIView):
	def post(self, request):
		bag_code = request.data.get('bag_code', None)
		hub_id = request.data.get('hub_id', None)
		vehicle_number = request.data.get('vehicle_number', None)
		if not bag_code:
			return Response({"message": "Invalid order_id"}, status=status.HTTP_400_BAD_REQUEST)
		hub_id = int(hub_id)
		success, data = helper.mark_bag_received(bag_code, hub_id, vehicle_number)
		if success:
			return Response({"message": "Success", "data": data}, status=status.HTTP_200_OK)
		return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

class BagOFD(APIView):
	def post(self, request):
		bag_code = request.data.get('bag_code', None)
		partner_required = request.data.get('partner_required', False)
		if not bag_code:
			return Response({"message": "Invalid order_id"}, status=status.HTTP_400_BAD_REQUEST)

		success, data = helper.mark_bag_ofd(bag_code, partner_required)
		if success:
			return Response({"message": "Success", "data": data}, status=status.HTTP_200_OK)
		return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

class OrderDelivered(APIView):
	def post(self, request):
		order_number = request.data.get('order_number', None)

		if not order_number:
			return Response({"message": "Invalid order_id"}, status=status.HTTP_400_BAD_REQUEST)

		success, data = helper.mark_order_delivered(order_number)
		if success:
			return Response({"message": "Success", "data": data}, status=status.HTTP_200_OK)
		return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

class HubDashboard(APIView):
	def get(self, request):
		hub_id = request.GET.get('hub_id', None)

		if not hub_id:
			return Response({"message": "Invalid hub_id"}, status=status.HTTP_400_BAD_REQUEST)
		dashboard_helper = helper.HubDashboardHelper(hub_id)
		data_dict = {}

		data_dict["orders_to_be_received"] = dashboard_helper.get_order_to_be_received()
		data_dict["bags_to_be_received"] = dashboard_helper.get_bags_to_be_received()
		data_dict["bags_to_transit"] = dashboard_helper.get_bags_to_transit()
		data_dict["bags_to_ofd"] = dashboard_helper.get_bags_to_ofd()

		return Response({"message": "Success", "data": data_dict}, status=status.HTTP_200_OK)


