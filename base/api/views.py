from base.models import *
from .serializers import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework.response import Response # for rest framework api views
from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


# Show's us all the routes in our API
@api_view(['GET'])
def get_routes(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms:id'
    ]
    return Response(routes)

@api_view(['GET'])
@login_required(login_url='login')
def get_rooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)

@api_view(['GET','PUT','PATCH'])
@login_required(login_url='login')
def get_room(request, pk):
  try:
    room = Room.objects.get(id=pk)
    if request.method == 'GET':
        serializer = RoomSerializer(room, many=False)
        return Response(serializer.data)
    if request.method in ['PUT','PATCH']:
        serializer = RoomSerializer(room, data = request.data, partial = request.method == 'PATCH')
        if serializer.is_valid():
           serializer.save()
           return Response(serializer.data)
        
  except Exception as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

     
     

@api_view(['POST'])
@login_required(login_url='login')
def create_room(request):
   serializer = RoomSerializer(request.data)
   try:
     if(serializer.is_valid()):
        serializer.save()
        return Response(serializer.data)
   except Exception as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE']) 
def delete_room(request,pk):
   try:
      room = Room.objects.get(id=pk)
      room.delete()
   except Exception as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
      
        


@api_view(['POST'])
@login_required(login_url = 'login')
def send_message(request,pk):
  try:
    room = room.objects.get(id = pk)
    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message':'Message sent Successfully'},status=status.HTTP_201_CREATED)
  except Exception as e:
         return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@login_required(login_url = 'login')
def get_messages(request, pk):
  try:
    room = room.objects.get(id = pk)
    messages = Message.objects.get(room = room)
    serializer = MessageSerializer(messages,many=True)
    return Response(serializer.data)
    
  except Exception as e:
         return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@login_required(login_url='login')
def delete_message(request, pk):
  try:
      message = message.objects.get(id=pk)
      message.delete()
      return Response({'message': 'profile deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
  except Exception as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@login_required(login_url='login')
def create_topic(request):
   serializer = TopicSerializer(request.data)
   try:
    if serializer.is_valid():
        serializer.save()
        return Response({'message':'Topic Created Successfully'},status=status.HTTP_201_CREATED)
   except Exception as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
   
@api_view(['GET'])
def get_topics(request):
    topics = Topic.objects.all()
    serializer = TopicSerializer(topics, many=True)
    return Response(serializer.data)




       
   

