from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import YouTubeComment, Plan, UserPlan
import json
import pandas as pd
import csv
from io import TextIOWrapper
from datetime import datetime


def index(request):
    # 表示件数をクエリパラメータから取得（デフォルト: 30件）
    limit_options = [10, 30, 50]
    limit = int(request.GET.get('limit', 30))
    if limit not in limit_options:
        limit = 30
    
    # ページ番号を取得（デフォルト: 1ページ目）
    page_number = request.GET.get('page', 1)
    
    # グラフ用には最大300件を使用
    comments_for_graph = YouTubeComment.objects.all()[:300]
    # テーブル表示用には全件を取得してページネーション
    all_comments = YouTubeComment.objects.all().order_by('-created_at')
    
    # ページネーション
    paginator = Paginator(all_comments, limit)
    page_obj = paginator.get_page(page_number)
    comments = page_obj.object_list

    # 3Dグラフ用のデータを準備
    graph_data = None
    stats = None

    if comments_for_graph.exists():
        df = pd.DataFrame(list(comments_for_graph.values(
            "like_count",
            "reply_count",
            "created_at",
            "author",
            "comment_text",
        )))

        # タイムスタンプを数値に変換
        df["created_at_num"] = df["created_at"].astype("int64") // 10**9
        
        # グラフ用のデータをリスト形式に変換
        graph_data = {
            "x": df["like_count"].tolist(),
            "y": df["reply_count"].tolist(),
            "z": df["created_at_num"].tolist(),
            "text": [
                f"Author: {author}<br>Likes: {likes}<br>Replies: {replies}<br>Comment: {text[:50]}..."
                for author, likes, replies, text in zip(
                    df["author"], df["like_count"], df["reply_count"], df["comment_text"]
                )
            ],
            "colors": df["created_at_num"].tolist(),  # 色分け用
        }

        # 統計情報を計算
        stats = {
            "total_comments": len(df),
            "avg_likes": float(df["like_count"].mean()),
            "avg_replies": float(df["reply_count"].mean()),
            "max_likes": int(df["like_count"].max()),
            "max_replies": int(df["reply_count"].max()),
            "total_likes": int(df["like_count"].sum()),
            "total_replies": int(df["reply_count"].sum()),
        }
        
        # 分析結果とアドバイスを生成（有料プラン・無料プラン両方で生成）
        analysis = None
        advice = None
        
        # 有料プランチェック
        is_premium = False
        if request.user.is_authenticated:
            try:
                user_plan = UserPlan.objects.get(user=request.user, is_active=True)
                is_premium = user_plan.is_premium
            except UserPlan.DoesNotExist:
                pass
        
        if len(df) > 0:
            # 分析結果を生成
            high_engagement = df[(df["like_count"] > stats["avg_likes"]) & (df["reply_count"] > stats["avg_replies"])]
            low_engagement = df[(df["like_count"] < stats["avg_likes"]) & (df["reply_count"] < stats["avg_replies"])]
            
            engagement_ratio = len(high_engagement) / len(df) * 100 if len(df) > 0 else 0
            
            analysis = {
                "high_engagement_count": len(high_engagement),
                "low_engagement_count": len(low_engagement),
                "engagement_ratio": round(engagement_ratio, 1),
                "top_comment_likes": int(df.nlargest(1, "like_count")["like_count"].iloc[0]) if len(df) > 0 else 0,
                "top_comment_replies": int(df.nlargest(1, "reply_count")["reply_count"].iloc[0]) if len(df) > 0 else 0,
            }
            
            # アドバイスを生成
            advice_items = []
            
            if stats["avg_likes"] < 5:
                advice_items.append("平均いいね数が低い傾向にあります。コメントの内容をより具体的で価値のあるものにすることで、エンゲージメントを向上させることができます。")
            
            if stats["avg_replies"] < 2:
                advice_items.append("返信数が少ない傾向にあります。質問形式のコメントや議論を促す内容を増やすことで、コミュニティの活性化につながります。")
            
            if engagement_ratio < 20:
                advice_items.append("高エンゲージメントコメントの割合が低いです。視聴者の興味を引く話題や、タイムリーな内容を意識することで改善できます。")
            
            if len(high_engagement) > 0:
                top_comment = df.nlargest(1, "like_count").iloc[0]
                advice_items.append(f"最もエンゲージメントが高いコメントは{int(top_comment['like_count'])}いいね、{int(top_comment['reply_count'])}返信を獲得しています。このようなコメントの特徴を分析し、同様のアプローチを他のコメントにも適用することをお勧めします。")
            
            if stats["max_likes"] > stats["avg_likes"] * 3:
                advice_items.append("一部のコメントが非常に高いエンゲージメントを獲得しています。これらの成功パターンを分析し、コンテンツ戦略に反映させることで、全体的なエンゲージメント向上が期待できます。")
            
            if not advice_items:
                advice_items.append("現在のエンゲージメント状況は良好です。継続的な分析と改善により、さらなる成長が期待できます。")
            
            advice = advice_items

    return render(request, "index.html", {
        "graph_data": json.dumps(graph_data) if graph_data else None,
        "stats": stats,
        "comments": comments,
        "page_obj": page_obj,
        "current_limit": limit,
        "limit_options": limit_options,
        "is_premium": is_premium,
        "analysis": analysis,
        "advice": advice,
    })


