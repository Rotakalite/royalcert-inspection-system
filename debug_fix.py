#!/usr/bin/env python3
"""
Debug the data fix endpoint issue
"""

import requests
import json

# Configuration
BACKEND_URL = "https://eba81ca4-6566-454a-8283-f31f83336333.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def authenticate():
    """Authenticate with admin credentials"""
    print("🔐 Authenticating...")
    
    login_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    session = requests.Session()
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        session.headers.update({
            "Authorization": f"Bearer {token}"
        })
        print("✅ Authentication successful")
        return session
    else:
        print(f"❌ Authentication failed: {response.text}")
        return None

def debug_data_fix():
    """Debug the data fix endpoint"""
    session = authenticate()
    if not session:
        return
    
    print("\n🔍 Getting users with role 'denetci'...")
    response = session.get(f"{BACKEND_URL}/users")
    if response.status_code == 200:
        users = response.json()
        inspectors = [u for u in users if u.get('role') == 'denetci' and u.get('is_active', True)]
        print(f"Found {len(inspectors)} inspectors:")
        for insp in inspectors:
            print(f"  - {insp['full_name']} (ID: {insp['id']})")
    
    print("\n🔍 Getting beklemede inspections...")
    response = session.get(f"{BACKEND_URL}/inspections")
    if response.status_code == 200:
        inspections = response.json()
        beklemede = [i for i in inspections if i.get('status') == 'beklemede']
        print(f"Found {len(beklemede)} beklemede inspections:")
        for insp in beklemede:
            print(f"  - {insp['id'][:8]}... Inspector: {insp.get('inspector_id', 'None')[:8] if insp.get('inspector_id') else 'None'}...")
    
    print("\n🔧 Running data fix endpoint...")
    response = session.post(f"{BACKEND_URL}/fix/orphaned-inspector-ids")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Result: {json.dumps(result, indent=2)}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    debug_data_fix()