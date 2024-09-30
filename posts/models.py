from django.db import models
from django.contrib.auth.models import User
from health.models import FoodUpload

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_uploads = models.ManyToManyField(FoodUpload)  # 여러 음식을 저장할 수 있도록 다대다 관계로 설정
    title = models.CharField(max_length=255)  # 제목 필드 추가
    caption = models.TextField(blank=True)  # 사용자가 입력하는 캡션    
    total_calories = models.FloatField(null=True, blank=True)
    total_protein = models.FloatField(null=True, blank=True)
    total_fat = models.FloatField(null=True, blank=True)
    total_carbs = models.FloatField(null=True, blank=True)
    goal_calories = models.FloatField(null=True, blank=True)
    goal_protein = models.FloatField(null=True, blank=True)
    goal_fat = models.FloatField(null=True, blank=True)
    goal_carbs = models.FloatField(null=True, blank=True)
    result = models.CharField(max_length=50)  # 성공 여부 (성공/실패)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s post"

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'post')  # 유저와 게시물의 조합은 유일해야 함

    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"
