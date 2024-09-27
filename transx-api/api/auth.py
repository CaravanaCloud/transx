from jose import JWTError, jwt
import requests
from fastapi import HTTPException, Depends
from app.config import COGNITO_JWKS_URL, COGNITO_CLIENT_ID

async def get_cognito_public_keys():
    response = requests.get(COGNITO_JWKS_URL)
    return response.json()

async def verify_token(token: str):
    jwks = await get_cognito_public_keys()
    unverified_header = jwt.get_unverified_header(token)
    
    rsa_key = {}
    for key in jwks['keys']:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=COGNITO_CLIENT_ID
            )
            return payload
        except JWTError:
            raise HTTPException(status_code=403, detail="Token inválido.")
    raise HTTPException(status_code=403, detail="Chave pública não encontrada.")
