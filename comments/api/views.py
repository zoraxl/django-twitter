from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
)

class CommentViewset(viewsets.GenericViewSet):
    """
    只实现list, create, update, destroy 的方法
    不实现 retrieve (查询单个comment）的方法， 因为这个没有需求
    """
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()

    def get_permissions(self):
        """
        注意要用 AllowAny()/ IsAuthenticated() 实例化出对象
        而不是 AllowAny / IsAuthenticated 这样只是一个类名
        """
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content')
        }
        # 注意这里必须要 'data=' 来指定参数是传给data的
        # 因为默认的第一个参数是 instance
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # save 方法会触发 serializer 里的 create 方法，点进 save 的具体实现里可以看到
        comment = serializer.save()
        return Response(
            CommentSerializerForCreate(comment).data,
            status=status.HTTP_201_CREATED,
        )
