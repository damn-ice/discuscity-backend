from django.db import models
from django.contrib.auth.models import User


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    pix = models.ImageField(default="profile.png")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name

class Section(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Topic(models.Model):
    title = models.CharField(max_length=200)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='topics')
    created = models.DateTimeField(auto_now_add=True)
    isFront = models.BooleanField(default=False)
    # Necessary... 24/4/21
    # consider ....
    # created = models.DateTime...

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title

class Post(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='posts')
    message = models.TextField()
    date = models.CharField(max_length=100)

    def __str__(self):
        if len(self.message) < 50:
            return self.message
        return f'{self.message[:50]}...'

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    like = models.CharField(max_length=50)

    def __str__(self):
        return self.like
    

class Dislike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='dislikes')
    dislike = models.CharField(max_length=50)
    
    def __str__(self):
        return self.dislike
    