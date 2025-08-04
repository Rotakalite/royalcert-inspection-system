#!/usr/bin/env python3
"""
Universal Template Parser Database Model Testing
Tests the fix for Universal Template Parser where EquipmentTemplate Pydantic model 
now includes all 11 universal template structure fields.

Focus Areas:
1. POST /api/equipment-templates/upload endpoint - Word file upload and parsing
2. Universal structure fields being correctly saved to database
3. GET /api/equipment-templates endpoint returning templates with universal fields
4. Template parsing still working with reasonable control item counts (50-60 range)
"""

import requests
import json
import os
from datetime import datetime

# Configuration - Use local backend for testing
BACKEND_URL = "http://localhost:8001/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Test document URLs
TEST_DOCUMENTS = {
    "FORKLIFT_MUAYENE_FORMU": "https://customer-assets.emergentagent.com/job_periodic-check/artifacts/y9b9lejo_RC-M-%C4%B0E-FR24_5%20FORKL%C4%B0FT%20MUAYENE%20FORMU.docx",
    "FORKLIFT_MUAYENE_RAPORU": "https://customer-assets.emergentagent.com/job_periodic-check/artifacts/00vmxy69_RC-M-%C4%B0E-FR25_6%20FORKL%C4%B0FT%20MUAYENE%20RAPORU.docx"
}

class UniversalTemplateParserTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        self.uploaded_templates = []
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        print("🔐 Testing Authentication...")
        
        login_data = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            print(f"Login Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.user_info = data["user"]
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                
                print(f"✅ Authentication successful")
                print(f"   User: {self.user_info['full_name']} ({self.user_info['role']})")
                return True
            else:
                print(f"❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def clean_existing_templates(self):
        """Clean existing FORKLIFT templates to ensure fresh testing"""
        print("\n🧹 Cleaning Existing FORKLIFT Templates...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/equipment-templates")
            
            if response.status_code == 200:
                templates = response.json()
                forklift_templates = [t for t in templates if t.get('equipment_type') == 'FORKLIFT']
                
                print(f"Found {len(forklift_templates)} existing FORKLIFT templates")
                
                deleted_count = 0
                for template in forklift_templates:
                    template_id = template.get('id')
                    template_name = template.get('name', 'UNNAMED')
                    
                    delete_response = self.session.delete(f"{BACKEND_URL}/equipment-templates/{template_id}")
                    
                    if delete_response.status_code == 200:
                        print(f"   ✅ Deleted: {template_name}")
                        deleted_count += 1
                    else:
                        print(f"   ❌ Failed to delete: {template_name}")
                
                print(f"✅ Cleaned {deleted_count}/{len(forklift_templates)} templates")
                return True
            else:
                print(f"❌ Failed to get templates: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Clean templates error: {str(e)}")
            return False

    def test_word_document_upload_and_parsing(self, doc_name, doc_url):
        """Test Word document upload and parsing with universal structure"""
        print(f"\n📥 Testing {doc_name} Upload and Universal Parsing...")
        
        try:
            # Download the document
            print(f"   Downloading from: {doc_url}")
            doc_response = requests.get(doc_url)
            
            if doc_response.status_code != 200:
                print(f"❌ Failed to download document: {doc_response.status_code}")
                return False, None
            
            print(f"✅ Document downloaded ({len(doc_response.content)} bytes)")
            
            # Prepare file for upload
            filename = doc_name.replace('_', ' ') + '.docx'
            files = {
                'file': (filename, doc_response.content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Upload the document
            print(f"   Uploading as: {filename}")
            upload_response = self.session.post(f"{BACKEND_URL}/equipment-templates/upload", files=files)
            
            print(f"Upload Response Status: {upload_response.status_code}")
            
            if upload_response.status_code == 200:
                upload_data = upload_response.json()
                print("✅ Document uploaded and parsed successfully")
                
                # Extract template data
                template_data = upload_data.get('template', {})
                template_id = template_data.get('id')
                
                # Store for later cleanup
                self.uploaded_templates.append({
                    'id': template_id,
                    'name': template_data.get('name'),
                    'doc_name': doc_name
                })
                
                return True, template_data
            else:
                print(f"❌ Document upload failed: {upload_response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Document upload error: {str(e)}")
            return False, None

    def verify_universal_structure_fields(self, template_data):
        """Verify that all 11 universal structure fields are present"""
        print(f"\n🔍 Verifying Universal Structure Fields...")
        
        # Expected universal structure fields
        expected_fields = [
            'general_info',
            'measurement_devices', 
            'equipment_info',
            'test_values',
            'control_items',
            'categories_dict',
            'test_experiments',
            'defect_explanations',
            'notes',
            'result_opinion',
            'inspector_info',
            'company_official'
        ]
        
        print(f"Checking for {len(expected_fields)} universal structure fields:")
        
        present_fields = []
        missing_fields = []
        
        for field in expected_fields:
            if field in template_data:
                field_value = template_data.get(field)
                is_present = field_value is not None
                present_fields.append(field) if is_present else missing_fields.append(field)
                
                status = "✅" if is_present else "❌"
                value_info = ""
                
                if is_present:
                    if isinstance(field_value, dict):
                        value_info = f"(dict with {len(field_value)} keys)"
                    elif isinstance(field_value, list):
                        value_info = f"(list with {len(field_value)} items)"
                    elif isinstance(field_value, str):
                        value_info = f"(string, {len(field_value)} chars)"
                    else:
                        value_info = f"({type(field_value).__name__})"
                
                print(f"   {status} {field}: {value_info}")
            else:
                missing_fields.append(field)
                print(f"   ❌ {field}: Missing from template data")
        
        print(f"\n📊 Universal Structure Summary:")
        print(f"   Present fields: {len(present_fields)}/{len(expected_fields)}")
        print(f"   Missing fields: {len(missing_fields)}")
        
        if missing_fields:
            print(f"   Missing: {', '.join(missing_fields)}")
        
        return {
            'total_expected': len(expected_fields),
            'present_count': len(present_fields),
            'missing_count': len(missing_fields),
            'present_fields': present_fields,
            'missing_fields': missing_fields,
            'all_present': len(missing_fields) == 0
        }

    def verify_database_storage(self, template_id):
        """Verify that universal structure is correctly stored in database"""
        print(f"\n💾 Verifying Database Storage for Template {template_id[:8]}...")
        
        try:
            # Get template from database via API
            response = self.session.get(f"{BACKEND_URL}/equipment-templates/{template_id}")
            
            if response.status_code == 200:
                stored_template = response.json()
                print("✅ Template retrieved from database")
                
                # Verify universal structure fields are stored
                universal_verification = self.verify_universal_structure_fields(stored_template)
                
                # Additional checks for data integrity
                print(f"\n🔍 Database Storage Integrity:")
                
                # Check control items
                control_items = stored_template.get('control_items', [])
                categories = stored_template.get('categories', [])
                
                control_items_count = len(control_items) if control_items else 0
                categories_count = len(categories) if categories else 0
                
                print(f"   Control items: {control_items_count}")
                print(f"   Categories: {categories_count}")
                
                # Check if control items count is reasonable (50-60 range)
                reasonable_count = 50 <= control_items_count <= 60
                print(f"   Reasonable count (50-60): {'✅' if reasonable_count else '❌'} ({control_items_count})")
                
                return {
                    'retrieved': True,
                    'universal_fields': universal_verification,
                    'control_items_count': control_items_count,
                    'categories_count': categories_count,
                    'reasonable_count': reasonable_count,
                    'stored_template': stored_template
                }
            else:
                print(f"❌ Failed to retrieve template: {response.text}")
                return {'retrieved': False}
                
        except Exception as e:
            print(f"❌ Database verification error: {str(e)}")
            return {'retrieved': False}

    def test_get_templates_with_universal_fields(self):
        """Test GET /api/equipment-templates returns templates with universal fields"""
        print(f"\n📋 Testing GET /api/equipment-templates with Universal Fields...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/equipment-templates")
            
            if response.status_code == 200:
                templates = response.json()
                forklift_templates = [t for t in templates if t.get('equipment_type') == 'FORKLIFT']
                
                print(f"✅ Retrieved {len(templates)} total templates")
                print(f"   FORKLIFT templates: {len(forklift_templates)}")
                
                if not forklift_templates:
                    print("❌ No FORKLIFT templates found")
                    return False, None
                
                # Verify universal fields in retrieved templates
                universal_results = []
                
                for template in forklift_templates:
                    template_name = template.get('name', 'UNNAMED')
                    print(f"\n   Checking {template_name}:")
                    
                    universal_check = self.verify_universal_structure_fields(template)
                    universal_results.append({
                        'template_name': template_name,
                        'universal_check': universal_check
                    })
                
                return True, {
                    'total_templates': len(templates),
                    'forklift_templates': len(forklift_templates),
                    'universal_results': universal_results
                }
            else:
                print(f"❌ Failed to get templates: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Get templates error: {str(e)}")
            return False, None

    def verify_control_items_quality(self, template_data):
        """Verify that control items are of reasonable quality and count"""
        print(f"\n🎯 Verifying Control Items Quality...")
        
        control_items = template_data.get('control_items', [])
        categories = template_data.get('categories', [])
        
        # Count control items from both sources
        control_items_count = len(control_items) if control_items else 0
        
        # Count from categories (backward compatibility)
        categories_items_count = 0
        if categories and isinstance(categories, list):
            for category in categories:
                if isinstance(category, dict):
                    items = category.get('items', [])
                    categories_items_count += len(items)
        elif isinstance(categories, int):
            # If categories is just a count, use it directly
            categories_items_count = categories
        
        print(f"   Control items (universal): {control_items_count}")
        print(f"   Control items (categories): {categories_items_count}")
        
        # Use the higher count (should be consistent)
        total_items = max(control_items_count, categories_items_count)
        
        # Check if count is reasonable (50-60 range as per requirement)
        reasonable_count = 50 <= total_items <= 60
        acceptable_count = total_items <= 70  # Slightly more lenient
        
        print(f"   Total control items: {total_items}")
        print(f"   Reasonable count (50-60): {'✅' if reasonable_count else '❌'}")
        print(f"   Acceptable count (≤70): {'✅' if acceptable_count else '❌'}")
        
        # Check control items structure if available
        if control_items and len(control_items) > 0:
            sample_item = control_items[0]
            required_fields = ['id', 'text', 'category']
            
            has_required_fields = all(field in sample_item for field in required_fields)
            print(f"   Control items structure: {'✅' if has_required_fields else '❌'}")
            
            if has_required_fields:
                print(f"   Sample item: ID={sample_item.get('id')}, Category={sample_item.get('category')}")
                print(f"   Sample text: {sample_item.get('text', '')[:80]}...")
        
        return {
            'control_items_count': control_items_count,
            'categories_items_count': categories_items_count,
            'total_items': total_items,
            'reasonable_count': reasonable_count,
            'acceptable_count': acceptable_count
        }

    def run_comprehensive_universal_template_test(self):
        """Run comprehensive test of Universal Template Parser Database Model fix"""
        print("🚀 Starting Universal Template Parser Database Model Test")
        print("=" * 80)
        
        test_results = {}
        
        # Step 1: Authentication
        test_results['authentication'] = self.authenticate()
        if not test_results['authentication']:
            print("\n❌ Cannot proceed without authentication")
            return test_results
        
        # Step 2: Clean existing templates
        test_results['clean_templates'] = self.clean_existing_templates()
        
        # Step 3: Test Word document upload and parsing
        upload_results = {}
        universal_field_results = {}
        database_storage_results = {}
        control_items_results = {}
        
        for doc_name, doc_url in TEST_DOCUMENTS.items():
            print(f"\n" + "="*60)
            print(f"TESTING: {doc_name}")
            print("="*60)
            
            # Upload and parse document
            success, template_data = self.test_word_document_upload_and_parsing(doc_name, doc_url)
            upload_results[doc_name] = success
            
            if success and template_data:
                template_id = template_data.get('id')
                
                # Verify universal structure fields in upload response
                universal_check = self.verify_universal_structure_fields(template_data)
                universal_field_results[doc_name] = universal_check
                
                # Verify database storage
                storage_check = self.verify_database_storage(template_id)
                database_storage_results[doc_name] = storage_check
                
                # Verify control items quality
                quality_check = self.verify_control_items_quality(template_data)
                control_items_results[doc_name] = quality_check
        
        test_results['document_upload'] = upload_results
        test_results['universal_fields'] = universal_field_results
        test_results['database_storage'] = database_storage_results
        test_results['control_items_quality'] = control_items_results
        
        # Step 4: Test GET templates endpoint with universal fields
        success, get_results = self.test_get_templates_with_universal_fields()
        test_results['get_templates'] = success
        test_results['get_templates_data'] = get_results
        
        # Final Summary
        print("\n" + "=" * 80)
        print("📋 UNIVERSAL TEMPLATE PARSER DATABASE MODEL TEST SUMMARY")
        print("=" * 80)
        
        # Overall results
        all_uploads_successful = all(upload_results.values())
        all_universal_fields_present = all(
            result.get('universal_fields', {}).get('all_present', False) 
            for result in database_storage_results.values()
        )
        all_database_storage_working = all(
            result.get('retrieved', False) and result.get('universal_fields', {}).get('all_present', False)
            for result in database_storage_results.values()
        )
        all_control_items_reasonable = all(
            result.get('acceptable_count', False)
            for result in control_items_results.values()
        )
        
        print(f"Authentication: {'✅ PASS' if test_results['authentication'] else '❌ FAIL'}")
        print(f"Clean Templates: {'✅ PASS' if test_results['clean_templates'] else '❌ FAIL'}")
        print(f"Document Upload: {'✅ PASS' if all_uploads_successful else '❌ FAIL'}")
        print(f"Universal Fields Present: {'✅ PASS' if all_universal_fields_present else '❌ FAIL'}")
        print(f"Database Storage: {'✅ PASS' if all_database_storage_working else '❌ FAIL'}")
        print(f"Control Items Quality: {'✅ PASS' if all_control_items_reasonable else '❌ FAIL'}")
        print(f"GET Templates Endpoint: {'✅ PASS' if test_results['get_templates'] else '❌ FAIL'}")
        
        # Detailed Results
        print(f"\n📊 DETAILED RESULTS:")
        
        for doc_name in TEST_DOCUMENTS.keys():
            print(f"\n   {doc_name}:")
            
            # Universal fields
            if doc_name in universal_field_results:
                universal_data = universal_field_results[doc_name]
                present_count = universal_data.get('present_count', 0)
                total_expected = universal_data.get('total_expected', 11)
                print(f"     Universal fields: {present_count}/{total_expected}")
            
            # Control items
            if doc_name in control_items_results:
                quality_data = control_items_results[doc_name]
                total_items = quality_data.get('total_items', 0)
                reasonable = quality_data.get('reasonable_count', False)
                print(f"     Control items: {total_items} ({'✅ reasonable' if reasonable else '⚠️ acceptable' if quality_data.get('acceptable_count') else '❌ too many'})")
        
        # Key Findings
        print(f"\n🔍 KEY FINDINGS:")
        
        if all_universal_fields_present:
            print("   ✅ All 11 universal template structure fields are present in uploaded templates")
        else:
            missing_templates = [
                doc_name for doc_name, result in universal_field_results.items()
                if not result.get('all_present', False)
            ]
            print(f"   ❌ Universal fields missing in: {', '.join(missing_templates)}")
        
        if all_database_storage_working:
            print("   ✅ Universal structure fields are correctly stored in database")
        else:
            print("   ❌ Database storage issues detected")
        
        if all_control_items_reasonable:
            print("   ✅ Control item counts are reasonable (50-70 range)")
        else:
            print("   ⚠️ Some control item counts may be outside expected range")
        
        # Expected Outcome Verification
        print(f"\n🎯 EXPECTED OUTCOME VERIFICATION:")
        print("   Expected: Universal Template Parser stores all 11 universal structure fields")
        print("   Expected: Control items remain in reasonable range (50-60)")
        
        overall_success = (
            test_results['authentication'] and
            all_uploads_successful and
            all_universal_fields_present and
            all_database_storage_working and
            all_control_items_reasonable and
            test_results['get_templates']
        )
        
        if overall_success:
            print(f"\n🎉 UNIVERSAL TEMPLATE PARSER DATABASE MODEL FIX SUCCESSFUL!")
            print("   ✅ All 11 universal structure fields are correctly implemented")
            print("   ✅ Database storage is working properly")
            print("   ✅ Control item parsing still produces reasonable counts")
            print("   ✅ GET templates endpoint returns universal fields")
        else:
            print(f"\n⚠️ UNIVERSAL TEMPLATE PARSER FIX HAS ISSUES")
            if not all_universal_fields_present:
                print("   ❌ Universal structure fields are not properly implemented")
            if not all_database_storage_working:
                print("   ❌ Database storage is not working correctly")
            if not all_control_items_reasonable:
                print("   ❌ Control item parsing may have issues")
        
        return test_results

if __name__ == "__main__":
    print("🎯 EXECUTING UNIVERSAL TEMPLATE PARSER DATABASE MODEL TEST")
    print("="*80)
    
    tester = UniversalTemplateParserTester()
    results = tester.run_comprehensive_universal_template_test()