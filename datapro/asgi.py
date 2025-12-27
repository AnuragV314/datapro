"""
ASGI config for datapro project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import articles.routing

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datapro.settings')

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             articles.routing.websocket_urlpatterns
#         )
#     ),
# })




# import os
# import django
# from django.core.asgi import get_asgi_application
# from fastapi.middleware.wsgi import WSGIMiddleware
# from starlette.applications import Starlette
# from starlette.routing import Mount
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import articles.routing
# from apis.main import app as fastapi_app

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "datapro.settings")
# django.setup()

# # Django ASGI
# django_asgi_app = get_asgi_application()

# # Starlette (FastAPI + Django combined for HTTP)
# http_app = Starlette(routes=[
#     Mount("/apis", app=fastapi_app),   # FastAPI under /apis
#     Mount("", app=django_asgi_app),    # Django at root
# ])

# # Final ASGI application with WebSocket support
# application = ProtocolTypeRouter({
#     "http": http_app,   # All HTTP traffic goes here
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             articles.routing.websocket_urlpatterns
#         )
#     ),
# })



import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
from starlette.applications import Starlette
from starlette.routing import Mount
from fastapi.middleware.wsgi import WSGIMiddleware
from apis.main import app as fastapi_app
import articles.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "datapro.settings")
django.setup()

# Django ASGI app
django_asgi_app = get_asgi_application()

# Starlette app to mount FastAPI + Django HTTP
http_app = Starlette(routes=[
    Mount("/apis", app=fastapi_app),  # FastAPI
    Mount("", app=django_asgi_app),   # Django
])

# Channels ProtocolTypeRouter for HTTP + WebSocket
application = ProtocolTypeRouter({
    "http": http_app,  # All HTTP traffic
    "websocket": SessionMiddlewareStack(  # Ensures session cookie is passed
        AuthMiddlewareStack(
            URLRouter(
                articles.routing.websocket_urlpatterns
            )
        )
    ),
})

