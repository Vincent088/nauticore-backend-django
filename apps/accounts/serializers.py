from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Profile
from core.validators import (
    validate_name,
    validate_username,
    validate_email_field,
    validate_password_field,
    validate_phone,
    validate_no_emoji,
    validate_no_sql_xss,
)


class ProfileSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        required=False, allow_blank=True, validators=[validate_phone]
    )
    department = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
        validators=[validate_no_emoji, validate_no_sql_xss],
    )
    employee_id = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=50,
        validators=[validate_no_emoji, validate_no_sql_xss],
    )
    bio = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        validators=[validate_no_emoji, validate_no_sql_xss],
    )

    class Meta:
        model = Profile
        fields = ["avatar", "phone", "department", "employee_id", "bio"]

    def validate_avatar(self, value):
        if value:
            # max 2MB
            if value.size > 2 * 1024 * 1024:
                raise serializers.ValidationError("Avatar image cannot exceed 2MB.")
            # only image files
            allowed_types = ["image/jpeg", "image/png", "image/webp"]
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    "Only JPEG, PNG, and WebP images are allowed."
                )
        return value


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "profile",
        ]
        read_only_fields = ["id", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        required=True, max_length=100, validators=[validate_name]
    )
    last_name = serializers.CharField(
        required=True, max_length=100, validators=[validate_name]
    )
    username = serializers.CharField(required=True, validators=[validate_username])
    email = serializers.EmailField(required=True, validators=[validate_email_field])
    password = serializers.CharField(
        write_only=True, validators=[validate_password_field]
    )
    password2 = serializers.CharField(write_only=True, label="Confirm password")

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
        ]

    def validate_username(self, value):
        value = validate_username(value)
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "This username is already taken. Please choose another."
            )
        return value

    def validate_email(self, value):
        value = validate_email_field(value)
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        user = CustomUser.objects.create_user(**validated_data)
        Profile.objects.create(user=user)
        return user


class CustomTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username", "").strip()
        password = data.get("password", "")

        if not username:
            raise serializers.ValidationError({"username": "Username is required."})

        if not password:
            raise serializers.ValidationError({"password": "Password is required."})

        # sanitize username input
        if len(username) > 30:
            raise serializers.ValidationError({"username": "Invalid username."})

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                {"username": "No account found with this username."}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {
                    "username": "This account has been deactivated. Contact your administrator."
                }
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"password": "Incorrect password. Please try again."}
            )

        data["user"] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password_field]
    )
    new_password2 = serializers.CharField(write_only=True, label="Confirm new password")

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Your current password is incorrect.")
        return value

    def validate(self, data):
        if data["new_password"] != data["new_password2"]:
            raise serializers.ValidationError(
                {"new_password": "New passwords do not match."}
            )
        if data["old_password"] == data["new_password"]:
            raise serializers.ValidationError(
                {
                    "new_password": "New password must be different from your current password."
                }
            )
        return data

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
