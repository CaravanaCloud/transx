# app/config.py
import os

COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "your_user_pool_id")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID", "your_client_id")
COGNITO_REGION = os.getenv("COGNITO_REGION", "your_region")
COGNITO_JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")