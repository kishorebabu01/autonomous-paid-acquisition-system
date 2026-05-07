# test_connection.py
# Purpose: Verify Python can connect to Supabase successfully

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Step 1 — Load your .env file
# This reads SUPABASE_URL and SUPABASE_KEY from your .env file
load_dotenv()

# Step 2 — Get the values from .env
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Step 3 — Check they loaded correctly
print("URL found:", url is not None)
print("KEY found:", key is not None)

# Step 4 — Create the Supabase client
# This is like picking up the phone to call Supabase
supabase: Client = create_client(url, key)

# Step 5 — Test by fetching from raw_campaigns table
# Table is empty but if no error = connection works!
response = supabase.table("raw_campaigns").select("*").limit(1).execute()

print("✅ Supabase connection successful!")
print("Tables accessible. Response:", response)