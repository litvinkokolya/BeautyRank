from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.permissions import IsStaffOnly
from users.serializer import *
from users.smsc_api import send_sms
from users.utils import generate_password
from django.conf import settings


class UserViewSet(RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsStaffOnly]

    @action(
        detail=False,
        methods=["post"],
        serializer_class=LoginSerializer,
        permission_classes=[AllowAny],
    )
    def login_in(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.data["phone_number"]
        if phone_number:
            user = User.objects.filter(Q(phone_number=phone_number)).first()
            if user is None:
                user = User.objects.create(phone_number=phone_number)
            if user.is_superuser:
                return Response({"success": "Успешно!"})
            else:
                if settings.USE_SMSC:
                    random_number = generate_password()
                    send_sms(phone_number, random_number)
                else:
                    random_number = "0000"
                user.set_password(random_number)
                user.save()
                return Response({"success": "Успешно!"})
        return ValidationError(
            detail="Номер введён неверно", code=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False, methods=["get", "patch"], permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        if request.method == "PATCH":
            serializer = UserSerializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            request.user.refresh_from_db()
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
