from pathlib import Path
from dotenv import load_dotenv
import os

# .envファイルを読み込む
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'dev-secret-key'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',  # ← 追加
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'myapp' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'

# SQLiteでの接続をするための情報
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# PostgreSQLでの接続をするための情報
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "comment_dashboard",
        "USER": "comment_user",
        "PASSWORD": "your_password_here",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'myapp' / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# Stripe決済設定
# ============================================
# 必要な情報：
# 1. Stripe公開可能キー（Publishable Key）
#    - Stripeダッシュボード > 開発者 > APIキー から取得
#    - 例: pk_test_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# 2. Stripeシークレットキー（Secret Key）
#    - Stripeダッシュボード > 開発者 > APIキー から取得
#    - 例: sk_test_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# 3. Stripe Webhookシークレット
#    - Stripeダッシュボード > 開発者 > Webhook でエンドポイント作成後、署名シークレットを取得
#    - 例: whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# 4. Stripe価格ID（Price ID）
#    - Stripeダッシュボード > 商品 > 価格 でProプランの価格を作成し、価格IDを取得
#    - 例: price_1xxxxxxxxxxxxxxxxxxxxxxxxx
#    - または、Planモデルにstripe_price_idフィールドを追加して管理

# Stripe APIキー（環境変数から取得）
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

# Stripe価格ID（Proプラン）
STRIPE_PRO_PRICE_ID = os.environ.get('STRIPE_PRO_PRICE_ID', '')

# 決済成功後のリダイレクトURL
STRIPE_SUCCESS_URL = 'http://127.0.0.1:8000/checkout-success/'
STRIPE_CANCEL_URL = 'http://127.0.0.1:8000/pricing/'