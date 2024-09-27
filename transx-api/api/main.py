from fastapi import FastAPI, UploadFile, File
from boto3 import client
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from fastapi.responses import RedirectResponse
from app.auth import verify_token
from app.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME
app = FastAPI()

load_dotenv()


origins = [
    "http://localhost:5173",
    "http://localhost:8000",
    
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

s3 = client('s3')

@app.get("/auth/callback")  
async def auth_callback(token: str):
    """
    Callback do Cognito após o login do Google.
    """
    payload = await verify_token(token)
    # Aqui você pode salvar a sessão do usuário no banco ou retornar um token JWT próprio
    return {"message": "Login realizado com sucesso", "user": payload}

@app.get("/profile")
async def get_profile(token: str = Depends(verify_token)):
    """
    Rota protegida que requer um token JWT válido.
    """
    return {"message": "Perfil do usuário", "user": token}


# ================================================================================


@app.get("/")
async def main_route():
    return {"message": "Hello World"}


@app.get("/presigned_url")
def get_presigned_url():
    response = s3.generate_presigned_post(
                Bucket=BUCKET_NAME,
                Key="file.txt",
                Conditions=None,
                ExpiresIn=3600
            )
    meta
    
    return {"url": response["url"], "fields": response["fields"]}


@app.get("/getallfiles")
async def hello():
    # ERROR botocore.exceptions.ClientError: An error occurred (AccessDenied) when calling the ListObjectsV2 operation: User: arn:aws:iam::971422705337:user/transx-tester is not authorized to perform: s3:ListBucket on resource: "arn:aws:s3:::transxtestweb" because no identity-based policy allows the s3:ListBucket action
    res = s3.list_objects_v2(Bucket=BUCKET_NAME)
    print(res)
    return res

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if file:
        print(file.filename)
        s3.upload_fileobj(file.file, BUCKET_NAME, file.filename)
        return "file uploaded"
    else:
        return "error in uploading."
    # poetry run uvicorn api:app --host 0.0.0.0 --port 8000 --reload