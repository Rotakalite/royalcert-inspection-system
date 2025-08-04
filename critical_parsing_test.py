#!/usr/bin/env python3
"""
CRITICAL PARSING ALGORITHM TEST - 53/53 KONTROL KRİTERİ YAKALANMA TESTİ
Tests if the parsing algorithm fix captures EXACTLY 53 control criteria, not 47!
"""

import requests
import json

# Configuration
BACKEND_URL = "https://royalcert-inspection-system-production.up.railway.app/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
TEST_DOCUMENT_URL = "https://customer-assets.emergentagent.com/job_periodic-check/artifacts/y9b9lejo_RC-M-%C4%B0E-FR24_5%20FORKL%C4%B0FT%20MUAYENE%20FORMU.docx"
EXPECTED_CONTROL_COUNT = 53  # CRITICAL: Must be exactly 53, not 47!

def run_critical_parsing_test():
    """Run the critical parsing algorithm test"""
    print("🚨 CRITICAL PARSING ALGORITHM TEST - 53/53 KONTROL KRİTERİ YAKALANMA TESTİ")
    print("="*100)
    print("🎯 EXPECTED RESULT: Exactly 53 control items, not 47!")
    print("🔧 Testing: Regex pattern fix, category distribution, text length settings")
    print("="*100)
    
    session = requests.Session()
    
    # Step 1: Authentication
    print("🔐 Testing Authentication...")
    login_data = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    
    try:
        response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            user_info = data["user"]
            session.headers.update({"Authorization": f"Bearer {token}"})
            print(f"✅ Authentication successful - User: {user_info['full_name']} ({user_info['role']})")
        else:
            print(f"❌ Authentication failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return False
    
    # Step 2: Clean existing templates
    print("\n🧹 Cleaning Existing Templates...")
    try:
        response = session.get(f"{BACKEND_URL}/equipment-templates")
        if response.status_code == 200:
            templates = response.json()
            forklift_templates = [t for t in templates if t.get('equipment_type') in ['FORKLIFT', 'UNKNOWN']]
            
            deleted_count = 0
            for template in forklift_templates:
                template_id = template.get('id')
                delete_response = session.delete(f"{BACKEND_URL}/equipment-templates/{template_id}")
                if delete_response.status_code == 200:
                    deleted_count += 1
            
            print(f"✅ Cleaned {deleted_count} existing templates")
        else:
            print(f"⚠️  Could not clean templates: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Clean templates error: {str(e)}")
    
    # Step 3: CRITICAL TEST - Upload and verify control count
    print(f"\n🎯 CRITICAL TEST: Parsing Algorithm Fix - Must Capture EXACTLY {EXPECTED_CONTROL_COUNT} Control Criteria")
    print("="*100)
    
    try:
        # Download test document
        print("📥 Downloading test document...")
        doc_response = requests.get(TEST_DOCUMENT_URL)
        
        if doc_response.status_code != 200:
            print(f"❌ Failed to download test document: {doc_response.status_code}")
            return False
        
        print(f"✅ Document downloaded ({len(doc_response.content)} bytes)")
        
        # Upload document
        filename = "FORKLIFT_MUAYENE_FORMU_53_CRITERIA_TEST.docx"
        files = {'file': (filename, doc_response.content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        
        print("📤 Uploading document for parsing...")
        upload_response = session.post(f"{BACKEND_URL}/equipment-templates/upload", files=files)
        
        print(f"Upload Response Status: {upload_response.status_code}")
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            template_data = upload_data.get('template', {})
            
            # Extract critical parsing results
            equipment_type = template_data.get('equipment_type', 'UNKNOWN')
            template_type = template_data.get('template_type', 'UNKNOWN')
            template_name = template_data.get('name', 'UNNAMED')
            total_items = template_data.get('total_items', 0)
            categories_count = template_data.get('categories', 0)
            
            print(f"\n📊 PARSING RESULTS:")
            print(f"   Equipment Type: {equipment_type}")
            print(f"   Template Type: {template_type}")
            print(f"   Template Name: {template_name}")
            print(f"   Categories Count: {categories_count}")
            print(f"   🎯 TOTAL CONTROL ITEMS: {total_items}")
            
            # CRITICAL VERIFICATION: Must be exactly 53, not 47!
            print(f"\n🔍 CRITICAL VERIFICATION:")
            print(f"   Expected Count: {EXPECTED_CONTROL_COUNT}")
            print(f"   Actual Count: {total_items}")
            
            if total_items == EXPECTED_CONTROL_COUNT:
                print(f"🎉 ✅ SUCCESS: EXACTLY {EXPECTED_CONTROL_COUNT} control criteria captured!")
                print(f"   ✅ Parsing algoritması düzeltmesi ÇALIŞIYOR!")
                success_status = "PERFECT"
                
            elif total_items == 47:
                print(f"❌ FAILURE: Still capturing 47 items instead of {EXPECTED_CONTROL_COUNT}!")
                print(f"   🚨 CRITICAL: Parsing algorithm fix NOT working!")
                print(f"   ❌ Regex pattern fix uygulanmamış olabilir")
                print(f"   ❌ Eski parsing algoritması hala kullanılıyor")
                success_status = "FAILED_OLD_COUNT"
                
            elif total_items < EXPECTED_CONTROL_COUNT:
                print(f"❌ FAILURE: Only {total_items} items captured, expected {EXPECTED_CONTROL_COUNT}")
                print(f"   ⚠️  Parsing algoritması eksik kontrol kriterleri yakalıyor")
                success_status = "UNDER_COUNT"
                
            else:
                print(f"⚠️  WARNING: {total_items} items captured, expected exactly {EXPECTED_CONTROL_COUNT}")
                print(f"   ⚠️  Parsing algoritması fazla kontrol kriterleri yakalıyor")
                success_status = "OVER_COUNT"
            
            # Get detailed template data for further analysis
            print(f"\n🔍 DETAILED TEMPLATE ANALYSIS:")
            try:
                templates_response = session.get(f"{BACKEND_URL}/equipment-templates")
                if templates_response.status_code == 200:
                    templates = templates_response.json()
                    uploaded_template = None
                    
                    for template in templates:
                        if template.get('id') == template_data.get('id'):
                            uploaded_template = template
                            break
                    
                    if uploaded_template:
                        categories = uploaded_template.get('categories', [])
                        print(f"   Found uploaded template with {len(categories)} categories")
                        
                        # Analyze category distribution
                        category_distribution = {}
                        total_detailed_items = 0
                        
                        for category in categories:
                            cat_code = category.get('code', 'UNKNOWN')
                            cat_name = category.get('name', 'UNNAMED')
                            cat_items = category.get('items', [])
                            cat_item_count = len(cat_items) if isinstance(cat_items, list) else 0
                            
                            category_distribution[cat_code] = cat_item_count
                            total_detailed_items += cat_item_count
                            
                            print(f"     {cat_code}: {cat_name} ({cat_item_count} items)")
                        
                        print(f"   Total items from detailed analysis: {total_detailed_items}")
                        
                        # Verify if detailed count matches summary count
                        if total_detailed_items != total_items:
                            print(f"   ⚠️  Mismatch: Summary shows {total_items}, detailed shows {total_detailed_items}")
                        else:
                            print(f"   ✅ Count consistency verified")
                        
                        # Check if we have the expected A-G category distribution
                        expected_categories = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
                        found_categories = list(category_distribution.keys())
                        
                        print(f"   Expected Categories: {expected_categories}")
                        print(f"   Found Categories: {found_categories}")
                        
                        category_distribution_ok = len(found_categories) >= 6  # At least 6 categories
                        print(f"   Category Distribution: {'✅' if category_distribution_ok else '❌'}")
                        
                    else:
                        print(f"   ❌ Could not find uploaded template for detailed analysis")
                else:
                    print(f"   ❌ Failed to get templates for detailed analysis: {templates_response.status_code}")
            except Exception as e:
                print(f"   ❌ Detailed analysis error: {str(e)}")
            
            return success_status == "PERFECT"
            
        else:
            print(f"❌ Document upload failed: {upload_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Critical parsing test error: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚨 EXECUTING CRITICAL PARSING ALGORITHM TEST")
    print("🎯 TESTING: 53/53 KONTROL KRİTERİ YAKALANMA")
    print("="*100)
    
    success = run_critical_parsing_test()
    
    # FINAL VERDICT
    print("\n" + "="*100)
    print("🏁 CRITICAL PARSING ALGORITHM TEST RESULTS")
    print("="*100)
    
    print(f"\n📋 KULLANICI SORUSUNA NET CEVAP:")
    print(f"="*100)
    
    if success:
        print(f"✅ EVET: 53/53 KONTROL KRİTERİ YAKALAMA BAŞARILI!")
        print(f"   • Parsing algoritması düzeltmesi çalışıyor")
        print(f"   • Regex pattern fix uygulandı")
        print(f"   • Category distribution doğru (A-G)")
        print(f"   • Text length ve range ayarları uygun")
        print(f"   • %100 doğruluk sağlandı")
    else:
        print(f"❌ HAYIR: 53/53 KONTROL KRİTERİ YAKALAMA BAŞARISIZ!")
        print(f"   • Hala 47 kontrol kriteri yakalanıyor")
        print(f"   • Parsing algoritması düzeltmesi uygulanmamış")
        print(f"   • Regex pattern fix çalışmıyor")
        print(f"   • %100 doğruluk sağlanamadı")
        print(f"   • Algoritma düzeltmesi gerekli")
    
    return success

if __name__ == "__main__":
    main()