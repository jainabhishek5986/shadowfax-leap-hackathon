from django.urls import path
from django.conf.urls import url
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    #customer
    url(r'^tracking/$', views.TrackOrder.as_view(), name='track_order'),
    url(r'^order_creation/$', views.OrderCreation.as_view(), name='order_creation'),
    url(r'^order_society/$', views.OrderBySociety.as_view(), name='orders_society'),
    #seller
    url(r'^seller/receive/$', views.SellerReceive.as_view(), name='seller_receive'),
    url(r'^seller/orders/$', views.OrderDetailsSeller.as_view(), name='order_seller'),
    url(r'^order/transit/$', views.OrderTransit.as_view(), name='order_transit'),
    #hub
    url(r'^hub/receive/$', views.HubReceive.as_view(), name='hub_receive'),
    url(r'^bag/transit/$', views.BagTransit.as_view(), name='bag_transit'),
    url(r'^bag/receive/$', views.BagReceive.as_view(), name='bag_receive'),
    url(r'^bag/ofd/$', views.BagOFD.as_view(), name='bag_ofd'),
    #rider
    url(r'^order/delivered/$', views.OrderDelivered.as_view(), name='order_delivered'),

]
