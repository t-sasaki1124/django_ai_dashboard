from django.db import models

class YouTubeComment(models.Model):
    video_id = models.CharField(max_length=50)
    comment_id = models.CharField(max_length=100, unique=True)
    author = models.CharField(max_length=100)
    comment_text = models.TextField()
    like_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    created_at = models.DateTimeField()
    engagement_score = models.FloatField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "YouTube Comment"
        verbose_name_plural = "YouTube Comments"

    def __str__(self):
        return f"{self.author}: {self.comment_text[:40]}..."