def comments_table(request):
    """Ajax用: コメントテーブル部分のみを返す"""
    # 表示件数をクエリパラメータから取得（デフォルト: 30件）
    limit_options = [10, 30, 50]
    limit = int(request.GET.get('limit', 30))
    if limit not in limit_options:
        limit = 30
    
    # ページ番号を取得（デフォルト: 1ページ目）
    page_number = request.GET.get('page', 1)
    
    # テーブル表示用には全件を取得してページネーション
    all_comments = YouTubeComment.objects.all().order_by('-created_at')
    
    # ページネーション
    paginator = Paginator(all_comments, limit)
    page_obj = paginator.get_page(page_number)
    comments = page_obj.object_list

    from django.template.loader import render_to_string
    html = render_to_string('comments_table.html', {
        'comments': comments,
        'page_obj': page_obj,
        'current_limit': limit,
        'limit_options': limit_options,
    }, request=request)
    
    return JsonResponse({'html': html})


def import_csv(request):
    """CSVファイルをインポート"""
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = TextIOWrapper(request.FILES["csv_file"].file, encoding="utf-8")
        reader = csv.DictReader(csv_file)
        count = 0
        for row in reader:
            YouTubeComment.objects.create(
                video_id=row.get("video_id", ""),
                comment_id=row.get("comment_id", ""),
                comment_text=row.get("comment_text", ""),
                author=row.get("author", ""),
                like_count=int(row.get("like_count") or 0),
                reply_count=int(row.get("reply_count") or 0),
                reply_depth_potential=int(row.get("reply_depth_potential") or 0),
                engagement_score=float(row.get("engagement_score") or 0),
                created_at=row.get("created_at") or None,
                ai_reply=row.get("ai_reply") if row.get("ai_reply") and row.get("ai_reply") != "null" else None,
                embedding=row.get("embedding") if row.get("embedding") else None,
            )
            count += 1
        messages.success(request, f"{count} 件のコメントをインポートしました。")
        return redirect("index")
    
    messages.error(request, "CSVファイルを選択してください。")
    return redirect("index")


def import_json(request):
    """JSONファイルをインポート"""
    if request.method == "POST" and request.FILES.get("json_file"):
        json_file = request.FILES["json_file"]
        try:
            data = json.load(json_file)
            count = 0
            
            # JSONが配列の場合
            if isinstance(data, list):
                for item in data:
                    YouTubeComment.objects.create(
                        video_id=item.get("video_id", ""),
                        comment_id=item.get("comment_id", ""),
                        comment_text=item.get("comment_text", ""),
                        author=item.get("author", ""),
                        like_count=int(item.get("like_count") or 0),
                        reply_count=int(item.get("reply_count") or 0),
                        reply_depth_potential=int(item.get("reply_depth_potential") or 0),
                        engagement_score=float(item.get("engagement_score") or 0),
                        created_at=item.get("created_at") or None,
                        ai_reply=item.get("ai_reply") if item.get("ai_reply") and item.get("ai_reply") != "null" else None,
                        embedding=item.get("embedding") if item.get("embedding") else None,
                    )
                    count += 1
            # JSONがオブジェクトでcommentsキーがある場合
            elif isinstance(data, dict) and "comments" in data:
                for item in data["comments"]:
                    YouTubeComment.objects.create(
                        video_id=item.get("video_id", ""),
                        comment_id=item.get("comment_id", ""),
                        comment_text=item.get("comment_text", ""),
                        author=item.get("author", ""),
                        like_count=int(item.get("like_count") or 0),
                        reply_count=int(item.get("reply_count") or 0),
                        reply_depth_potential=int(item.get("reply_depth_potential") or 0),
                        engagement_score=float(item.get("engagement_score") or 0),
                        created_at=item.get("created_at") or None,
                        ai_reply=item.get("ai_reply") if item.get("ai_reply") and item.get("ai_reply") != "null" else None,
                        embedding=item.get("embedding") if item.get("embedding") else None,
                    )
                    count += 1
            
            messages.success(request, f"{count} 件のコメントをインポートしました。")
            return redirect("index")
        except json.JSONDecodeError:
            messages.error(request, "JSONファイルの形式が正しくありません。")
            return redirect("index")
    
    messages.error(request, "JSONファイルを選択してください。")
    return redirect("index")


