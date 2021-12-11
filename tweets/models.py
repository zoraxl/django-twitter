from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='who posts this tweet',
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        # 这里是你执行print(tweet instance)的时候会显示的内容
        return f'{self.created_at} {self.user}: {self.content}'


