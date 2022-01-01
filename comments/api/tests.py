from testing.testcases import TestCase
from rest_framework.test import APIClient

COMMENT_URL = '/api/comments'

class CommentApiTests(TestCase):

    def setUp(self):

        self.zora = self.create_user('zora')
        self.zora_client = APIClient()
        self.zora_client.force_authenticate(self.zora)

        self.daniel = self.create_user('daniel')
        self.daniel_client = APIClient()
        self.daniel_client.force_authenticate(self.daniel)

        self.tweet = self.create_tweet(self.zora)

    def test_create(self):
        # 匿名不可以创建
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # 啥参数都没带不行
        response = self.zora_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # 只带 tweet_id 不行
        response = self.zora_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)

        # 只带 content 不行
        response = self.zora_client.post(COMMENT_URL, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        # content 太长不行
        response = self.zora_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # tweet_id 和 content 都带才行
        response = self.zora_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1',
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.zora)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')
