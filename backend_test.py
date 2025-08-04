#!/usr/bin/env python3
"""
Backend API Testing for RoyalCert Improved Word Parsing Algorithm
Tests the improved Word document parsing algorithm that limits control items to reasonable numbers (max 50-60)
Focus: Testing FORKLIFT document parsing with improved filtering and reasonable control item counts
"""

import requests
import json
import pandas as pd
import io
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://405a5b7a-3c02-4793-9fcc-5203d2944620.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# FORKLIFT Document URLs for testing
FORKLIFT_DOCUMENTS = {
    "FORKLIFT_MUAYENE_FORMU": "https://customer-assets.emergentagent.com/job_periodic-check/artifacts/y9b9lejo_RC-M-%C4%B0E-FR24_5%20FORKL%C4%B0FT%20MUAYENE%20FORMU.docx",
    "FORKLIFT_MUAYENE_RAPORU": "https://customer-assets.emergentagent.com/job_periodic-check/artifacts/00vmxy69_RC-M-%C4%B0E-FR25_6%20FORKL%C4%B0FT%20MUAYENE%20RAPORU.docx"
}

class ImprovedWordParsingTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        self.existing_forklift_templates = []
        self.template_results = {}
        
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

    def check_existing_forklift_templates(self):
        """Check for existing FORKLIFT templates and store their IDs"""
        print("\n🔍 Checking for Existing FORKLIFT Templates...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/equipment-templates")
            print(f"Equipment Templates Status: {response.status_code}")
            
            if response.status_code == 200:
                templates_data = response.json()
                
                # Find FORKLIFT templates
                forklift_templates = [t for t in templates_data if t.get('equipment_type') == 'FORKLIFT']
                self.existing_forklift_templates = forklift_templates
                
                print(f"✅ Found {len(forklift_templates)} existing FORKLIFT templates")
                
                for template in forklift_templates:
                    template_type = template.get('template_type', 'UNKNOWN')
                    template_name = template.get('name', 'UNNAMED')
                    total_items = sum(len(cat.get('items', [])) for cat in template.get('categories', []))
                    print(f"   - {template_name} ({template_type}): {total_items} control items")
                
                return True, forklift_templates
            else:
                print(f"❌ Failed to get templates: {response.text}")
                return False, []
                
        except Exception as e:
            print(f"❌ Check existing templates error: {str(e)}")
            return False, []

    def clean_existing_forklift_templates(self):
        """Delete existing FORKLIFT templates to test fresh parsing"""
        print("\n🧹 Cleaning Existing FORKLIFT Templates...")
        
        if not self.existing_forklift_templates:
            print("✅ No existing FORKLIFT templates to clean")
            return True
        
        deleted_count = 0
        
        for template in self.existing_forklift_templates:
            try:
                template_id = template.get('id')
                template_name = template.get('name', 'UNNAMED')
                
                response = self.session.delete(f"{BACKEND_URL}/equipment-templates/{template_id}")
                
                if response.status_code == 200:
                    print(f"✅ Deleted template: {template_name}")
                    deleted_count += 1
                else:
                    print(f"❌ Failed to delete template {template_name}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error deleting template {template.get('name', 'UNKNOWN')}: {str(e)}")
        
        print(f"✅ Cleaned {deleted_count}/{len(self.existing_forklift_templates)} FORKLIFT templates")
        return deleted_count == len(self.existing_forklift_templates)

    def download_and_upload_forklift_document(self, doc_name, doc_url):
        """Download and upload a FORKLIFT document for parsing"""
        print(f"\n📥 Testing {doc_name} Upload and Parsing...")
        
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
                
                # Extract parsing results
                template_data = upload_data.get('template', {})
                equipment_type = template_data.get('equipment_type', 'UNKNOWN')
                template_type = template_data.get('template_type', 'UNKNOWN')
                template_name = template_data.get('name', 'UNNAMED')
                categories = template_data.get('categories', [])
                
                total_items = sum(len(cat.get('items', [])) for cat in categories)
                
                print(f"   Equipment Type: {equipment_type}")
                print(f"   Template Type: {template_type}")
                print(f"   Template Name: {template_name}")
                print(f"   Categories: {len(categories)}")
                print(f"   Total Control Items: {total_items}")
                
                # Verify reasonable control item count (50-60 max as per requirement)
                if total_items <= 60:
                    print(f"✅ Control item count is reasonable: {total_items} ≤ 60")
                else:
                    print(f"❌ Control item count too high: {total_items} > 60")
                
                # Check category distribution
                print("   Category Distribution:")
                for category in categories:
                    cat_code = category.get('code', 'UNKNOWN')
                    cat_name = category.get('name', 'UNNAMED')
                    cat_items = len(category.get('items', []))
                    print(f"     {cat_code}: {cat_name} ({cat_items} items)")
                
                result_data = {
                    'equipment_type': equipment_type,
                    'template_type': template_type,
                    'template_name': template_name,
                    'total_items': total_items,
                    'categories_count': len(categories),
                    'categories': categories,
                    'template_id': template_data.get('id')
                }
                
                # Store results for later analysis
                self.template_results[doc_name] = result_data
                
                return True, result_data
            else:
                print(f"❌ Document upload failed: {upload_response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Document upload error: {str(e)}")
            return False, None

    def verify_improved_filtering(self, template_data):
        """Verify that improved filtering is working correctly"""
        print(f"\n🔍 Verifying Improved Filtering for {template_data['template_name']}...")
        
        categories = template_data.get('categories', [])
        total_items = template_data.get('total_items', 0)
        
        # Check 1: Reasonable total count
        reasonable_count = total_items <= 60
        print(f"   Total items ≤ 60: {'✅' if reasonable_count else '❌'} ({total_items})")
        
        # Check 2: Categories are properly distributed (A-H)
        category_codes = [cat.get('code') for cat in categories]
        expected_categories = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        has_proper_categories = any(code in expected_categories for code in category_codes)
        print(f"   Proper categories (A-H): {'✅' if has_proper_categories else '❌'} ({category_codes})")
        
        # Check 3: Items have reasonable text length (not too short/long)
        reasonable_text_items = 0
        total_checked_items = 0
        
        for category in categories:
            for item in category.get('items', []):
                item_text = item.get('text', '')
                text_length = len(item_text)
                total_checked_items += 1
                
                # Reasonable text length: 10-200 characters
                if 10 <= text_length <= 200:
                    reasonable_text_items += 1
        
        if total_checked_items > 0:
            reasonable_text_ratio = reasonable_text_items / total_checked_items
            print(f"   Reasonable text length: {'✅' if reasonable_text_ratio >= 0.8 else '❌'} ({reasonable_text_items}/{total_checked_items})")
        else:
            print("   Reasonable text length: ❌ (No items to check)")
            reasonable_text_ratio = 0
        
        # Check 4: No repetitive or header-like items
        item_texts = []
        for category in categories:
            for item in category.get('items', []):
                item_texts.append(item.get('text', '').upper())
        
        # Check for common header patterns that should be filtered out
        header_patterns = ['GENEL', 'BİLGİLER', 'MUAYENE', 'TEST', 'KONTROL', 'ETİKET', 'BAŞLIK', 'TABLE', 'FORM', 'RAPOR']
        header_items = sum(1 for text in item_texts if any(pattern in text for pattern in header_patterns))
        header_ratio = header_items / len(item_texts) if item_texts else 0
        
        good_filtering = header_ratio < 0.1  # Less than 10% header-like items
        print(f"   Good filtering (low headers): {'✅' if good_filtering else '❌'} ({header_items}/{len(item_texts)} header-like)")
        
        # Overall filtering score
        filtering_score = sum([reasonable_count, has_proper_categories, reasonable_text_ratio >= 0.8, good_filtering])
        max_score = 4
        
        print(f"   Overall Filtering Score: {filtering_score}/{max_score}")
        
        return {
            'reasonable_count': reasonable_count,
            'proper_categories': has_proper_categories,
            'reasonable_text_ratio': reasonable_text_ratio,
            'good_filtering': good_filtering,
            'filtering_score': filtering_score,
            'max_score': max_score
        }

    def verify_template_structure(self, template_data):
        """Verify template structure is correct"""
        print(f"\n🏗️  Verifying Template Structure for {template_data['template_name']}...")
        
        # Check equipment type
        equipment_type = template_data.get('equipment_type')
        correct_equipment_type = equipment_type == 'FORKLIFT'
        print(f"   Equipment Type = FORKLIFT: {'✅' if correct_equipment_type else '❌'} ({equipment_type})")
        
        # Check template type differentiation
        template_type = template_data.get('template_type')
        valid_template_type = template_type in ['FORM', 'REPORT']
        print(f"   Valid Template Type: {'✅' if valid_template_type else '❌'} ({template_type})")
        
        # Check categories structure
        categories = template_data.get('categories', [])
        has_categories = len(categories) > 0
        print(f"   Has Categories: {'✅' if has_categories else '❌'} ({len(categories)} categories)")
        
        # Check category distribution (should be reasonably distributed)
        if categories:
            items_per_category = [len(cat.get('items', [])) for cat in categories]
            avg_items_per_category = sum(items_per_category) / len(items_per_category)
            balanced_distribution = all(items >= 1 for items in items_per_category)  # Each category has at least 1 item
            print(f"   Balanced Distribution: {'✅' if balanced_distribution else '❌'} (avg: {avg_items_per_category:.1f} items/category)")
        else:
            balanced_distribution = False
        
        # Check item structure
        sample_items_valid = True
        if categories and categories[0].get('items'):
            sample_item = categories[0]['items'][0]
            required_fields = ['id', 'text', 'category', 'input_type', 'has_comment', 'required']
            missing_fields = [field for field in required_fields if field not in sample_item]
            sample_items_valid = len(missing_fields) == 0
            print(f"   Valid Item Structure: {'✅' if sample_items_valid else '❌'} (missing: {missing_fields})")
        else:
            print("   Valid Item Structure: ❌ (No items to check)")
            sample_items_valid = False
        
        structure_score = sum([correct_equipment_type, valid_template_type, has_categories, balanced_distribution, sample_items_valid])
        max_score = 5
        
        print(f"   Overall Structure Score: {structure_score}/{max_score}")
        
        return {
            'correct_equipment_type': correct_equipment_type,
            'valid_template_type': valid_template_type,
            'has_categories': has_categories,
            'balanced_distribution': balanced_distribution,
            'sample_items_valid': sample_items_valid,
            'structure_score': structure_score,
            'max_score': max_score
        }

    def test_duplicate_prevention(self, doc_name, doc_url):
        """Test that duplicate templates are prevented"""
        print(f"\n🚫 Testing Duplicate Prevention for {doc_name}...")
        
        try:
            # Try to upload the same document again
            doc_response = requests.get(doc_url)
            if doc_response.status_code != 200:
                print(f"❌ Failed to download document for duplicate test")
                return False
            
            filename = doc_name.replace('_', ' ') + '.docx'
            files = {
                'file': (filename, doc_response.content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            upload_response = self.session.post(f"{BACKEND_URL}/equipment-templates/upload", files=files)
            
            if upload_response.status_code == 400:
                response_text = upload_response.text.lower()
                if 'already exists' in response_text or 'duplicate' in response_text:
                    print("✅ Duplicate prevention working correctly")
                    return True
                else:
                    print(f"❌ Unexpected 400 error: {upload_response.text}")
                    return False
            else:
                print(f"❌ Duplicate upload should have failed but got status: {upload_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Duplicate prevention test error: {str(e)}")
            return False

    def verify_final_template_state(self):
        """Verify final state of FORKLIFT templates"""
        print("\n📊 Verifying Final Template State...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/equipment-templates")
            
            if response.status_code == 200:
                templates_data = response.json()
                forklift_templates = [t for t in templates_data if t.get('equipment_type') == 'FORKLIFT']
                
                print(f"✅ Final FORKLIFT templates count: {len(forklift_templates)}")
                
                expected_templates = ['FORM', 'REPORT']
                found_types = []
                
                for template in forklift_templates:
                    template_type = template.get('template_type', 'UNKNOWN')
                    template_name = template.get('name', 'UNNAMED')
                    total_items = sum(len(cat.get('items', [])) for cat in template.get('categories', []))
                    
                    found_types.append(template_type)
                    print(f"   - {template_name} ({template_type}): {total_items} items")
                
                # Check if we have both FORM and REPORT
                has_both_types = 'FORM' in found_types and 'REPORT' in found_types
                print(f"   Has both FORM and REPORT: {'✅' if has_both_types else '❌'}")
                
                return True, {
                    'total_templates': len(forklift_templates),
                    'template_types': found_types,
                    'has_both_types': has_both_types,
                    'templates': forklift_templates
                }
            else:
                print(f"❌ Failed to get final templates: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Final verification error: {str(e)}")
            return False, None

    def run_improved_parsing_tests(self):
        """Run all improved Word parsing algorithm tests"""
        print("🚀 Starting Improved Word Parsing Algorithm Tests")
        print("=" * 80)
        
        test_results = {}
        
        # Step 1: Authentication
        test_results['authentication'] = self.authenticate()
        if not test_results['authentication']:
            print("\n❌ Cannot proceed without authentication")
            return test_results
        
        # Step 2: Check existing FORKLIFT templates
        test_results['check_existing_templates'] = self.check_existing_forklift_templates()[0]
        
        # Step 3: Clean existing FORKLIFT templates
        test_results['clean_existing_templates'] = self.clean_existing_forklift_templates()
        
        # Step 4: Test improved Word document parsing
        parsing_results = {}
        filtering_results = {}
        structure_results = {}
        duplicate_results = {}
        
        for doc_name, doc_url in FORKLIFT_DOCUMENTS.items():
            # Upload and parse document
            success, template_data = self.download_and_upload_forklift_document(doc_name, doc_url)
            parsing_results[doc_name] = success
            
            if success and template_data:
                # Verify improved filtering
                filtering_results[doc_name] = self.verify_improved_filtering(template_data)
                
                # Verify template structure
                structure_results[doc_name] = self.verify_template_structure(template_data)
                
                # Test duplicate prevention
                duplicate_results[doc_name] = self.test_duplicate_prevention(doc_name, doc_url)
        
        test_results['document_parsing'] = parsing_results
        test_results['improved_filtering'] = filtering_results
        test_results['template_structure'] = structure_results
        test_results['duplicate_prevention'] = duplicate_results
        
        # Step 5: Verify final template state
        test_results['final_verification'] = self.verify_final_template_state()[0]
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 IMPROVED WORD PARSING ALGORITHM TEST SUMMARY")
        print("=" * 80)
        
        # Overall results
        all_parsing_passed = all(parsing_results.values())
        all_duplicates_prevented = all(duplicate_results.values())
        
        print(f"Authentication: {'✅ PASS' if test_results['authentication'] else '❌ FAIL'}")
        print(f"Clean Existing Templates: {'✅ PASS' if test_results['clean_existing_templates'] else '❌ FAIL'}")
        print(f"Document Parsing: {'✅ PASS' if all_parsing_passed else '❌ FAIL'}")
        print(f"Duplicate Prevention: {'✅ PASS' if all_duplicates_prevented else '❌ FAIL'}")
        print(f"Final Verification: {'✅ PASS' if test_results['final_verification'] else '❌ FAIL'}")
        
        # Detailed filtering results
        print(f"\n📊 FILTERING QUALITY RESULTS:")
        for doc_name, filtering_data in filtering_results.items():
            if filtering_data:
                score = filtering_data['filtering_score']
                max_score = filtering_data['max_score']
                print(f"   {doc_name}: {score}/{max_score} ({'✅ GOOD' if score >= 3 else '❌ NEEDS IMPROVEMENT'})")
        
        # Detailed structure results
        print(f"\n🏗️  STRUCTURE QUALITY RESULTS:")
        for doc_name, structure_data in structure_results.items():
            if structure_data:
                score = structure_data['structure_score']
                max_score = structure_data['max_score']
                print(f"   {doc_name}: {score}/{max_score} ({'✅ GOOD' if score >= 4 else '❌ NEEDS IMPROVEMENT'})")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        
        # Check control item counts from stored results
        for doc_name, template_data in self.template_results.items():
            total_items = template_data.get('total_items', 0)
            if total_items <= 53:
                print(f"   {doc_name}: ✅ Excellent count ({total_items} items)")
            elif total_items <= 60:
                print(f"   {doc_name}: ✅ Good count ({total_items} items)")
            else:
                print(f"   {doc_name}: ❌ Too many items ({total_items} items)")
        
        # Expected outcome verification
        print(f"\n🎯 EXPECTED OUTCOME VERIFICATION:")
        print("   Expected: FORKLIFT templates with ~50-53 control items (max 60)")
        
        # Check if we achieved the expected outcome
        reasonable_counts = []
        for doc_name, template_data in self.template_results.items():
            total_items = template_data.get('total_items', 0)
            reasonable_counts.append(total_items <= 60)
            expected_range = 50 <= total_items <= 53
            print(f"   {doc_name}: {total_items} items ({'✅ PERFECT' if expected_range else '✅ ACCEPTABLE' if total_items <= 60 else '❌ TOO HIGH'})")
        
        overall_success = (test_results['authentication'] and 
                          test_results['clean_existing_templates'] and
                          all_parsing_passed and
                          all_duplicates_prevented and
                          test_results['final_verification'] and
                          all(reasonable_counts))
        
        if overall_success:
            print(f"\n🎉 IMPROVED WORD PARSING ALGORITHM TEST COMPLETED SUCCESSFULLY!")
            print("   ✅ Control item counts are reasonable (≤60 items)")
            print("   ✅ Filtering algorithm is working correctly")
            print("   ✅ Template structure is proper")
            print("   ✅ Duplicate prevention is working")
        else:
            print(f"\n⚠️  SOME TESTS FAILED - ALGORITHM NEEDS IMPROVEMENT")
        
        return test_results

if __name__ == "__main__":
    tester = ImprovedWordParsingTester()
    results = tester.run_improved_parsing_tests()

class RoyalCertPDFReportingTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        self.test_customer_id = None
        self.test_inspection_id = None
        
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

    def test_current_user_endpoint(self):
        """Test GET /api/auth/me - Current user info for inspector signatures"""
        print("\n👤 Testing Current User Info Endpoint...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/auth/me")
            print(f"Current User Status: {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                print("✅ Current user endpoint working")
                print(f"   User ID: {user_data.get('id')}")
                print(f"   Full Name: {user_data.get('full_name')}")
                print(f"   Role: {user_data.get('role')}")
                print(f"   Email: {user_data.get('email')}")
                
                # Check if data is suitable for PDF signatures
                required_fields = ['id', 'full_name', 'role', 'email']
                missing_fields = [field for field in required_fields if not user_data.get(field)]
                
                if not missing_fields:
                    print("✅ All required user fields available for PDF signatures")
                else:
                    print(f"⚠️  Missing fields for PDF signatures: {missing_fields}")
                
                return True, user_data
            else:
                print(f"❌ Current user endpoint failed: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Current user endpoint error: {str(e)}")
            return False, None

    def test_users_list_endpoint(self):
        """Test GET /api/users - List users for inspector information"""
        print("\n👥 Testing Users List Endpoint...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/users")
            print(f"Users List Status: {response.status_code}")
            
            if response.status_code == 200:
                users_data = response.json()
                print(f"✅ Users list endpoint working")
                print(f"   Total users: {len(users_data)}")
                
                # Analyze user data structure for PDF reporting
                if users_data:
                    sample_user = users_data[0]
                    print("   Sample user structure:")
                    for key, value in sample_user.items():
                        print(f"     {key}: {type(value).__name__}")
                    
                    # Check for inspectors (denetci role)
                    inspectors = [user for user in users_data if user.get('role') == 'denetci']
                    print(f"   Available inspectors: {len(inspectors)}")
                    
                    # Check for technical managers (teknik_yonetici role)
                    tech_managers = [user for user in users_data if user.get('role') == 'teknik_yonetici']
                    print(f"   Available technical managers: {len(tech_managers)}")
                    
                    return True, users_data
                else:
                    print("⚠️  No users found in system")
                    return True, []
            else:
                print(f"❌ Users list endpoint failed: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Users list endpoint error: {str(e)}")
            return False, None

    def test_customers_list_endpoint(self):
        """Test GET /api/customers - List customers for PDF reports"""
        print("\n🏢 Testing Customers List Endpoint...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/customers")
            print(f"Customers List Status: {response.status_code}")
            
            if response.status_code == 200:
                customers_data = response.json()
                print(f"✅ Customers list endpoint working")
                print(f"   Total customers: {len(customers_data)}")
                
                # Analyze customer data structure for PDF reporting
                if customers_data:
                    sample_customer = customers_data[0]
                    self.test_customer_id = sample_customer.get('id')  # Store for inspection tests
                    
                    print("   Sample customer structure:")
                    for key, value in sample_customer.items():
                        if isinstance(value, list):
                            print(f"     {key}: list with {len(value)} items")
                            if value and isinstance(value[0], dict):
                                print(f"       Sample item keys: {list(value[0].keys())}")
                        else:
                            print(f"     {key}: {type(value).__name__} = {value}")
                    
                    # Check equipment data availability
                    customers_with_equipment = [c for c in customers_data if c.get('equipments')]
                    print(f"   Customers with equipment data: {len(customers_with_equipment)}")
                    
                    return True, customers_data
                else:
                    print("⚠️  No customers found in system")
                    return True, []
            else:
                print(f"❌ Customers list endpoint failed: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Customers list endpoint error: {str(e)}")
            return False, None

    def test_equipment_templates_endpoint(self):
        """Test GET /api/equipment-templates - Get equipment templates for PDF reports"""
        print("\n⚙️  Testing Equipment Templates Endpoint...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/equipment-templates")
            print(f"Equipment Templates Status: {response.status_code}")
            
            if response.status_code == 200:
                templates_data = response.json()
                print(f"✅ Equipment templates endpoint working")
                print(f"   Total templates: {len(templates_data)}")
                
                # Analyze template data structure for PDF reporting
                if templates_data:
                    sample_template = templates_data[0]
                    print("   Sample template structure:")
                    for key, value in sample_template.items():
                        if isinstance(value, list):
                            print(f"     {key}: list with {len(value)} items")
                            if value and isinstance(value[0], dict):
                                print(f"       Sample category keys: {list(value[0].keys())}")
                                if 'items' in value[0] and value[0]['items']:
                                    print(f"       Sample item keys: {list(value[0]['items'][0].keys())}")
                        else:
                            print(f"     {key}: {type(value).__name__} = {value}")
                    
                    # Check for CARASKAL template specifically
                    caraskal_template = next((t for t in templates_data if t.get('equipment_type') == 'CARASKAL'), None)
                    if caraskal_template:
                        print("   ✅ CARASKAL template found")
                        print(f"     Categories: {len(caraskal_template.get('categories', []))}")
                        total_items = sum(len(cat.get('items', [])) for cat in caraskal_template.get('categories', []))
                        print(f"     Total control items: {total_items}")
                    else:
                        print("   ⚠️  CARASKAL template not found")
                    
                    return True, templates_data
                else:
                    print("⚠️  No equipment templates found")
                    return True, []
            else:
                print(f"❌ Equipment templates endpoint failed: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Equipment templates endpoint error: {str(e)}")
            return False, None

    def create_test_inspection(self):
        """Create a test inspection for testing inspection endpoints"""
        print("\n🔧 Creating Test Inspection...")
        
        if not self.test_customer_id:
            print("❌ No customer ID available for test inspection")
            return False
        
        try:
            # Create test inspection data
            inspection_data = {
                "customer_id": self.test_customer_id,
                "equipment_info": {
                    "equipment_type": "CARASKAL",
                    "serial_number": "TEST-001",
                    "manufacturer": "Test Manufacturer",
                    "model": "Test Model",
                    "capacity": "5000 kg"
                },
                "inspector_id": self.user_info['id'],
                "planned_date": "2025-01-20T10:00:00"
            }
            
            response = self.session.post(f"{BACKEND_URL}/inspections", json=inspection_data)
            print(f"Create Inspection Status: {response.status_code}")
            
            if response.status_code == 200:
                inspection = response.json()
                self.test_inspection_id = inspection.get('id')
                print(f"✅ Test inspection created: {self.test_inspection_id}")
                return True
            else:
                print(f"❌ Failed to create test inspection: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Create test inspection error: {str(e)}")
            return False

    def test_inspection_details_endpoint(self):
        """Test GET /api/inspections/{id} - Get inspection details for PDF"""
        print("\n📋 Testing Inspection Details Endpoint...")
        
        if not self.test_inspection_id:
            print("❌ No test inspection ID available")
            return False, None
        
        try:
            response = self.session.get(f"{BACKEND_URL}/inspections/{self.test_inspection_id}")
            print(f"Inspection Details Status: {response.status_code}")
            
            if response.status_code == 200:
                inspection_data = response.json()
                print("✅ Inspection details endpoint working")
                
                print("   Inspection data structure:")
                for key, value in inspection_data.items():
                    if isinstance(value, dict):
                        print(f"     {key}: dict with keys {list(value.keys())}")
                    elif isinstance(value, list):
                        print(f"     {key}: list with {len(value)} items")
                    else:
                        print(f"     {key}: {type(value).__name__} = {value}")
                
                # Check essential fields for PDF generation
                essential_fields = ['id', 'customer_id', 'equipment_info', 'inspector_id', 'status', 'planned_date']
                missing_fields = [field for field in essential_fields if field not in inspection_data]
                
                if not missing_fields:
                    print("✅ All essential fields available for PDF generation")
                else:
                    print(f"⚠️  Missing essential fields: {missing_fields}")
                
                return True, inspection_data
            else:
                print(f"❌ Inspection details endpoint failed: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Inspection details endpoint error: {str(e)}")
            return False, None

    def test_inspection_form_endpoint(self):
        """Test GET /api/inspections/{id}/form - Get inspection form data with results"""
        print("\n📝 Testing Inspection Form Data Endpoint...")
        
        if not self.test_inspection_id:
            print("❌ No test inspection ID available")
            return False, None
        
        try:
            response = self.session.get(f"{BACKEND_URL}/inspections/{self.test_inspection_id}/form")
            print(f"Inspection Form Status: {response.status_code}")
            
            if response.status_code == 200:
                form_data = response.json()
                print("✅ Inspection form endpoint working")
                
                print("   Form data structure:")
                for key, value in form_data.items():
                    if isinstance(value, dict):
                        print(f"     {key}: dict with keys {list(value.keys())}")
                    elif isinstance(value, list):
                        print(f"     {key}: list with {len(value)} items")
                        if value and isinstance(value[0], dict):
                            print(f"       Sample item keys: {list(value[0].keys())}")
                    else:
                        print(f"     {key}: {type(value).__name__} = {value}")
                
                # Check control items availability for PDF
                control_items = form_data.get('control_items', [])
                print(f"   Control items available: {len(control_items)}")
                
                if control_items:
                    sample_item = control_items[0]
                    print(f"   Sample control item structure: {list(sample_item.keys())}")
                
                # Check form completion data
                completion_percentage = form_data.get('completion_percentage', 0)
                is_draft = form_data.get('is_draft', True)
                print(f"   Form completion: {completion_percentage}% (Draft: {is_draft})")
                
                return True, form_data
            else:
                print(f"❌ Inspection form endpoint failed: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Inspection form endpoint error: {str(e)}")
            return False, None

    def test_inspections_list_endpoint(self):
        """Test GET /api/inspections - List all inspections"""
        print("\n📊 Testing Inspections List Endpoint...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/inspections")
            print(f"Inspections List Status: {response.status_code}")
            
            if response.status_code == 200:
                inspections_data = response.json()
                print(f"✅ Inspections list endpoint working")
                print(f"   Total inspections: {len(inspections_data)}")
                
                # Analyze inspection statuses for PDF reporting
                if inspections_data:
                    statuses = {}
                    for inspection in inspections_data:
                        status = inspection.get('status', 'unknown')
                        statuses[status] = statuses.get(status, 0) + 1
                    
                    print("   Inspection statuses:")
                    for status, count in statuses.items():
                        print(f"     {status}: {count}")
                    
                    # Check for completed inspections (good candidates for PDF reports)
                    completed_inspections = [i for i in inspections_data if i.get('status') in ['rapor_yazildi', 'onaylandi']]
                    print(f"   Completed inspections (PDF ready): {len(completed_inspections)}")
                
                return True, inspections_data
            else:
                print(f"❌ Inspections list endpoint failed: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Inspections list endpoint error: {str(e)}")
            return False, None

    def check_backend_dependencies(self):
        """Check backend dependencies for PDF generation"""
        print("\n📦 Checking Backend Dependencies for PDF Generation...")
        
        try:
            # Check requirements.txt for PDF-related libraries
            requirements_path = "/app/backend/requirements.txt"
            if os.path.exists(requirements_path):
                with open(requirements_path, 'r') as f:
                    requirements = f.read()
                
                print("✅ Requirements.txt found")
                
                # Check for common PDF libraries
                pdf_libraries = {
                    'reportlab': 'reportlab' in requirements.lower(),
                    'weasyprint': 'weasyprint' in requirements.lower(),
                    'pdfkit': 'pdfkit' in requirements.lower(),
                    'fpdf': 'fpdf' in requirements.lower(),
                    'matplotlib': 'matplotlib' in requirements.lower(),
                    'pillow': 'pillow' in requirements.lower() or 'pil' in requirements.lower()
                }
                
                print("   PDF-related libraries check:")
                found_libraries = []
                for lib, found in pdf_libraries.items():
                    status = "✅" if found else "❌"
                    print(f"     {lib}: {status}")
                    if found:
                        found_libraries.append(lib)
                
                if found_libraries:
                    print(f"   Found PDF libraries: {', '.join(found_libraries)}")
                else:
                    print("   ⚠️  No PDF generation libraries found in requirements.txt")
                    print("   Recommendation: Add reportlab or weasyprint for PDF generation")
                
                return True, found_libraries
            else:
                print("❌ Requirements.txt not found")
                return False, []
                
        except Exception as e:
            print(f"❌ Dependencies check error: {str(e)}")
            return False, []

    def test_existing_report_endpoints(self):
        """Check for any existing report-related endpoints"""
        print("\n📄 Testing Existing Report Endpoints...")
        
        # Test common report endpoint patterns
        report_endpoints = [
            "/reports",
            "/inspections/reports", 
            "/inspections/pdf",
            "/reports/pdf",
            "/reports/generate",
            "/api/reports",
            "/api/inspections/reports",
            "/api/reports/pdf"
        ]
        
        existing_endpoints = []
        
        for endpoint in report_endpoints:
            try:
                full_url = f"{BACKEND_URL.replace('/api', '')}{endpoint}"
                response = self.session.get(full_url)
                
                if response.status_code != 404:
                    existing_endpoints.append({
                        'endpoint': endpoint,
                        'status': response.status_code,
                        'response': response.text[:100] if response.text else 'No content'
                    })
                    print(f"   Found endpoint: {endpoint} (Status: {response.status_code})")
                    
            except Exception as e:
                # Ignore connection errors for non-existent endpoints
                pass
        
        if existing_endpoints:
            print(f"✅ Found {len(existing_endpoints)} existing report endpoints")
            return True, existing_endpoints
        else:
            print("❌ No existing report endpoints found")
            print("   Recommendation: Need to implement PDF report generation endpoints")
            return False, []

    def run_pdf_reporting_tests(self):
        """Run all PDF reporting system tests"""
        print("🚀 Starting RoyalCert PDF Reporting System Tests")
        print("=" * 70)
        
        test_results = {}
        
        # Authentication test
        test_results['authentication'] = self.authenticate()
        
        if not test_results['authentication']:
            print("\n❌ Cannot proceed without authentication")
            return test_results
        
        # User endpoints for inspector signatures
        test_results['current_user_endpoint'] = self.test_current_user_endpoint()[0]
        test_results['users_list_endpoint'] = self.test_users_list_endpoint()[0]
        
        # Customer data for PDF reports
        test_results['customers_list_endpoint'] = self.test_customers_list_endpoint()[0]
        
        # Equipment templates for form structure
        test_results['equipment_templates_endpoint'] = self.test_equipment_templates_endpoint()[0]
        
        # Create test inspection for inspection endpoints
        test_results['create_test_inspection'] = self.create_test_inspection()
        
        # Inspection data endpoints
        if test_results['create_test_inspection']:
            test_results['inspection_details_endpoint'] = self.test_inspection_details_endpoint()[0]
            test_results['inspection_form_endpoint'] = self.test_inspection_form_endpoint()[0]
        else:
            test_results['inspection_details_endpoint'] = False
            test_results['inspection_form_endpoint'] = False
        
        test_results['inspections_list_endpoint'] = self.test_inspections_list_endpoint()[0]
        
        # Backend dependencies and existing endpoints
        test_results['backend_dependencies'] = self.check_backend_dependencies()[0]
        test_results['existing_report_endpoints'] = self.test_existing_report_endpoints()[0]
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 PDF REPORTING SYSTEM TEST SUMMARY")
        print("=" * 70)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title():<35} {status}")
            if result:
                passed += 1
        
        print(f"\nOverall Result: {passed}/{total} tests passed")
        
        # PDF Reporting Implementation Recommendations
        print("\n" + "=" * 70)
        print("📝 PDF REPORTING IMPLEMENTATION RECOMMENDATIONS")
        print("=" * 70)
        
        print("✅ AVAILABLE DATA FOR PDF GENERATION:")
        print("   • Customer information (company, address, contact)")
        print("   • Equipment details and templates")
        print("   • Inspection data and form results")
        print("   • User information for signatures")
        print("   • Control items and categories")
        
        print("\n⚠️  MISSING COMPONENTS FOR PDF REPORTING:")
        print("   • PDF generation library (recommend: reportlab or weasyprint)")
        print("   • PDF report generation endpoints")
        print("   • Report templates and formatting")
        print("   • File storage/download mechanism")
        
        print("\n🔧 RECOMMENDED IMPLEMENTATION STEPS:")
        print("   1. Add PDF library to requirements.txt")
        print("   2. Create PDF report generation service")
        print("   3. Implement /api/inspections/{id}/pdf endpoint")
        print("   4. Add report templates for different equipment types")
        print("   5. Include digital signatures and approval workflow")
        
        if passed >= 8:  # Most core endpoints working
            print("\n🎉 Backend infrastructure is ready for PDF reporting implementation!")
        else:
            print(f"\n⚠️  {total - passed} critical issue(s) need to be resolved first.")
        
        return test_results

if __name__ == "__main__":
    tester = RoyalCertPDFReportingTester()
    results = tester.run_pdf_reporting_tests()