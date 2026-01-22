
import asyncio
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async def check_schema():
    print("Checking 'resumes' table schema...")
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Try to insert a dummy record to force an error that reveals columns
    # Or select * limit 1 to see keys
    try:
        # Try to insert a record with just user_id (required) to see what happens
        # We use a random UUID
        import uuid
        dummy_id = str(uuid.uuid4())
        # We intentionally omit other fields to see if it complains or succeeds
        # But actually, let's just try to select an empty result set and print 'error' if it fails
        res = client.table("resumes").select("*").limit(0).execute()
        # If this works, we can't see columns easily without data.
        # Let's try to fetch metadata if possible, or just fail an insert.
        
        print("Select worked. Now trying to insert with NO filename (maybe it's not needed or different name).")
        client.table("resumes").insert({
            "user_id": dummy_id,
            "file_path": "test/path"
        }).execute()
        print("Insert with NO filename SUCCESS!")
        
    except Exception as e:
        print("Error details:", str(e))

if __name__ == "__main__":
    asyncio.run(check_schema())
