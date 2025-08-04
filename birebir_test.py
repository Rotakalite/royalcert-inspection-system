#!/usr/bin/env python3
"""
BİREBİR KOPYALA TEST - 49/49 kontrol kriteri yakalanıyor mu?
CRITICAL TEST for the user's specific question about capturing exactly 49 control criteria
"""

import requests
import json

# Configuration
BACKEND_URL = "https://royalcert-inspection-system-production.up.railway.app/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# FORKLIFT MUAYENE FORMU URL
FORKLIFT_DOC_URL = "https://customer-assets.emergentagent.com/job_periodic-check/artifacts/y9b9lejo_RC-M-%C4%B0E-FR24_5%20FORKL%C4%B0FT%20MUAYENE%20FORMU.docx"

class BirebirkopyalaTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        print("🔐 Authenticating...")
        
        login_data = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                
                print(f"✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def clean_forklift_templates(self):
        """Clean existing FORKLIFT templates"""
        print("🧹 Cleaning existing FORKLIFT templates...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/equipment-templates")
            if response.status_code == 200:
                templates = response.json()
                forklift_templates = [t for t in templates if t.get('equipment_type') == 'FORKLIFT']
                
                for template in forklift_templates:
                    template_id = template.get('id')
                    delete_response = self.session.delete(f"{BACKEND_URL}/equipment-templates/{template_id}")
                    if delete_response.status_code == 200:
                        print(f"✅ Deleted: {template.get('name', 'Unknown')}")
                
                print(f"✅ Cleaned {len(forklift_templates)} FORKLIFT templates")
                return True
            else:
                print(f"❌ Failed to get templates: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Clean templates error: {str(e)}")
            return False

    def test_birebir_kopyala(self):
        """Test BİREBİR KOPYALA algorithm with FORKLIFT MUAYENE FORMU"""
        print("\n🎯 TESTING BİREBİR KOPYALA ALGORITHM")
        print("=" * 80)
        print("SORU: 49/49 kontrol kriteri yakalanıyor mu?")
        print("BEKLENEN: Tam olarak 49 kontrol kriteri (17, 20, 21, 50 eksik)")
        print("=" * 80)
        
        try:
            # Download document
            print("📥 Downloading FORKLIFT MUAYENE FORMU...")
            doc_response = requests.get(FORKLIFT_DOC_URL)
            
            if doc_response.status_code != 200:
                print(f"❌ Download failed: {doc_response.status_code}")
                return False
            
            print(f"✅ Downloaded ({len(doc_response.content)} bytes)")
            
            # Upload document
            print("📤 Uploading to POST /api/equipment-templates/upload...")
            files = {
                'file': ('FORKLIFT MUAYENE FORMU.docx', doc_response.content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            upload_response = self.session.post(f"{BACKEND_URL}/equipment-templates/upload", files=files)
            
            if upload_response.status_code != 200:
                print(f"❌ Upload failed: {upload_response.text}")
                return False
            
            print("✅ Upload successful")
            
            # Parse results
            upload_data = upload_response.json()
            template_data = upload_data.get('template', {})
            
            equipment_type = template_data.get('equipment_type', 'UNKNOWN')
            template_type = template_data.get('template_type', 'UNKNOWN')
            categories = template_data.get('categories', [])
            
            # Count total items
            total_items = sum(len(cat.get('items', [])) for cat in categories)
            
            print(f"\n📊 PARSING RESULTS:")
            print(f"   Equipment Type: {equipment_type}")
            print(f"   Template Type: {template_type}")
            print(f"   Total Categories: {len(categories)}")
            print(f"   Total Control Items: {total_items}")
            
            # Category breakdown
            print(f"\n📋 Category Distribution:")
            for cat in categories:
                cat_code = cat.get('code', '?')
                cat_items = len(cat.get('items', []))
                print(f"   {cat_code}: {cat_items} items")
            
            # Collect all items for analysis
            all_items = []
            for cat in categories:
                for item in cat.get('items', []):
                    all_items.append({
                        'id': item.get('id'),
                        'text': item.get('text'),
                        'category': cat.get('code')
                    })
            
            # Sort by ID
            all_items.sort(key=lambda x: x.get('id', 0))
            
            # Show first 10 items
            print(f"\n📝 First 10 Control Items:")
            for i, item in enumerate(all_items[:10], 1):
                item_id = item.get('id', 'N/A')
                category = item.get('category', 'N/A')
                text = item.get('text', 'N/A')[:60]
                print(f"   {i:2d}. ID:{item_id:3d} [{category}] {text}...")
            
            # CRITICAL TEST: Check if exactly 49 items
            print(f"\n🔥 CRITICAL TEST RESULTS:")
            print(f"   Expected: 49 control criteria")
            print(f"   Actual: {total_items} control criteria")
            
            if total_items == 49:
                print(f"   ✅ SUCCESS: Exactly 49/49 control criteria captured!")
                result = "EVET"
            else:
                print(f"   ❌ FAILURE: {total_items}/49 control criteria captured!")
                result = "HAYIR"
            
            # Check for expected missing items (17, 20, 21, 50)
            print(f"\n🔍 Missing Items Check (17, 20, 21, 50 should be missing):")
            item_ids = [item['id'] for item in all_items if item['id']]
            expected_missing = [17, 20, 21, 50]
            
            correctly_missing = 0
            incorrectly_found = 0
            
            for missing_id in expected_missing:
                if missing_id not in item_ids:
                    print(f"   ✅ Item {missing_id}: Correctly missing")
                    correctly_missing += 1
                else:
                    print(f"   ❌ Item {missing_id}: Found (should be missing!)")
                    incorrectly_found += 1
            
            # Final assessment
            perfect_result = (total_items == 49 and correctly_missing == 4 and incorrectly_found == 0)
            
            print(f"\n" + "=" * 80)
            print(f"🎯 FINAL ASSESSMENT:")
            print(f"   Total items correct (49): {'✅' if total_items == 49 else '❌'}")
            print(f"   Missing items correct: {'✅' if correctly_missing == 4 else '❌'} ({correctly_missing}/4)")
            print(f"   No incorrect items: {'✅' if incorrectly_found == 0 else '❌'}")
            print(f"   Overall success: {'✅' if perfect_result else '❌'}")
            
            print(f"\n🔥 KESİN CEVAP:")
            if perfect_result:
                print(f"   ✅ EVET - 49/49 BİREBİR YAKALANIYOR!")
                print(f"   ✅ BİREBİR KOPYALA algoritması çalışıyor!")
                print(f"   ✅ Eksik itemler (17,20,21,50) doğru filtrelendi!")
            else:
                print(f"   ❌ HAYIR - 49/49 BİREBİR YAKALANMIYOR!")
                print(f"   ❌ BİREBİR KOPYALA algoritması düzeltilmeli!")
                if total_items != 49:
                    print(f"   ❌ Yanlış item sayısı: {total_items} (beklenen: 49)")
                if incorrectly_found > 0:
                    print(f"   ❌ Yanlış itemler bulundu: {incorrectly_found}")
            
            print("=" * 80)
            
            return perfect_result
            
        except Exception as e:
            print(f"❌ Test error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def run_test(self):
        """Run the complete BİREBİR KOPYALA test"""
        print("🚀 BİREBİR KOPYALA TEST - 49/49 KONTROL KRİTERİ")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Step 2: Clean existing templates
        if not self.clean_forklift_templates():
            print("⚠️ Could not clean templates, continuing...")
        
        # Step 3: Run the critical test
        success = self.test_birebir_kopyala()
        
        print(f"\n🎯 FINAL RESULT:")
        if success:
            print(f"✅ TEST PASSED - BİREBİR KOPYALA çalışıyor!")
        else:
            print(f"❌ TEST FAILED - BİREBİR KOPYALA düzeltilmeli!")
        
        return success

if __name__ == "__main__":
    tester = BirebirkopyalaTester()
    result = tester.run_test()
    
    print(f"\n" + "=" * 80)
    print(f"KULLANICI SORUSUNA CEVAP:")
    print(f"SON TEST - BİREBİR KOPYALA: {'EVET' if result else 'HAYIR'}")
    print(f"49/49 kontrol kriteri yakalanıyor mu? {'EVET' if result else 'HAYIR'}!")
    print("=" * 80)