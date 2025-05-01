import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import chat_app.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_project.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat_app.routing.websocket_urlpatterns
        )
    ),
})
