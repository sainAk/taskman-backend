from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound

from utils.views.base import BaseModelViewSet

from .models import AccessLevel, Board, BoardAccess, Stage, Tag, Task, User
from .permissions import BoardAccessPermission, IsSelfOrReadOnly
from .serializers import (
    BoardDetailAccessSerializer,
    BoardSerializer,
    BoardDetailSerializer,
    StageSerializer,
    StageDetailSerializer,
    TagSerializer,
    TagSerializer,
    TaskSerializer,
    TaskDetailSerializer,
    UserDetailSerializer,
)


class BaseApiViewSet(BaseModelViewSet):
    permission_classes = (BoardAccessPermission,)


@extend_schema_view(
    destroy=extend_schema(exclude=True),
    list=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
)
class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    def get_permissions(self):
        if self.action == "create":
            return (permissions.AllowAny(),)
        return (IsSelfOrReadOnly(),)

    def get_object(self):
        return (
            super().get_object()
            if self.kwargs.get(self.lookup_field)
            else self.request.user
        )

    def list(self, request, *args, **kwargs):
        raise NotFound

    @action(detail=False)
    def me(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @me.mapping.patch
    def partial_update_me(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @me.mapping.delete
    def destroy_me(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class BoardViewSet(BaseModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    serializer_action_classes = {
        "list": BoardSerializer,
    }

    def get_permissions(self):
        return (BoardAccessPermission(AccessLevel.READ_ONLY, AccessLevel.ADMIN),)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            qs = qs.filter(Q(access__id=self.request.user.id) | Q(public=True))
        return qs


class BoardAccessViewSet(BaseModelViewSet):
    queryset = BoardAccess.objects.all()
    serializer_class = BoardDetailAccessSerializer

    def get_permissions(self):
        return (BoardAccessPermission(AccessLevel.READ_ONLY, AccessLevel.OWNER),)

    def get_queryset(self):
        qs = super().get_queryset()
        if board_pk := self.kwargs.get("board_pk"):
            qs.filter(board=board_pk)
        if self.action == "list":
            qs = qs.filter(access__id=self.request.user.id)
        return qs


class StageViewSet(BaseApiViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageDetailSerializer
    serializer_action_classes = {
        "list": StageSerializer,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        if board_pk := self.kwargs.get("board_pk"):
            qs.filter(board=board_pk)
        if self.action == "list":
            qs = qs.filter(
                Q(board__access__id=self.request.user.id) | Q(board__public=True)
            )
        return qs


class TagViewSet(BaseApiViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    serializer_action_classes = {
        "list": TagSerializer,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        if board_pk := self.kwargs.get("board_pk"):
            qs.filter(board__id=board_pk)
        if self.action == "list":
            qs = qs.filter(
                Q(board__access__id=self.request.user.id) | Q(board__public=True)
            )
        return qs


class TaskViewSet(BaseApiViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    serializer_action_classes = {
        "list": TaskSerializer,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        if board_pk := self.kwargs.get("board_pk"):
            qs.filter(board=board_pk)
        if stage_pk := self.kwargs.get("stage_pk"):
            qs.filter(stage=stage_pk)
        if self.action == "list":
            qs = qs.filter(
                Q(board__access__id=self.request.user.id) | Q(board__public=True)
            )
        return qs
