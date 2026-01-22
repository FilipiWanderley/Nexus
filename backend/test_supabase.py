from supabase import create_client
import os

url = "https://xgnwaftodadidwqxmqym.supabase.co"
key = "sb_publishable_n2C73TzO3-9ZJS2cx8ji9w_ikxPdHsi"

try:
    print(f"Testing connection to {url} with key {key[:10]}...")
    supabase = create_client(url, key)
    # Try a simple request - usually 'health' or auth check
    # We can try to sign in with a fake user or just check if client initializes without error
    # Note: create_client usually doesn't throw network error immediately, we need to make a request.
    
    # Try to list buckets (usually public or fails with 401 if key is bad)
    res = supabase.storage.list_buckets()
    print("Connection successful!")
    print(res)
except Exception as e:
    print(f"Connection failed: {e}")
