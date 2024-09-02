from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "image",
            "optimized_image",
        )
        read_only_fields = ["id", "optimized_image"]


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate_phone_number(self, value):
        numbers = "".join([str(i) for i in str(value) if i.isdigit()])
        if len(numbers) == 11:
            if numbers.startswith("374"):
                return numbers
            if numbers[0] == "7":
                return numbers
            elif numbers[0] == "8":
                return "7" + numbers[1:]
            else:
                return serializers.ValidationError(
                    detail="Номер телефона введен неверно!"
                )
        elif len(numbers) == 12 and numbers.startswith(("375", "972", "996", "358")):
            return numbers
        raise serializers.ValidationError(detail="Номер телефона введен неверно!")


class UserIdOfUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
