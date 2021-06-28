from rest_framework.response import Response
from rest_framework import status

def unauthenticated(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response('authenticated user', status=status.HTTP_400_BAD_REQUEST)
        else:
            return view_func(request, *args, **kwargs)
    return wrapper