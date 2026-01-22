
from supabase import create_client
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

def check_jwt_secret():
    if not SUPABASE_JWT_SECRET:
        print("WARNING: SUPABASE_JWT_SECRET is missing in .env")
        return

    if SUPABASE_JWT_SECRET.startswith("eyJ"):
        print("\nCRITICAL WARNING: SUPABASE_JWT_SECRET seems to be a JWT Token (starts with 'eyJ').")
        print("It MUST be the raw JWT SECRET string from Supabase Dashboard > Settings > API.")
        print("Current value causes 'alg value is not allowed' or validation errors.")
    else:
        print("SUPABASE_JWT_SECRET format looks correct (not a JWT token).")
        
        print(f"DEBUG: SUPABASE_KEY starts with: {SUPABASE_KEY[:10] if SUPABASE_KEY else 'None'}")

        # Verify if the Secret can decode the Anon Key
        if SUPABASE_KEY and SUPABASE_KEY.strip('"').strip("'").startswith("eyJ"):
            clean_key = SUPABASE_KEY.strip('"').strip("'")
            print("Verifying SUPABASE_JWT_SECRET against SUPABASE_KEY (Anon Token)...")
            try:
                from jose import jwt
                jwt.decode(clean_key, SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="anon")
                print("SUCCESS: SUPABASE_JWT_SECRET is valid and matches the SUPABASE_KEY project!")
            except Exception as e:
                print(f"FAILURE: SUPABASE_JWT_SECRET could not verify SUPABASE_KEY. Mismatch? Error: {e}")
                print("Double check that you copied the 'JWT Secret' from the same Supabase project as the Anon Key.")

def test_upload_permission():
    print(f"Connecting to {SUPABASE_URL}...")
    # Initialize client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Try to upload a dummy file to 'resumes'
    # We'll use a random path to avoid conflicts
    import uuid
    dummy_path = f"test_check_{uuid.uuid4()}.pdf"
    dummy_content = b"%PDF-1.4 empty pdf"
    
    print(f"Attempting upload to 'resumes/{dummy_path}' using configured KEY...")
    
    try:
        res = supabase.storage.from_("resumes").upload(
            path=dummy_path,
            file=dummy_content,
            file_options={"content-type": "application/pdf"}
        )
        print("SUCCESS: Upload accepted! The KEY has write permissions.")
        
        # Cleanup
        supabase.storage.from_("resumes").remove([dummy_path])
        print("Cleanup successful.")
        
    except Exception as e:
        print(f"FAILURE: Upload failed. Error: {e}")
        print("\nDIAGNOSIS:")
        if "policy" in str(e).lower() or "permission" in str(e).lower() or "403" in str(e) or "new row violates" in str(e):
            print("The configured SUPABASE_KEY does not have permission to upload.")
            print("It is likely an ANON/PUBLIC key, but the bucket requires AUTHENTICATION.")
            print("SOLUTION: You need to use the SERVICE_ROLE_KEY in backend/.env for 'SUPABASE_KEY'.")
        else:
            print("Unknown error. Check network or bucket existence.")

if __name__ == "__main__":
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: SUPABASE_URL or SUPABASE_KEY not found in environment.")
    else:
        check_jwt_secret()
        test_upload_permission()
