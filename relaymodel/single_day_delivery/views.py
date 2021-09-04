from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed, ValidationError
import single_day_delivery.helper as helper 


def index(request):
    return HttpResponse("Hello, world. You're at the single_day_delivery index.")

# Create your views here.
class TrackOrder(APIView):
	def get(self, request):
		order_id = request.GET.get('order_id', None)
		if not order_id:
			return Response({"message": "Invalid order_id"}, status=status.HTTP_400_BAD_REQUEST)
		tracking_data = helper.get_order_tracking_details(order_id)
		return Response({"message": "Success", "data": tracking_data.data}, status=status.HTTP_200_OK)
