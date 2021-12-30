from newsfeeds.models import NewsFeed
from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase

NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'

class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.zora = self.create_user('zora')
        self.zora_client = APIClient()
        self.zora_client.force_authenticate(self.zora)

        self.daniel = self.create_user('daniel')
        self.daniel_client = APIClient()
        self.daniel_client.force_authenticate(self.daniel)

        # create followings and followers for daniels
        for i in range(2):
            follower = self.create_user('daniel_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.daniel)

        for i in range(3):
            following = self.create_user('daniel_following{}'.format(i))
            Friendship.objects.create(from_user=self.daniel, to_user=following)


    def test_list(self):

        # 需要登陆
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)
        # 不能用post
        response = self.zora_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)
        # 一开始啥也没有
        response = self.zora_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 0)
        # 自己发的信息是可以看到的
        self.zora_client.post(POST_TWEETS_URL, {'content': 'HELLO WORLD'})
        response = self.zora_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 1)
        # 关注之后可以看到关注的人发的feed
        self.zora_client.post(FOLLOW_URL.format(self.daniel.id))
        response = self.daniel_client.post(POST_TWEETS_URL, {
            'content': 'Hello world!!'
        })
        posted_tweet_id = response.data['id']
        response = self.zora_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeed']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'], posted_tweet_id)
