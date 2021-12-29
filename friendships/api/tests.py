from django.test import TestCase
from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase

FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        self.anonymous_client = APIClient()
        self.zora = self.create_user('zora')
        self.zora_client = APIClient()
        self.zora_client.force_authenticate(self.zora)

        self.daniel = self.create_user('daniel')
        self.daniel_client = APIClient()
        self.daniel_client.force_authenticate(self.daniel)

        # create followings and followers for daniel
        for i in range(2):
            follower = self.create_user('daniel_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.daniel)

        for i in range(3):
            following = self.create_user('daniel_following{}'.format(i))
            Friendship.objects.create(from_user=self.daniel, to_user=following)

    def test_follow(self):
        url = FOLLOW_URL.format(self.zora.id)

        # 需要登录才可以follow别人
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # 用get来follow是不行的，需要用post
        response = self.daniel_client.get(url)
        self.assertEqual(response.status_code, 405)

        # 不可以 follow 自己
        response = self.zora_client.post(url)
        self.assertEqual(response.status_code, 400)

        # follow 成功
        response = self.daniel_client.post(url)
        self.assertEqual(response.status_code, 201)

        # 重复 follow 静默成功
        response = self.daniel_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicate'], True)

        # 反向关注会创建新的数据
        count = Friendship.objects.count()
        response = self.zora_client.post(FOLLOW_URL.format(self.daniel.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.zora.id)

        # 需要登陆才能 unfollow 别人
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # 不能用 get 来 unfollow 别人
        response = self.daniel_client.get(url)
        self.assertEqual(response.status_code, 405)
        # 不能 unfollow 自己
        response = self.zora_client.post(url)
        self.assertEqual(response.status_code, 400)
        # unfollow 成功
        Friendship.objects.create(from_user=self.daniel, to_user=self.zora)
        count = Friendship.objects.count()
        response = self.daniel_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)
        # 在未 unfollow 的情况下 unfollow 静默处理
        count = Friendship.objects.count()
        response = self.daniel_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.daniel.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)

        # make sure it is ordered by the latest first
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'daniel_following2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'daniel_following1'
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'daniel_following0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.daniel.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)

        # make sure the latest first
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'daniel_follower1'
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'daniel_follower0'
        )






