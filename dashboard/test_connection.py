"""
Test script to verify .env file and Snowflake credentials
"""
import os
from pathlib import Path
from dotenv import load_dotenv

print("="*60)
print("🔍 ENVIRONMENT VERIFICATION")
print("="*60)

# Find .env file
dashboard_dir = Path(__file__).parent
project_root = dashboard_dir.parent
env_path = project_root / 'ml_pipeline' / '.env'

print(f"\n📂 Dashboard directory: {dashboard_dir}")
print(f"📂 Project root: {project_root}")
print(f"📄 .env file path: {env_path}")
print(f"✅ .env file exists: {env_path.exists()}")

if not env_path.exists():
    print("\n❌ ERROR: .env file not found!")
    print(f"Expected location: {env_path}")
    print("\nPlease create a .env file with your Snowflake credentials.")
    exit(1)

# Load .env file
print("\n🔄 Loading .env file...")
load_dotenv(dotenv_path=env_path)

# Check each required variable
required_vars = [
    'SNOWFLAKE_USER',
    'SNOWFLAKE_PASSWORD',
    'SNOWFLAKE_ACCOUNT',
    'SNOWFLAKE_WAREHOUSE',
    'SNOWFLAKE_DATABASE',
    'SNOWFLAKE_SCHEMA',
    'SNOWFLAKE_ROLE'
]

print("\n📋 Checking environment variables:")
print("-" * 60)

all_found = True
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Mask password
        if 'PASSWORD' in var:
            display_value = '*' * len(value)
        else:
            display_value = value
        print(f"✅ {var:<25} = {display_value}")
    else:
        print(f"❌ {var:<25} = NOT FOUND")
        all_found = False

print("-" * 60)

if all_found:
    print("\n✅ All credentials found!")
    print("\nTrying to connect to Snowflake...")
    
    try:
        import snowflake.connector
        
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA', 'gold'),
            role=os.getenv('SNOWFLAKE_ROLE')
        )
        
        print("✅ Successfully connected to Snowflake!")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_ROLE()")
        result = cursor.fetchone()
        
        print(f"\n📊 Current context:")
        print(f"   Database: {result[0]}")
        print(f"   Schema: {result[1]}")
        print(f"   Role: {result[2]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Connection test successful!")
        print("You can now run: streamlit run app.py")
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nPlease check:")
        print("  1. Your credentials are correct")
        print("  2. Your Snowflake warehouse is running")
        print("  3. Your account has access to the database/schema")
else:
    print("\n❌ Missing required environment variables!")
    print("\nPlease add them to your .env file:")
    print(f"{env_path}")

print("\n" + "="*60)
