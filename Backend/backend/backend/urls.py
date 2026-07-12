"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle


class LoginView(ObtainAuthToken):
    """Token login, rate-limited to blunt credential brute-forcing.

    ObtainAuthToken keeps `permission_classes = ()`, so this endpoint stays public;
    we only add a scoped throttle (rate from REST_FRAMEWORK["login"]).

    Each login rotates the token: the old one is deleted and a fresh one issued, so
    expiry is measured from now (see ExpiringTokenAuthentication) and any previously
    leaked token immediately stops working.
    """

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        return Response({"token": token.key})


@api_view(["POST"])
def logout_view(request):
    """Server-side logout: revoke the caller's token so it can't be reused."""
    Token.objects.filter(user=request.user).delete()
    return Response({"message": "Logged out."})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("api/login/", LoginView.as_view(), name="api-login"),
    path("api/logout/", logout_view, name="api-logout"),
]
