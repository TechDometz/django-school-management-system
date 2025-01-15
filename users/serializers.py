from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


from .models import Accountant, CustomUser


class UserSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)
    isAccountant = serializers.SerializerMethodField(read_only=True)
    isTeacher = serializers.SerializerMethodField(read_only=True)
    isParent = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "middle_name",
            "last_name",
            "isAdmin",
            "isAccountant",
            "isTeacher",
            "isParent",
        ]

    def get_isAdmin(self, obj):
        return obj.is_staff

    def get_isAccountant(self, obj):
        return obj.is_accountant

    def get_isTeacher(self, obj):
        return obj.is_teacher

    def get_isParent(self, obj):
        return obj.is_parent

    def get_username(self, obj):
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.email or "Unknown User"


class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    user_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "middle_name",
            "last_name",
            "isAdmin",
            "user_type",
            "token",
        ]

    def get_token(self, obj):
        try:
            token = RefreshToken.for_user(obj)
            return str(token.access_token)
        except Exception as e:
            return None

    def get_user_type(self, obj):
        roles = ["is_accountant", "is_teacher", "is_parent"]
        for role in roles:
            if getattr(obj, role, False):
                return {role: True}
        return {"unknown": True}


class AccountantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Accountant
        fields = "__all__"
