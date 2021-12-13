from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate
from tweets.models import Tweet
from rest_framework.response import Response


class TweetViewSet(viewsets.GenericViewSet):
    """
    API endpoint that allows user to create, list tweets
    """

    serializer_class = TweetSerializerForCreate

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]


    def list(self, request):
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status = 400)
        # 这句查询会被翻译为
        # select * from twitter_tweets
        # where user_id = xxx
        # order by created_at desc
        # 这句sql查询会用到user 和created_at 的联合索引
        # 单纯的user索引是不够的
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')

        serializer = TweetSerializer(tweets, many=True)
        serializer.data
        return Response({'tweets': serializer.data})

    def create(self, request):
        serializer = TweetSerializerForCreate(
            data = request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input.",
                "errors": serializer.errors,
            }, status=400)

        # save will call create method in TweetSerializerForCreate
        tweet = serializer.save()
        return Response(TweetSerializer(tweet).data, status=201)





