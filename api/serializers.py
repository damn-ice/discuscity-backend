from django.db.models import fields
from rest_framework import serializers
from .models import Section, Post, Topic, Like, Dislike, Person
from django.contrib.auth.models import User
from django.db import IntegrityError


class PersonDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['first_name', 'pix', 'created']

class UserDataSerializer(serializers.ModelSerializer):
    person = PersonDataSerializer()
    class Meta: 
        model = User
        fields = ['username', 'person', 'last_login']
class SectionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Section
        fields = ['name']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['like']

class DislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dislike
        fields = ['dislike']

class PersonSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field='username'
    )
    class Meta:
        model = Person
        fields = ['user', 'first_name', 'last_name', 'email', 'pix', 'created']


class PostSerializer(serializers.ModelSerializer):

    likes = LikeSerializer(many=True, read_only=True)
    dislikes = DislikeSerializer(many=True, read_only=True)
    sender = UserDataSerializer()

    # sender = serializers.SlugRelatedField(
    #     queryset=User.objects.all(), slug_field='username'
    # )
    class Meta:
        model = Post
        fields = ['id', 'sender', 'message', 'date', 'likes', 'dislikes']

class TopicSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = ['title', 'posts']

class TopicSectionSerializer(serializers.ModelSerializer):
    section = serializers.SlugRelatedField(
        queryset=Section.objects.all(), slug_field='name'
    )
    class Meta:
        model = Topic
        fields = ['id', 'title', 'section']

class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, style={'input-type': 'password'})
    class Meta:
        model = User
        # Seems we need to first create the user object
        fields = ['username', 'first_name', 'last_name','email', 'password', 'password2']
        # This ensures the field is not serialized...
        extra_kwargs = {
            'password':{'write_only': True},
        }

    def save(self):
        email = self.validated_data['email']
        username = self.validated_data['username']
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        password=self.validated_data['password']
        password2=self.validated_data['password2']
        
        user = User(email=email, username=username, first_name=first_name, last_name=last_name)
        # Could have made a custom user but this is a prototype used filter to ensure unique email...

        if password != password2:
            raise serializers.ValidationError({'password': 'Password doesnt match!'})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email Already Exists!'})
        user.set_password(password)
        user.save()
        # Could have made a Custom model manager and handled this creation...
        person = Person.objects.create(user=user, first_name=first_name, last_name=last_name, email=email)
        
        return person
