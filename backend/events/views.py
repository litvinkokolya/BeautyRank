from django.db.models import BooleanField, Case, F, Q, When, Count, Value, IntegerField, OuterRef, Subquery, Exists
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from RateOnline import settings
from events.paginator import MemberNominationsPaginator
from events.permissions import (
    IsMemberOrReadOnly,
    IsStaffOrReadOnly,
    TelegramBotUpdate,
    IsOwnerOnly,
)
from events.serializer import *


class MemberNominationViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Viewset для управления объектами MemberNomination.
    Предоставляет действия для получения списка, получения и обновления объектов.
    """

    queryset = MemberNomination.objects.all()
    serializer_class = MemberNominationSerializer
    pagination_class = MemberNominationsPaginator
    filterset_fields = ["category_nomination__event_category__event", "is_done"]
    permission_classes = [TelegramBotUpdate]

    def get_queryset(self):
        """
        Возвращает queryset для объектов MemberNomination.
        Если запрос не от телеграмм-бота, то добавляет дополнительные поля и фильтры.
        """
        queryset = super().get_queryset()

        if not self.request.data.get("user", "client") == "telegram":
            queryset = (
                queryset
                .filter(
                    Q(member__user=self.request.user)
                    | Q(category_nomination__event_staff=self.request.user)
                    | Q(
                        category_nomination__event_category__event__owners=self.request.user
                    )
                    | Q(
                        category_nomination__event_category__event__members__user=self.request.user,
                        is_done=True,
                    )
                ).distinct()
            )

            if self.request.user.id in queryset.values_list('category_nomination__event_staff', flat=True):
                has_result = Subquery(Result.objects.filter(event_staff_id=self.request.user.id, member_nomination=OuterRef('pk')))
                queryset = queryset.filter(photos__isnull=False).annotate(
                    has_result=Exists(has_result)
                ).order_by('has_result')

            elif self.request.user.id in queryset.values_list('member__user', flat=True):
                queryset = queryset.annotate(
                    is_current_member=Case(
                        When(member__user=self.request.user, then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                ).order_by('-is_current_member')

            return queryset
        return super().get_queryset()


class MemberNominationPhotoViewSet(
    ListModelMixin, CreateModelMixin, viewsets.GenericViewSet
):
    """
    Viewset для управления объектами MemberNominationPhoto.
    Предоставляет действия для получения списка и создания объектов.
    """

    queryset = MemberNominationPhoto.objects.all()
    serializer_class = MemberNominationPhotoSerializer
    filterset_fields = ["member_nomination"]
    ordering_fields = ["before_after"]
    permission_classes = [IsMemberOrReadOnly]

    def get_queryset(self):
        """
        Возвращает queryset для объектов MemberNominationPhoto.
        Добавляет дополнительные поля и фильтры.
        """
        queryset = (
            super()
            .get_queryset()
            .annotate(
                count_results=Count("member_nomination__results"),
                count_staffs=Count(
                    "member_nomination__category_nomination__event_staff"
                ),
            )
            .annotate(
                is_done=Case(
                    When(count_results=F("count_staffs"), then=True),
                    default=False,
                    output_field=BooleanField(),
                )
            )
            .filter(
                Q(member_nomination__member__user=self.request.user)
                | Q(
                    member_nomination__category_nomination__event_staff=self.request.user
                )
                | Q(
                    member_nomination__category_nomination__event_category__event__owners=self.request.user
                )
                | Q(
                    member_nomination__category_nomination__event_category__event__members__user=self.request.user,
                    is_done=True,
                )
            )
            .distinct()
        )
        return queryset


class ResultViewSet(ListModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    """
    Viewset для управления объектами Result.
    Предоставляет действия для получения списка и создания объектов.
    """

    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    filterset_fields = ["member_nomination"]
    permission_classes = [IsStaffOrReadOnly]


class EventViewSet(
    UpdateModelMixin, ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet
):
    """
    Viewset для управления объектами Event.
    Предоставляет действия для получения списка; определенного объекта по его ID; а также обновление мероприятия.
    Показывает роль пользователя в этом мероприятии при запросе.
    """

    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.action in [
            "partial_update",
            "update",
            "winners_nominations",
            "winners_of_categories",
        ]:
            permission_classes = [IsOwnerOnly]
        elif self.action == "top_100":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["get"], permission_classes=[IsOwnerOnly])
    def winners_nominations(self, request, *args, **kwargs):
        event = self.get_object()
        win_nominations = event.get_winners_nominations()
        serializer = NominationWinnersSerializer(win_nominations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], permission_classes=[IsOwnerOnly])
    def winners_of_categories(self, request, *args, **kwargs):
        event = self.get_object()
        win_categories = event.get_winners_categories()
        serializer = CategoryWinnersSerializer(win_categories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def top_100(self, request, *args, **kwargs):
        results = []
        for event in Event.objects.filter(finished=True):
            event_result = event.result
            for category in event_result["categories"]:
                for nomination in category["nominations"]:
                    for member in nomination["members"]:
                        if member["user_avatar"]:
                            s3_storage = PrivateMediaStorage(
                                bucket_name=settings.AWS_STORAGE_BUCKET_NAME
                            )
                            url = s3_storage.url(member["user_avatar"])
                            member["user_avatar"] = url
            results.append(event_result)
        return Response(data=results)


class NominationAttributeViewSet(ListModelMixin, viewsets.GenericViewSet):
    """
    Viewset для управления объектами NominationAttribute.
    Предоставляет действие для получения списка аттрибутов номинации и её максимальная оценка.
    """

    queryset = NominationAttribute.objects.all()
    serializer_class = NominationAttributesSerializer
    filterset_fields = ["nomination__nom__categ__id"]
