from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer

from .models import AccessLevel, Board, BoardAccess, Stage, Tag, Task, User


class AuthSerializer(AuthTokenSerializer):
    token = None


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "avatar",
            "email",
            "password",
            "first_name",
            "last_name",
            "last_login",
            "date_joined",
        )
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ("id", "last_login", "date_joined")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        if password := validated_data.pop("password", None):
            instance.set_password(password)
        return super().update(instance, validated_data)


class UserSerializer(UserDetailSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "avatar",
            "first_name",
            "last_name",
            "last_login",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "description",
            "modified_at",
            "created_at",
        )


class TagSerializer(TagSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
        )


class TaskDetailSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Task
        fields = (
            "id",
            "name",
            "description",
            "body",
            "priority",
            "archived",
            "tags",
            "stage",
            "modified_at",
            "created_at",
        )


class TaskSerializer(TaskDetailSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "name",
            "description",
            "tags",
            "priority",
        )


class StageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = (
            "id",
            "name",
            "description",
            "priority",
            "archived",
            "board",
            "modified_at",
            "created_at",
        )


class StageSerializer(StageDetailSerializer):
    class Meta:
        model = Stage
        fields = (
            "id",
            "name",
            "priority",
        )


class BoardDetailAccessSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = BoardAccess
        fields = (
            "id",
            "user",
            "board",
            "level",
            "modified_at",
            "created_at",
        )


class BoardDetailSerializer(serializers.ModelSerializer):

    access_level = serializers.SerializerMethodField()
    # stages = StageSerializer(many=True, read_only=True)

    def get_access_level(self, obj) -> int:
        try:
            return BoardAccess.objects.get(
                user=self.context["request"].user, board=obj
            ).level
        except BoardAccess.DoesNotExist:
            return AccessLevel.NONE

    def create(self, validated_data):
        board = super().create(validated_data)
        # create owner level access for the user
        BoardAccess.objects.create(
            user=self.context["request"].user,
            board=board,
            level=AccessLevel.OWNER,
        )
        return board

    class Meta:
        model = Board
        fields = (
            "id",
            "name",
            "description",
            "archived",
            "modified_at",
            "created_at",
            "access_level",
            # "stages",
        )


class BoardSerializer(BoardDetailSerializer):
    class Meta:
        model = Board
        fields = (
            "id",
            "name",
            "description",
            "archived",
            "modified_at",
            "created_at",
            "access_level",
        )
