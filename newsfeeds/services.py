from newsfeeds.models import NewsFeed
from friendships.services import  FriendshipService

class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):

        # 不可以将数据库的操作放在for循环里面，效率会非常低
        # 正确的做法是用bulk_create 会把insert语句合成一条
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)
