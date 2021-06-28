"""
WSGI config for discuscityBackend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import socketio
from api.views import sio
import eventlet

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discuscityBackend.settings')

# application = get_wsgi_application()
# The below was added...
django_app = get_wsgi_application()
application = socketio.WSGIApp(sio, django_app)
eventlet.wsgi.server(eventlet.listen(('', 8000)), application)
