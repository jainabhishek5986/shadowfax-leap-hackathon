from django.urls import path
from django.conf.urls import url
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    url(r'^tracking/$', views.TrackOrder.as_view(), name='track_order'),
    url(r'^order_creation/$', views.OrderCreation.as_view(), name='order_creation'),
    url(r'^seller/receive/$', views.SellerReceive.as_view(), name='seller_receive'),
    url(r'^order/transit/$', views.OrderTransit.as_view(), name='order_transit'),
    # url(r'^hub/scan/$', views.HubScan.as_view(), name='hub_scan'),
    url(r'^hub/receive/$', views.HubReceive.as_view(), name='hub_receive'),
    url(r'^bag/transit/$', views.BagTransit.as_view(), name='bag_transit'),
    url(r'^bag/receive/$', views.BagReceive.as_view(), name='bag_receive'),

]
