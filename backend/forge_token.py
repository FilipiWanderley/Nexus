import jwt
import time
import uuid

# Configuration from your .env
SUPABASE_JWT_SECRET = "sb_secret_OfodgUNs4kQpdSucLRM2Zw_Ir4cj6yE"

def forge_token():
    user_id = str(uuid.uuid4())
    now = int(time.time())
    
    payload = {
        "aud": "authenticated",
        "exp": now + (24 * 3600), # 24 hours
        "iat": now,
        "iss": "supabase",
        "sub": user_id,
        "email": "demo@nexus.com",
        "phone": "",
        "app_metadata": {
            "provider": "email",
            "providers": ["email"]
        },
        "user_metadata": {
            "full_name": "Demo User"
        },
        "role": "authenticated",
        "aal": "aal1",
        "amr": [
            {
                "method": "password",
                "timestamp": now
            }
        ],
        "session_id": str(uuid.uuid4())
    }
    
    token = jwt.encode(payload, SUPABASE_JWT_SECRET, algorithm="HS256")
    return token, user_id

if __name__ == "__main__":
    token, uid = forge_token()
    print(f"ACCESS_TOKEN={token}")
    print(f"USER_ID={uid}")
