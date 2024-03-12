"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import CookieMiddleware
from django.core.asgi import get_asgi_application
from apps.notifications import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()


application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": application,
    "websocket": URLRouter(routing.websocket_urlpatterns),
})
