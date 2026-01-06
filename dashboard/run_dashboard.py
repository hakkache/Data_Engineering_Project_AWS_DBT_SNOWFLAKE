"""
Quick start script for the analytics dashboard
"""
import subprocess
import sys
import os

def main():
    print("="*60)
    print("🚀 Starting E-Commerce Analytics Dashboard")
    print("="*60)
    
    # Check if .env file exists
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if not os.path.exists(env_path):
        print("\n⚠️  WARNING: .env file not found!")
        print("Please create a .env file with your Snowflake credentials")
        print("\nRequired variables:")
        print("  - SNOWFLAKE_USER")
        print("  - SNOWFLAKE_PASSWORD")
        print("  - SNOWFLAKE_ACCOUNT")
        print("  - SNOWFLAKE_WAREHOUSE")
        print("  - SNOWFLAKE_DATABASE")
        print("  - SNOWFLAKE_SCHEMA")
        print("  - SNOWFLAKE_ROLE")
        return
    
    print("\n✅ Environment configuration found")
    print("📊 Launching Streamlit dashboard...")
    print("\n" + "="*60)
    
    # Run streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error running dashboard: {e}")

if __name__ == "__main__":
    main()
