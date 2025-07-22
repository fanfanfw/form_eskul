#!/usr/bin/env python3
"""
Script untuk menjalankan aplikasi Form Eskul
"""

import uvicorn
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Starting Form Eskul Application...")
    print("📍 Access URL: http://localhost:8000")
    print("📊 Data Registrasi: http://localhost:8000/registrations")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Application stopped")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("💡 Make sure all dependencies are installed")
        print("📋 Run: pip install fastapi uvicorn jinja2 python-multipart psycopg2")
