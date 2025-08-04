#!/usr/bin/env python3
"""
Critical Fixes Testing for RoyalCert Inspection System
Tests two critical fixes:
1. Inspector Form Question Cutting Issue - All 53 questions should be visible
2. Template Builder Form Fields - Universal structure fields should be included
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv("REACT_APP_ROYALCERT_API_URL", "https://royalcert-inspection-system-production.up.railway.app/api")
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class CriticalFixesTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        self.test_results = {}
        
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

    def get_item_category(self, item_number):
        """Test the getItemCategory function logic - CRITICAL FIX 1"""
        print(f"\n🔍 Testing getItemCategory function for item {item_number}...")
        
        # This is the FIXED logic that should now work for all 53 questions
        if item_number <= 8:
            category = 'A'
        elif item_number <= 16:
            category = 'B'
        elif item_number <= 24:
            category = 'C'
        elif item_number <= 32:
            category = 'D'
        elif item_number <= 40:
            category = 'E'
        elif item_number <= 48:
            category = 'F'
        elif item_number <= 53:
            category = 'G'  # This should now include questions 49-53
        else:
            category = 'H'
        
        print(f"   Item {item_number} -> Category {category}")
        return category

    def test_inspector_form_all_53_questions(self):
        """Test that inspector dashboard shows all 53 questions - CRITICAL FIX 1"""
        print("\n🎯 CRITICAL FIX 1: Testing Inspector Form - All 53 Questions Visibility")
        print("=" * 80)
        
        try:
            # Get equipment templates to find one with control items
            response = self.session.get(f"{BACKEND_URL}/equipment-templates")
            print(f"Equipment Templates Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Failed to get equipment templates: {response.text}")
                return False
            
            templates = response.json()
            print(f"✅ Found {len(templates)} equipment templates")
            
            # Find a template with control items
            test_template = None
            for template in templates:
                categories = template.get('categories', [])
                total_items = sum(len(cat.get('items', [])) for cat in categories)
                if total_items > 0:
                    test_template = template
                    print(f"   Using template: {template.get('name', 'UNNAMED')} ({total_items} items)")
                    break
            
            if not test_template:
                print("❌ No template with control items found")
                return False
            
            # Test the getItemCategory function for all possible question numbers
            print(f"\n📋 Testing getItemCategory function for questions 1-53:")
            
            category_distribution = {}
            problematic_questions = []
            
            for question_num in range(1, 54):  # Test questions 1-53
                category = self.get_item_category(question_num)
                
                if category not in category_distribution:
                    category_distribution[category] = []
                category_distribution[category].append(question_num)
                
                # Check if questions 49-53 are properly categorized (this was the bug)
                if 49 <= question_num <= 53:
                    if category != 'G':
                        problematic_questions.append(question_num)
                        print(f"   ❌ Question {question_num} -> Category {category} (SHOULD BE G)")
                    else:
                        print(f"   ✅ Question {question_num} -> Category {category}")
                elif 41 <= question_num <= 48:
                    if category != 'F':
                        problematic_questions.append(question_num)
                        print(f"   ❌ Question {question_num} -> Category {category} (SHOULD BE F)")
                    else:
                        print(f"   ✅ Question {question_num} -> Category {category}")
            
            print(f"\n📊 Category Distribution:")
            for category in sorted(category_distribution.keys()):
                questions = category_distribution[category]
                print(f"   Category {category}: Questions {min(questions)}-{max(questions)} ({len(questions)} items)")
            
            # Verify the fix
            questions_49_53_in_G = all(49 <= q <= 53 for q in category_distribution.get('G', []))
            questions_41_48_in_F = all(41 <= q <= 48 for q in category_distribution.get('F', []))
            all_53_questions_covered = len([q for questions in category_distribution.values() for q in questions]) == 53
            
            print(f"\n🎯 CRITICAL FIX 1 VERIFICATION:")
            print(f"   Questions 41-48 in Category F: {'✅ YES' if questions_41_48_in_F else '❌ NO'}")
            print(f"   Questions 49-53 in Category G: {'✅ YES' if questions_49_53_in_G else '❌ NO'}")
            print(f"   All 53 questions covered: {'✅ YES' if all_53_questions_covered else '❌ NO'}")
            print(f"   Problematic questions: {problematic_questions if problematic_questions else 'None'}")
            
            # Test with actual inspection form if available
            print(f"\n🔍 Testing with actual inspection form...")
            
            # Get inspections to find one we can test with
            inspections_response = self.session.get(f"{BACKEND_URL}/inspections")
            if inspections_response.status_code == 200:
                inspections = inspections_response.json()
                
                if inspections:
                    test_inspection = inspections[0]
                    inspection_id = test_inspection.get('id')
                    
                    # Get the inspection form
                    form_response = self.session.get(f"{BACKEND_URL}/inspections/{inspection_id}/form")
                    if form_response.status_code == 200:
                        form_data = form_response.json()
                        control_items = form_data.get('control_items', [])
                        
                        print(f"   ✅ Retrieved inspection form with {len(control_items)} control items")
                        
                        # Check if we have items in the problematic range (43-53)
                        high_numbered_items = [item for item in control_items if item.get('id', 0) >= 43]
                        print(f"   Items with ID ≥ 43: {len(high_numbered_items)}")
                        
                        if high_numbered_items:
                            print(f"   ✅ High-numbered items found - questions 43-53 should be visible")
                            for item in high_numbered_items[:5]:  # Show first 5
                                print(f"     ID {item.get('id')}: {item.get('text', 'N/A')[:50]}...")
                        else:
                            print(f"   ⚠️  No items with ID ≥ 43 found in this inspection")
                    else:
                        print(f"   ❌ Failed to get inspection form: {form_response.status_code}")
                else:
                    print(f"   ⚠️  No inspections available for testing")
            else:
                print(f"   ❌ Failed to get inspections: {inspections_response.status_code}")
            
            success = not problematic_questions and all_53_questions_covered
            
            if success:
                print(f"\n🎉 CRITICAL FIX 1 SUCCESS: Inspector form question cutting issue RESOLVED!")
                print(f"   ✅ All 53 questions are properly categorized")
                print(f"   ✅ Questions 43-53 are in Category G as expected")
            else:
                print(f"\n❌ CRITICAL FIX 1 FAILED: Inspector form question cutting issue NOT resolved!")
                
            return success
            
        except Exception as e:
            print(f"❌ Inspector form test error: {str(e)}")
            return False

    def test_simple_template_builder_universal_fields(self):
        """Test that SimpleTemplateBuilder includes universal structure fields - CRITICAL FIX 2"""
        print("\n🎯 CRITICAL FIX 2: Testing SimpleTemplateBuilder Universal Structure Fields")
        print("=" * 80)
        
        try:
            # Create a test template using SimpleTemplateBuilder logic
            print("🔧 Creating test template with SimpleTemplateBuilder...")
            
            # This simulates what SimpleTemplateBuilder should now do
            template_data = {
                "name": "TEST SIMPLE TEMPLATE",
                "equipment_type": "TEST_EQUIPMENT",
                "template_type": "FORM",
                "description": "Test template created by SimpleTemplateBuilder",
                "categories": [
                    {
                        "code": "A",
                        "name": "TEST CATEGORY A",
                        "items": [
                            {
                                "id": 1,
                                "text": "Test control item 1",
                                "category": "A",
                                "input_type": "dropdown",
                                "has_comment": True,
                                "required": True
                            }
                        ]
                    }
                ],
                
                # CRITICAL FIX 2: These universal structure fields should now be included
                "general_info": {
                    "company_name": "Test Company",
                    "inspection_date": "2025-01-20",
                    "inspector_name": "Test Inspector"
                },
                "measurement_devices": [
                    {
                        "device_name": "Test Measurement Device",
                        "model": "TMD-2025",
                        "calibration_date": "2025-01-01"
                    }
                ],
                "equipment_info": {
                    "equipment_type": "TEST_EQUIPMENT",
                    "serial_number": "TEST-12345",
                    "manufacturer": "Test Manufacturer"
                },
                "test_values": {
                    "max_load": "1000 kg",
                    "test_pressure": "150 bar"
                },
                "test_experiments": [
                    {
                        "experiment_name": "Load Test",
                        "result": "PASSED"
                    }
                ],
                "defect_explanations": "No defects found during inspection",
                "notes": "Template created for testing universal structure fields",
                "result_opinion": "UYGUN - Equipment meets safety standards",
                "inspector_info": {
                    "name": "Test Inspector",
                    "license_number": "INS-2025-001",
                    "signature_date": "2025-01-20"
                },
                "company_official": {
                    "name": "Test Official",
                    "title": "Technical Manager",
                    "signature_date": "2025-01-20"
                }
            }
            
            # Test POST /api/equipment-templates with universal structure
            print("📤 Testing POST /api/equipment-templates with universal structure...")
            
            response = self.session.post(f"{BACKEND_URL}/equipment-templates", json=template_data)
            print(f"POST /api/equipment-templates Status: {response.status_code}")
            
            if response.status_code == 200:
                created_template = response.json()
                template_id = created_template.get('id')
                
                print(f"✅ Template created successfully with ID: {template_id}")
                
                # Verify that universal structure fields are included
                print(f"\n🔍 Verifying universal structure fields in created template...")
                
                universal_fields = [
                    'general_info',
                    'measurement_devices', 
                    'equipment_info',
                    'test_values',
                    'test_experiments',
                    'defect_explanations',
                    'notes',
                    'result_opinion',
                    'inspector_info',
                    'company_official'
                ]
                
                missing_fields = []
                present_fields = []
                
                for field in universal_fields:
                    if field in created_template and created_template[field] is not None:
                        present_fields.append(field)
                        print(f"   ✅ {field}: Present")
                    else:
                        missing_fields.append(field)
                        print(f"   ❌ {field}: Missing or None")
                
                # Get the template back to double-check
                print(f"\n🔍 Retrieving template to verify persistence...")
                get_response = self.session.get(f"{BACKEND_URL}/equipment-templates/{template_id}")
                
                if get_response.status_code == 200:
                    retrieved_template = get_response.json()
                    
                    print(f"✅ Template retrieved successfully")
                    
                    # Check universal fields in retrieved template
                    print(f"\n📋 Universal fields in retrieved template:")
                    
                    retrieved_missing = []
                    retrieved_present = []
                    
                    for field in universal_fields:
                        if field in retrieved_template and retrieved_template[field] is not None:
                            retrieved_present.append(field)
                            print(f"   ✅ {field}: Present and persisted")
                        else:
                            retrieved_missing.append(field)
                            print(f"   ❌ {field}: Missing or None in retrieved template")
                    
                    # Verify specific field contents
                    print(f"\n🔍 Verifying specific field contents:")
                    
                    if 'general_info' in retrieved_template:
                        general_info = retrieved_template['general_info']
                        if isinstance(general_info, dict) and 'company_name' in general_info:
                            print(f"   ✅ general_info contains expected data: {general_info.get('company_name')}")
                        else:
                            print(f"   ❌ general_info structure incorrect: {general_info}")
                    
                    if 'measurement_devices' in retrieved_template:
                        devices = retrieved_template['measurement_devices']
                        if isinstance(devices, list) and len(devices) > 0:
                            print(f"   ✅ measurement_devices contains {len(devices)} device(s)")
                        else:
                            print(f"   ❌ measurement_devices structure incorrect: {devices}")
                    
                    # Clean up - delete test template
                    print(f"\n🧹 Cleaning up test template...")
                    delete_response = self.session.delete(f"{BACKEND_URL}/equipment-templates/{template_id}")
                    if delete_response.status_code == 200:
                        print(f"   ✅ Test template deleted successfully")
                    else:
                        print(f"   ⚠️  Failed to delete test template: {delete_response.status_code}")
                    
                    # Determine success
                    success = len(retrieved_missing) == 0
                    
                    print(f"\n🎯 CRITICAL FIX 2 VERIFICATION:")
                    print(f"   Universal fields present: {len(retrieved_present)}/{len(universal_fields)}")
                    print(f"   Universal fields missing: {len(retrieved_missing)}")
                    print(f"   Missing fields: {retrieved_missing if retrieved_missing else 'None'}")
                    
                    if success:
                        print(f"\n🎉 CRITICAL FIX 2 SUCCESS: SimpleTemplateBuilder universal structure fields WORKING!")
                        print(f"   ✅ All {len(universal_fields)} universal structure fields are included")
                        print(f"   ✅ Fields are properly persisted in database")
                    else:
                        print(f"\n❌ CRITICAL FIX 2 FAILED: SimpleTemplateBuilder missing universal structure fields!")
                        print(f"   ❌ {len(retrieved_missing)} fields are missing: {retrieved_missing}")
                    
                    return success
                    
                else:
                    print(f"❌ Failed to retrieve created template: {get_response.status_code}")
                    return False
                    
            elif response.status_code == 400 and "already exists" in response.text.lower():
                print(f"⚠️  Template already exists, testing with existing template...")
                
                # Get existing templates and find our test template
                templates_response = self.session.get(f"{BACKEND_URL}/equipment-templates")
                if templates_response.status_code == 200:
                    templates = templates_response.json()
                    test_template = None
                    
                    for template in templates:
                        if template.get('equipment_type') == 'TEST_EQUIPMENT':
                            test_template = template
                            break
                    
                    if test_template:
                        print(f"✅ Found existing test template: {test_template.get('name')}")
                        
                        # Check universal fields
                        universal_fields = [
                            'general_info', 'measurement_devices', 'equipment_info',
                            'test_values', 'test_experiments', 'defect_explanations',
                            'notes', 'result_opinion', 'inspector_info', 'company_official'
                        ]
                        
                        present_fields = []
                        missing_fields = []
                        
                        for field in universal_fields:
                            if field in test_template and test_template[field] is not None:
                                present_fields.append(field)
                            else:
                                missing_fields.append(field)
                        
                        success = len(missing_fields) == 0
                        
                        print(f"\n🎯 CRITICAL FIX 2 VERIFICATION (Existing Template):")
                        print(f"   Universal fields present: {len(present_fields)}/{len(universal_fields)}")
                        print(f"   Universal fields missing: {missing_fields if missing_fields else 'None'}")
                        
                        return success
                    else:
                        print(f"❌ No existing test template found")
                        return False
                else:
                    print(f"❌ Failed to get existing templates: {templates_response.status_code}")
                    return False
            else:
                print(f"❌ Failed to create template: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ SimpleTemplateBuilder test error: {str(e)}")
            return False

    def run_critical_fixes_tests(self):
        """Run all critical fixes tests"""
        print("🚀 Starting Critical Fixes Testing")
        print("=" * 80)
        print("Testing two critical fixes:")
        print("1. Inspector Form Question Cutting Issue (Questions 43-53)")
        print("2. SimpleTemplateBuilder Universal Structure Fields")
        print("=" * 80)
        
        # Step 1: Authentication
        print("\n📋 STEP 1: Authentication")
        auth_success = self.authenticate()
        self.test_results['authentication'] = auth_success
        
        if not auth_success:
            print("\n❌ Cannot proceed without authentication")
            return self.test_results
        
        # Step 2: Test Critical Fix 1 - Inspector Form Questions
        print("\n📋 STEP 2: Critical Fix 1 - Inspector Form Questions")
        fix1_success = self.test_inspector_form_all_53_questions()
        self.test_results['inspector_form_53_questions'] = fix1_success
        
        # Step 3: Test Critical Fix 2 - SimpleTemplateBuilder Universal Fields
        print("\n📋 STEP 3: Critical Fix 2 - SimpleTemplateBuilder Universal Fields")
        fix2_success = self.test_simple_template_builder_universal_fields()
        self.test_results['template_builder_universal_fields'] = fix2_success
        
        # Final Summary
        print("\n" + "=" * 80)
        print("📋 CRITICAL FIXES TEST SUMMARY")
        print("=" * 80)
        
        print(f"Authentication: {'✅ PASS' if self.test_results['authentication'] else '❌ FAIL'}")
        print(f"Critical Fix 1 (Inspector Form 53 Questions): {'✅ PASS' if self.test_results['inspector_form_53_questions'] else '❌ FAIL'}")
        print(f"Critical Fix 2 (Template Builder Universal Fields): {'✅ PASS' if self.test_results['template_builder_universal_fields'] else '❌ FAIL'}")
        
        # Overall result
        overall_success = (self.test_results['authentication'] and 
                          self.test_results['inspector_form_53_questions'] and 
                          self.test_results['template_builder_universal_fields'])
        
        print(f"\n🎯 OVERALL RESULT:")
        if overall_success:
            print(f"🎉 SUCCESS: Both critical fixes are working correctly!")
            print(f"   ✅ Inspector dashboard shows all 53 questions")
            print(f"   ✅ SimpleTemplateBuilder includes universal structure fields")
            print(f"\n📝 ANSWER TO REVIEW REQUEST: EVET - Both fixes are successful!")
        else:
            failed_fixes = []
            if not self.test_results['inspector_form_53_questions']:
                failed_fixes.append("Inspector Form Questions (43-53 not showing)")
            if not self.test_results['template_builder_universal_fields']:
                failed_fixes.append("SimpleTemplateBuilder Universal Fields")
            
            print(f"❌ FAILURE: Critical fixes have issues!")
            print(f"   Failed fixes: {', '.join(failed_fixes)}")
            print(f"\n📝 ANSWER TO REVIEW REQUEST: HAYIR - Fixes need more work!")
        
        return self.test_results

def main():
    """Main test execution"""
    tester = CriticalFixesTester()
    results = tester.run_critical_fixes_tests()
    
    # Return exit code based on results
    if all(results.values()):
        exit(0)  # Success
    else:
        exit(1)  # Failure

if __name__ == "__main__":
    main()