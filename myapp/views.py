from django.shortcuts import render
from .models import YouTubeComment
import matplotlib.pyplot as plt
import io, base64
import pandas as pd

def index(request):
    comments = YouTubeComment.objects.all()[:100]
    df = pd.DataFrame(list(comments.values('like_count', 'reply_count', 'author')))

    graphic = None
    if not df.empty:
        fig, ax = plt.subplots()
        ax.scatter(df['like_count'], df['reply_count'], alpha=0.7)
        ax.set_xlabel("Likes")
        ax.set_ylabel("Replies")
        ax.set_title("YouTube Comment Engagement")

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        graphic = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

    return render(request, 'index.html', {'graphic': graphic, 'comments': comments})

def pricing(request):
    return render(request, "pricing.html")
