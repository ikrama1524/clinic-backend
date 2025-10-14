#!/usr/bin/env python3
"""
Standalone runner for the clinic management backend.
This script can be run directly without any package structure concerns.
"""

import uvicorn
import sys
import os

# Add current directory and parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

if __name__ == "__main__":
    print("Starting Clinic Management Backend...")
    print("API will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")

    # Set up environment
    os.environ.setdefault(
        'DATABASE_URL',
        'postgresql://neondb_owner:npg_hILOi9m1ARzv@ep-cool-darkness-a15byxd1-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    )

    try:
        uvicorn.run("main:app",
                    host="0.0.0.0",
                    port=8000,
                    reload=True,
                    access_log=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
