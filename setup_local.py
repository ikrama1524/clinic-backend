#!/usr/bin/env python3
"""
Setup script for local development
"""

import os
import subprocess
import sys


def main():
    print("Setting up Clinic Management Backend for local development...")

    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("Creating .env file...")
        with open('.env', 'w') as f:
            f.write(
                "DATABASE_URL=postgresql://neondb_owner:npg_hILOi9m1ARzv@ep-cool-darkness-a15byxd1-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require\n"
            )
        print("✓ Created .env file with SQLite database")

    # Install dependencies
    print("Installing dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False

    print("\nSetup complete! To start the backend, run:")
    print("python run_standalone.py")

    return True


if __name__ == "__main__":
    main()
