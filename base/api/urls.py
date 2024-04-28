from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_routes),
    path('rooms/', views.get_rooms),
    path('rooms/<str:pk>', views.get_room),
    path('rooms/<str:pk>/delete', views.delete_room),
    path('rooms/create', views.create_room),
    path('messages/<str:pk>', views.get_messages),
    path('messages/<str:pk>/delete', views.delete_message),
    path('messages/send/<str:pk>', views.send_message),
]

# {
 
 


# }

