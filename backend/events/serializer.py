from rest_framework import serializers

from events.models import *


class ResultSerializer(serializers.ModelSerializer):
    event_staff_name = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = (
            "member_nomination",
            "score",
            "event_staff",
            "event_staff_name",
            "score_retail",
        )

    def get_event_staff_name(self, obj) -> str:
        return str(obj.event_staff) if obj.event_staff else None


class MemberNominationPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberNominationPhoto
        fields = (
            "id",
            "member_nomination",
            "photo",
            "optimized_photo",
            "before_after",
            "name",
        )
        read_only_fields = ["id", "optimized_photo"]

    def validate(self, attrs):
        if self.context["request"].user != attrs["member_nomination"].member.user:
            raise serializers.ValidationError("Запрещено загружать фото в чужую работу")
        return super().validate(attrs)


class MemberNominationSerializer(serializers.ModelSerializer):
    nomination = serializers.CharField(
        source="category_nomination.nomination.name", read_only=True
    )
    nomination_info = serializers.JSONField(
        source="category_nomination.nomination.photos_conf", read_only=True
    )
    category = serializers.CharField(
        source="category_nomination.event_category.category.name", read_only=True
    )
    id_member = serializers.IntegerField(source="member.user.id", read_only=True)
    member = serializers.CharField(source="member.user", read_only=True)
    result_sum = serializers.IntegerField(source="result_all", read_only=True)
    preview = serializers.SerializerMethodField()
    is_done = serializers.BooleanField(read_only=True)

    class Meta:
        model = MemberNomination
        fields = (
            "id",
            "nomination",
            "nomination_info",
            "category",
            "id_member",
            "member",
            "result_sum",
            "is_done",
            "preview",
            "url_video",
            "url_message_video",
        )
        read_only_fields = [
            "id",
            "nomination",
            "nomination_info",
            "category",
            "id_member",
            "member",
            "result_sum",
            "is_done",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        unique_results = instance.results.order_by("event_staff").distinct(
            "event_staff"
        )

        representation["result_sum"] = sum(result.score for result in unique_results)

        return representation

    def get_preview(self, obj) -> str:
        preview = obj.photos.first()
        if preview:
            return preview.optimized_photo.url
        else:
            return None


class CategoryNominationSerializer(serializers.ModelSerializer):
    member_nomination = MemberNominationSerializer(many=True, read_only=True)

    class Meta:
        model = CategoryNomination
        fields = ("event_category", "nomination", "member_nomination")


class EventSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ("id", "name", "image", "finished", "result", "role")
        read_only_fields = ["id", "name", "result", "image", "role"]

    def get_role(self, obj) -> str:
        user = self.context.get("request").user
        event = obj
        if CategoryNomination.objects.filter(
            event_category__event__pk=event.pk, event_staff=user
        ).exists():
            return "Судья"

        if Member.objects.filter(event__pk=event.pk, user=user).exists():
            return "Мастер"

        if Event.objects.filter(pk=event.pk, owners=user).exists():
            return "Организатор"

        return "Unknown role"


class MemberNominationSerializerForWinners(serializers.ModelSerializer):
    member = serializers.CharField(source="member.user", read_only=True)
    member_id = serializers.IntegerField(source="member.user_id", read_only=True)
    result_all = serializers.IntegerField(read_only=True)

    class Meta:
        model = MemberNomination
        fields = ("id", "member", "member_id", "result_all")
        read_only_fields = ["id"]


class CategoryWinnersSerializer(serializers.Serializer):
    name = serializers.CharField()
    members = MemberNominationSerializerForWinners(many=True)


class NominationWinnersSerializer(serializers.Serializer):
    category = serializers.CharField()
    name = serializers.CharField()
    members = MemberNominationSerializerForWinners(many=True)


class NominationAttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NominationAttribute
        fields = ("name", "max_score")
        read_only_fields = ["id", "name", "max_score"]
