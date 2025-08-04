#!/usr/bin/env python3
"""
Simple verification test for BİREBİR KOPYALA algorithm
"""

import requests

# Configuration
BACKEND_URL = "https://royalcert-inspection-system-production.up.railway.app/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def test_birebir_kopyala():
    """Simple test to verify the current state"""
    session = requests.Session()
    
    # Authenticate
    login_data = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("❌ Authentication failed")
        return False
    
    token = response.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    # Get existing FORKLIFT templates
    response = session.get(f"{BACKEND_URL}/equipment-templates")
    if response.status_code == 200:
        templates = response.json()
        forklift_templates = [t for t in templates if t.get('equipment_type') == 'FORKLIFT']
        
        if forklift_templates:
            template = forklift_templates[0]  # Get first FORKLIFT template
            categories = template.get('categories', [])
            total_items = sum(len(cat.get('items', [])) for cat in categories)
            
            print(f"🔍 Current FORKLIFT template analysis:")
            print(f"   Template Name: {template.get('name', 'Unknown')}")
            print(f"   Template Type: {template.get('template_type', 'Unknown')}")
            print(f"   Total Control Items: {total_items}")
            
            # Category breakdown
            for cat in categories:
                cat_code = cat.get('code', '?')
                cat_items = len(cat.get('items', []))
                print(f"   {cat_code}: {cat_items} items")
            
            print(f"\n🎯 RESULT:")
            if total_items == 49:
                print(f"   ✅ EVET - 49/49 kontrol kriteri yakalandı!")
                return True
            else:
                print(f"   ❌ HAYIR - Sadece {total_items}/49 kontrol kriteri yakalandı!")
                return False
        else:
            print("❌ No FORKLIFT templates found")
            return False
    else:
        print("❌ Failed to get templates")
        return False

if __name__ == "__main__":
    print("🔍 BİREBİR KOPYALA Verification Test")
    print("=" * 50)
    
    result = test_birebir_kopyala()
    
    print(f"\n🔥 FINAL ANSWER:")
    print(f"49/49 kontrol kriteri yakalanıyor mu? {'EVET' if result else 'HAYIR'}!")