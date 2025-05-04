#!/usr/bin/env python3
"""
Utility script to generate secure random secrets for production use.
Run this script to generate secure values for your .env file.
"""

import secrets
import sys

def generate_secret(length=32):
    """Generate a secure random secret."""
    return secrets.token_urlsafe(length)

def main():
    print("=" * 60)
    print("🔐 Secure Secret Generator for MasterSpeak AI")
    print("=" * 60)
    print("\nGenerated secure secrets for your .env file:\n")
    
    print(f"SECRET_KEY={generate_secret(32)}")
    print(f"RESET_SECRET={generate_secret(32)}")
    print(f"VERIFICATION_SECRET={generate_secret(32)}")
    
    print("\n" + "=" * 60)
    print("⚠️  IMPORTANT SECURITY NOTES:")
    print("=" * 60)
    print("1. Never commit these secrets to version control")
    print("2. Use different secrets for each environment")
    print("3. Store production secrets in a secure vault")
    print("4. Rotate secrets regularly")
    print("5. Never share secrets in logs or error messages")
    print("\n✅ Copy the above values to your .env file (not .env.example)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())