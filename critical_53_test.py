#!/usr/bin/env python3
"""
CRITICAL TEST: 53/53 KONTROL KRİTERİ YAKALAMA TESTİ
Tests if the parsing algorithm captures exactly 53 control criteria, not 47!
"""

import requests
import json

# Configuration
BACKEND_URL = "https://royalcert-inspection-system-production.up.railway.app/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Test document URL
FORKLIFT_DOC_URL = "https://customer-assets.emergentagent.com/job_periodic-check/artifacts/y9b9lejo_RC-M-%C4%B0E-FR24_5%20FORKL%C4%B0FT%20MUAYENE%20FORMU.docx"

def test_53_criteria_capture():
    """Test if exactly 53 control criteria are captured"""
    print("🚨 CRITICAL TEST: 53/53 KONTROL KRİTERİ YAKALAMA")
    print("=" * 80)
    
    session = requests.Session()
    
    # Step 1: Authenticate
    print("🔐 Authenticating...")
    login_data = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    
    try:
        response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Authentication failed: {response.text}")
            return False, 0
        
        data = response.json()
        token = data["access_token"]
        session.headers.update({"Authorization": f"Bearer {token}"})
        print("✅ Authentication successful")
        
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return False, 0
    
    # Step 2: Clean existing templates
    print("\n🧹 Cleaning existing FORKLIFT templates...")
    try:
        templates_response = session.get(f"{BACKEND_URL}/equipment-templates")
        if templates_response.status_code == 200:
            templates = templates_response.json()
            forklift_templates = [t for t in templates if t.get('equipment_type') == 'FORKLIFT']
            
            for template in forklift_templates:
                delete_response = session.delete(f"{BACKEND_URL}/equipment-templates/{template['id']}")
                if delete_response.status_code == 200:
                    print(f"✅ Deleted template: {template.get('name', 'UNNAMED')}")
    except Exception as e:
        print(f"⚠️  Template cleanup error: {str(e)}")
    
    # Step 3: Download and upload test document
    print("\n📥 Downloading test document...")
    try:
        doc_response = requests.get(FORKLIFT_DOC_URL)
        if doc_response.status_code != 200:
            print(f"❌ Failed to download document: {doc_response.status_code}")
            return False, 0
        
        print(f"✅ Document downloaded ({len(doc_response.content)} bytes)")
        
    except Exception as e:
        print(f"❌ Download error: {str(e)}")
        return False, 0
    
    # Step 4: Upload document for parsing
    print("\n📤 Uploading document for parsing...")
    try:
        files = {
            'file': ('FORKLIFT MUAYENE FORMU.docx', doc_response.content, 
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        upload_response = session.post(f"{BACKEND_URL}/equipment-templates/upload", files=files)
        print(f"Upload Response Status: {upload_response.status_code}")
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            print("✅ Document uploaded and parsed successfully")
            
            # Extract results
            template_info = upload_data.get('template', {})
            total_items = template_info.get('total_items', 0)
            
            print(f"\n📊 PARSING RESULTS:")
            print(f"   Equipment Type: {template_info.get('equipment_type', 'UNKNOWN')}")
            print(f"   Template Type: {template_info.get('template_type', 'UNKNOWN')}")
            print(f"   Template Name: {template_info.get('name', 'UNNAMED')}")
            print(f"   🎯 TOTAL CONTROL ITEMS: {total_items}")
            
            # CRITICAL CHECK: Must be exactly 53!
            if total_items == 53:
                print(f"\n🎉 ✅ SUCCESS: EXACTLY 53 control criteria captured!")
                print(f"✅ EVET - %100 doğruluk sağlandı!")
                return True, 53
            elif total_items == 47:
                print(f"\n❌ FAILURE: Still capturing 47 items instead of 53!")
                print(f"❌ HAYIR - Parsing algorithm fix NOT working!")
                return False, 47
            else:
                print(f"\n⚠️  PARTIAL: {total_items} items captured (expected: 53)")
                print(f"⚠️  Algorithm needs adjustment")
                return False, total_items
                
        else:
            print(f"❌ Upload failed: {upload_response.text}")
            return False, 0
            
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return False, 0

if __name__ == "__main__":
    success, count = test_53_criteria_capture()
    
    print("\n" + "=" * 80)
    print("🎯 FINAL ANSWER TO USER QUESTION:")
    print("=" * 80)
    
    if success and count == 53:
        print("✅ EVET - 53/53 kontrol kriteri yakalanıyor!")
        print("   • Parsing algoritması düzeltmesi çalışıyor")
        print("   • %100 doğruluk sağlandı")
    else:
        print("❌ HAYIR - 53/53 kontrol kriteri yakalanmıyor!")
        print(f"   • Sadece {count} kontrol kriteri yakalandı")
        print("   • Parsing algoritması düzeltmesi uygulanmamış")
        print("   • %100 doğruluk sağlanamadı")
    
    print("=" * 80)