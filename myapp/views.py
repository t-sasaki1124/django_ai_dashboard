from django.shortcuts import render
from .models import YouTubeComment

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import io
import base64
import pandas as pd


def index(request):
    comments = YouTubeComment.objects.all()[:300]

    df = pd.DataFrame(list(comments.values(
        "like_count",
        "reply_count",
        "created_at",
        "author",
    )))

    graphic_3d = None

    if not df.empty:
        df["created_at_num"] = df["created_at"].astype("int64") // 10**9

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection="3d")

        sc = ax.scatter(
            df["like_count"],
            df["reply_count"],
            df["created_at_num"],
            c=df["created_at_num"],  # 作成日時で色分け
            cmap="viridis",
            alpha=0.85,
            s=40,
        )

        ax.set_xlabel("Likes")
        ax.set_ylabel("Replies")
        ax.set_zlabel("Created (timestamp)")
        ax.set_title("3D YouTube Comment Engagement")

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=120)
        buffer.seek(0)
        graphic_3d = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()

        plt.close(fig)

    return render(request, "index.html", {
        "graphic_3d": graphic_3d,
        "comments": comments,
    })


def pricing(request):
    return render(request, "pricing.html")


