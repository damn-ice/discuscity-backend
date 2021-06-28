import socketio
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .serializers import (
    LikeSerializer, DislikeSerializer,SectionSerializer, TopicSerializer, RegistrationSerializer, PersonSerializer,TopicSectionSerializer
)
from .models import Section, Post, Topic, Person, Like, Dislike
from .decorators import unauthenticated
from PIL import Image

# Consider putting a try except block in a get request in case of any errors...

# To automatically update the user total emotion consider using websocket to effect this change...

async_mode = None
sio = socketio.Server(async_mode=async_mode, cors_allowed_origins='*')
# sio = socketio.Server(async_mode=async_mode, logger=True, engineio_logger=True, cors_allowed_origins='*')
    
# We can use django code in ths sio.event...

def user_processed_data(person, likes, dislikes):
        person_serializer = PersonSerializer(person)
        # We simply could have used .count to get the number...
        #  but i chose to send the details of emotion...
        like_serializer = LikeSerializer(likes, many=True)
        dislike_serializer = DislikeSerializer(dislikes, many=True)
        data = dict(person_serializer.data)
        data['totalLikes'] = like_serializer.data
        data['totalDislikes'] = dislike_serializer.data
        return data

@sio.event
def sendMsg(sid, data):
    sio.emit('receive-msg', {'msg': data['result']}, room=data['room'], skip_sid=sid)
    print('sendMsg done!')

@sio.event
def sendEmotion(sid, data):
    sio.emit('receive-emotion', {'post': data['updatePost'], 'index': data['index']}, room=data['room'], skip_sid=sid)
    print('sendEmotion done!')

@sio.event
def connect(sid, environ, auth):
    print(dir(sid))
    print({'auth': auth})
    print('connected ---- ', sid)

@sio.event
def join(sid, data):
    sio.enter_room(sid, data)
    print('joined room')

@sio.event
def disconnect(sid):
    print('disconnect ===== ', sid)

@api_view(['GET'])
def index(request):
    if request.method == 'GET':
        sections = Section.objects.all()
        # print(request.META['REMOTE_ADDR'])
        # print(request.user.is_anonymous)
        # print(request.user, 'index')
        # print(dir(request.user))
        serializer = SectionSerializer(sections, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

def test(request):
    print(request)
    return Response('all good!', status=status.HTTP_200_OK)

@api_view(['POST'])
def image(request):
    if request.method == 'POST':
        image = request.data['image']
        try:
            test_image = Image.open(image)
            test_image.verify()
        except: 
            return Response('Invalid Image Type', status=status.HTTP_400_BAD_REQUEST)
        # Get the person instance 
        person = Person.objects.get(user=request.user)

        # Below code should be uncommented if we decide delete old pix...
        # if person.pix.name != 'profile.png':
        #     person.pix.delete()
        # replace the image and save to db
        person.pix = image
        person.save()
        likes = Like.objects.filter(post__sender=request.user)
        dislikes = Dislike.objects.filter(post__sender=request.user)
        data = user_processed_data(person, likes, dislikes)
        return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
def update(request):
    if request.method == 'POST':
        person = Person.objects.get(user=request.user)
        person = PersonSerializer(person, data=request.data, partial=True)
        if person.is_valid():
            updated_person = person.save()
        else:
            return Response(person.errors, status=status.HTTP_400_BAD_REQUEST)
        likes = Like.objects.filter(post__sender=request.user)
        dislikes = Dislike.objects.filter(post__sender=request.user)
        data = user_processed_data(updated_person, likes, dislikes)       
        return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def home(request):
    if request.method == 'GET':
        topics = Topic.objects.filter(isFront=True)
        serializer = TopicSectionSerializer(topics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def current(request):
    if not request.user.is_anonymous:
        person = Person.objects.get(user=request.user)
        likes = Like.objects.filter(post__sender=request.user)
        dislikes = Dislike.objects.filter(post__sender=request.user)
        data = user_processed_data(person, likes, dislikes)
        return Response(data, status=status.HTTP_200_OK)
    return Response('unauthenticated', status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create(request):
    section = Section.objects.get(name=request.data['section'].title())
    new_topic = Topic.objects.create(section=section, title=request.data['title'])
    Post.objects.create(
        sender=request.user, topic=new_topic, message=request.data['post'], date=request.data['date'])
    return Response('success', status=status.HTTP_200_OK)

@api_view(['GET'])
def topics(request):
    if request.method == 'GET':
        topics = Topic.objects.all()
        serializer = TopicSerializer(topics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def section(request, name):
    # The below is necessary because all section name are capitalized...
    # Enforce capitalization at the model saving, this might bring up errors when creating from admin...
    section = Section.objects.get(name=name.title())
    topics = Topic.objects.filter(section=section)
    serializer = TopicSectionSerializer(topics, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Create new post...
# Poor naming but honestly don't have time to trace it...
@permission_classes([IsAuthenticated])
@api_view(['GET', 'POST'])
def topic(request, name, topic_id):
    # All Sections are in Title...
    # Poor Implementation I know...
    name = name.title()
    section = Section.objects.get(name=name)
    topic = Topic.objects.filter(section=section).get(id=topic_id)

    if request.method == 'POST':
        # print(request.data)
        if request.user.is_anonymous:
            return Response('unauthorised', status=status.HTTP_403_FORBIDDEN)
        post = Post.objects.create(
            sender=request.user,
            topic=topic,
            message=request.data.get('message'),
            date=request.data.get('date')
        )
    serializer = TopicSerializer(topic)
    return Response(serializer.data, status=status.HTTP_200_OK )

# handle emotion...
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def emotion(request):
    post = Post.objects.get(id=request.data.get('post_id'))

    if request.data.get('emotion') == 'likes':
        if request.data.get('create'):
            Like.objects.create(post=post, like=request.data.get('reacted_user'))
            if request.data.get('opposing'):
                Dislike.objects.filter(post=post).get(dislike=request.data.get('reacted_user')).delete()
        elif not request.data.get('create'):
            Like.objects.filter(post=post).get(like=request.data.get('reacted_user')).delete()

    elif request.data.get('emotion') == 'dislikes':
        if request.data.get('create'):
            Dislike.objects.create(post=post, dislike=request.data.get('reacted_user'))
            if request.data.get('opposing'):
                Like.objects.filter(post=post).get(like=request.data.get('reacted_user')).delete()
        elif not request.data.get('create'):
            Dislike.objects.filter(post=post).get(dislike=request.data.get('reacted_user')).delete()
    return Response('success', status=status.HTTP_200_OK)

# Allow only unauthenticated user...
# @unauthenticated
@api_view(['POST'])
def registerView(request):
    serializer = RegistrationSerializer(data=request.data)   
    if serializer.is_valid():
        serializer.save()
        return Response('success', status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Allow only unauthenticated user...
# @unauthenticated .... Client is handling it....
@api_view(['POST'])
def loginView(request):
    username = request.data['username']
    password = request.data['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        person = Person.objects.get(user=user)
        likes = Like.objects.filter(post__sender=user)
        dislikes = Dislike.objects.filter(post__sender=user)
        data = user_processed_data(person, likes, dislikes)
        return Response(data, status=status.HTTP_200_OK)
    return Response('Username or Password is incorrect!', status=status.HTTP_400_BAD_REQUEST)

# Allow only logged in user
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def logoutView(request):
    logout(request)
    return Response('success', status=status.HTTP_200_OK)