def pricing(request):
    # 現在のユーザーのプラン情報を取得
    current_plan = None
    current_user_plan = None
    if request.user.is_authenticated:
        try:
            current_user_plan = UserPlan.objects.get(user=request.user, is_active=True)
            current_plan = current_user_plan.plan
        except UserPlan.DoesNotExist:
            pass
    
    # すべてのプランを取得
    plans = Plan.objects.all().order_by('price')
    
    # Stripe公開キーとProプランの価格IDをテンプレートに渡す
    from django.conf import settings
    stripe_public_key = getattr(settings, 'STRIPE_PUBLIC_KEY', '')
    stripe_pro_price_id = getattr(settings, 'STRIPE_PRO_PRICE_ID', '')
    
    return render(request, "pricing.html", {
        "current_plan": current_plan,
        "current_user_plan": current_user_plan,
        "plans": plans,
        "user": request.user,  # テンプレートでユーザーIDを使用するため
        "stripe_public_key": stripe_public_key,
        "stripe_pro_price_id": stripe_pro_price_id,
    })


def downgrade_to_free(request):
    """Proプランから無料プランへ変更"""
    if not request.user.is_authenticated:
        messages.error(request, "ログインが必要です。")
        return redirect('pricing')
    
    if request.method == "POST":
        try:
            # 現在のユーザープランを取得
            user_plan = UserPlan.objects.get(user=request.user, is_active=True)
            current_plan = user_plan.plan
            
            # 無料プランを取得
            free_plan = Plan.objects.get(name='free')
            
            # プランを無料プランに変更
            user_plan.plan = free_plan
            user_plan.is_active = True
            user_plan.save()
            
            # 完了メッセージ
            messages.success(
                request,
                "ご利用ありがとうございました。\n"
                f"{current_plan.display_name if current_plan else 'Proプラン'}のご契約は終了し、無料プランへ変更されました。\n"
                "引き続き、無料プランにてサービスをご利用いただけます。"
            )
            
            return redirect('pricing')
        except UserPlan.DoesNotExist:
            messages.error(request, "ユーザープランが見つかりません。")
            return redirect('pricing')
        except Plan.DoesNotExist:
            messages.error(request, "無料プランが見つかりません。")
            return redirect('pricing')
    
    return redirect('pricing')


# ============================================
# Stripe決済機能
# ============================================
# 必要なパッケージ: pip install stripe
# インストールコマンド: pip install stripe

def create_checkout_session(request, plan_id):
    """
    Stripe Checkoutセッションを作成して決済画面にリダイレクト
    
    必要な設定:
    - settings.STRIPE_SECRET_KEY: Stripeシークレットキー
    - settings.STRIPE_SUCCESS_URL: 決済成功後のリダイレクトURL
    - settings.STRIPE_CANCEL_URL: 決済キャンセル時のリダイレクトURL
    - Plan.stripe_price_id: Stripe価格ID
    """
    if not request.user.is_authenticated:
        from django.contrib import messages
        messages.error(request, "ログインが必要です。")
        return redirect('pricing')
    
    try:
        plan = Plan.objects.get(id=plan_id)
    except Plan.DoesNotExist:
        from django.contrib import messages
        messages.error(request, "プランが見つかりません。")
        return redirect('pricing')
    
    # 無料プランの場合は管理画面にリダイレクト
    if not plan.is_premium:
        from django.contrib import messages
        messages.info(request, "無料プランは管理画面から変更できます。")
        return redirect('admin:myapp_userplan_changelist')
    
    # Stripe価格IDを取得
    stripe_price_id = plan.stripe_price_id
    if not stripe_price_id:
        # settings.pyから取得（フォールバック）
        from django.conf import settings
        if plan.name == 'pro':
            stripe_price_id = getattr(settings, 'STRIPE_PRO_PRICE_ID', '')
    
    if not stripe_price_id:
        from django.contrib import messages
        messages.error(request, "このプランの決済設定が完了していません。管理画面から変更してください。")
        return redirect('admin:myapp_userplan_changelist')
    
    # Stripe Checkoutセッションを作成
    import stripe
    from django.conf import settings
    from django.contrib import messages
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Stripe APIキーの確認
    if not settings.STRIPE_SECRET_KEY:
        logger.error("Stripe APIキーが設定されていません")
        messages.error(request, "Stripe APIキーが設定されていません。")
        return redirect('pricing')
    
    # Stripe価格IDの確認
    if not stripe_price_id:
        logger.error(f"Stripe価格IDが取得できませんでした。plan_id: {plan_id}, plan.name: {plan.name}")
        messages.error(request, "このプランの決済設定が完了していません。")
        return redirect('pricing')
    
    logger.info(f"Stripe Checkoutセッション作成開始: plan_id={plan_id}, stripe_price_id={stripe_price_id}, user_id={request.user.id}")
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': stripe_price_id,
                'quantity': 1,
            }],
            mode='subscription',  # サブスクリプション（月額課金）
            success_url=settings.STRIPE_SUCCESS_URL + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=settings.STRIPE_CANCEL_URL,
            customer_email=request.user.email,
            metadata={
                'user_id': request.user.id,
                'plan_id': plan.id,
            },
        )
        
        logger.info(f"Stripe Checkoutセッション作成成功: session_id={checkout_session.id}, url={checkout_session.url}")
        
        # Checkout URLが正しく取得できたか確認
        if not checkout_session.url:
            logger.error("Stripe Checkout URLが取得できませんでした")
            messages.error(request, "Stripe Checkout URLの取得に失敗しました。")
            return redirect('pricing')
        
        # Stripe Checkoutページにリダイレクト
        return redirect(checkout_session.url)
    except stripe.error.StripeError as e:
        logger.error(f"Stripe APIエラー: {str(e)}")
        messages.error(request, f"決済セッションの作成に失敗しました: {str(e)}")
        return redirect('pricing')
    except Exception as e:
        logger.error(f"予期しないエラー: {str(e)}", exc_info=True)
        messages.error(request, f"予期しないエラーが発生しました: {str(e)}")
        return redirect('pricing')


