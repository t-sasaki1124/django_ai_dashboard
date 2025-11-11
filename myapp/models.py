from django.db import models

class YouTubeComment(models.Model):
    video_id = models.CharField(max_length=50)
    comment_id = models.CharField(max_length=50)
    comment_text = models.TextField()
    author = models.CharField(max_length=100)
    like_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(null=True, blank=True)
    reply_depth_potential = models.IntegerField(default=0)
    engagement_score = models.FloatField(default=0)
    ai_reply = models.TextField(null=True, blank=True)
    embedding = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "YouTube Comment"
        verbose_name_plural = "YouTube Comments"

    def __str__(self):
        return f"{self.author}: {self.comment_text[:40]}..."
