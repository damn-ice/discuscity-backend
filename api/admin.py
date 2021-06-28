from django.contrib import admin
from .models import *

admin.site.register(Person)
admin.site.register(Section)
admin.site.register(Topic)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Dislike)