def checkout_success(request):
    """
    決済成功後のコールバック処理
    Stripe Checkoutからリダイレクトされた後に実行される
    """
    session_id = request.GET.get('session_id')
    
    if not session_id:
        from django.contrib import messages
        messages.error(request, "セッションIDが見つかりません。")
        return redirect('pricing')
    
    if not request.user.is_authenticated:
        from django.contrib import messages
        messages.error(request, "ログインが必要です。")
        return redirect('pricing')
    
    import stripe
    from django.conf import settings
    from django.contrib import messages
    from datetime import datetime, timedelta
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        # Checkoutセッションを取得
        session = stripe.checkout.Session.retrieve(session_id)
        
        # メタデータからユーザーIDとプランIDを取得
        user_id = session.metadata.get('user_id')
        plan_id = session.metadata.get('plan_id')
        
        # ユーザーが一致するか確認
        if int(user_id) != request.user.id:
            messages.error(request, "ユーザーが一致しません。")
            return redirect('pricing')
        
        # プランを取得
        try:
            plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            messages.error(request, "プランが見つかりません。")
            return redirect('pricing')
        
        # ユーザープランを更新または作成
        user_plan, created = UserPlan.objects.get_or_create(
            user=request.user,
            defaults={'plan': plan, 'is_active': True}
        )
        
        if not created:
            user_plan.plan = plan
            user_plan.is_active = True
            # 有効期限を1ヶ月後に設定（サブスクリプションの場合）
            user_plan.expires_at = datetime.now() + timedelta(days=30)
            user_plan.save()
        
        messages.success(request, f"{plan.display_name}プランへの変更が完了しました。")
        return redirect('index')
        
    except stripe.error.StripeError as e:
        messages.error(request, f"決済情報の確認に失敗しました: {str(e)}")
        return redirect('pricing')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Stripe Webhookエンドポイント
    Stripeから決済完了などのイベントを受け取る
    
    必要な設定:
    - settings.STRIPE_WEBHOOK_SECRET: Webhook署名シークレット
    - StripeダッシュボードでWebhookエンドポイントを設定: https://yourdomain.com/stripe-webhook/
    - イベント: checkout.session.completed, customer.subscription.updated, customer.subscription.deleted
    """
    import stripe
    import json
    from django.conf import settings
    from django.http import HttpResponse
    from datetime import datetime, timedelta
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # イベントタイプに応じて処理
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # 決済完了時の処理
        user_id = session['metadata'].get('user_id')
        plan_id = session['metadata'].get('plan_id')
        
        # ユーザープランを更新
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)
            plan = Plan.objects.get(id=plan_id)
            
            user_plan, created = UserPlan.objects.get_or_create(
                user=user,
                defaults={'plan': plan, 'is_active': True}
            )
            
            if not created:
                user_plan.plan = plan
                user_plan.is_active = True
                user_plan.expires_at = datetime.now() + timedelta(days=30)
                user_plan.save()
        except (User.DoesNotExist, Plan.DoesNotExist):
            pass
        
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        # サブスクリプション更新時の処理
        # 必要に応じて実装
        
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        # サブスクリプション解約時の処理
        # ユーザーを無料プランに戻す
        try:
            customer_id = subscription.get('customer')
            # customer_idからuser_idを取得する処理が必要
            # 現時点では簡易実装
        except:
            pass
    
    return HttpResponse(status=200)


