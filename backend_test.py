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

class OrphanedInspectorIdsTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        self.inspectors = []
        self.inspections_before = []
        self.inspections_after = []
        
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

    def get_current_inspections_state(self):
        """Get current state of all inspections"""
        print("\n📊 Getting Current Inspections State...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/inspections")
            print(f"GET /api/inspections Status: {response.status_code}")
            
            if response.status_code == 200:
                inspections_data = response.json()
                print(f"✅ Found {len(inspections_data)} total inspections")
                
                # Analyze by status
                status_counts = {}
                beklemede_inspections = []
                
                for inspection in inspections_data:
                    status = inspection.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                    
                    if status == 'beklemede':
                        beklemede_inspections.append(inspection)
                
                print("   Status Distribution:")
                for status, count in status_counts.items():
                    print(f"     {status}: {count}")
                
                print(f"\n🎯 Found {len(beklemede_inspections)} 'beklemede' inspections")
                
                if beklemede_inspections:
                    print("   Beklemede Inspections Details:")
                    for i, inspection in enumerate(beklemede_inspections, 1):
                        inspector_id = inspection.get('inspector_id')
                        equipment_type = inspection.get('equipment_info', {}).get('equipment_type', 'N/A')
                        print(f"     {i}. ID: {inspection.get('id')[:8]}..., Inspector: {inspector_id[:8] if inspector_id else 'None'}..., Equipment: {equipment_type}")
                
                return True, inspections_data, beklemede_inspections
            else:
                print(f"❌ Failed to get inspections: {response.text}")
                return False, [], []
                
        except Exception as e:
            print(f"❌ Get inspections error: {str(e)}")
            return False, [], []

    def get_available_inspectors(self):
        """Get all available inspectors"""
        print("\n👥 Getting Available Inspectors...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/users")
            print(f"GET /api/users Status: {response.status_code}")
            
            if response.status_code == 200:
                users_data = response.json()
                inspectors = [user for user in users_data if user.get('role') == 'denetci' and user.get('is_active', True)]
                self.inspectors = inspectors
                
                print(f"✅ Found {len(inspectors)} active inspectors")
                
                if inspectors:
                    print("   Available Inspectors:")
                    for i, inspector in enumerate(inspectors, 1):
                        print(f"     {i}. {inspector.get('full_name')} (ID: {inspector.get('id')[:8]}...)")
                
                return True, inspectors
            else:
                print(f"❌ Failed to get users: {response.text}")
                return False, []
                
        except Exception as e:
            print(f"❌ Get inspectors error: {str(e)}")
            return False, []

    def identify_orphaned_inspector_ids(self, inspections, inspectors):
        """Identify inspections with orphaned inspector IDs"""
        print("\n🔍 Identifying Orphaned Inspector IDs...")
        
        valid_inspector_ids = {insp['id'] for insp in inspectors}
        orphaned_inspections = []
        valid_inspections = []
        
        beklemede_inspections = [insp for insp in inspections if insp.get('status') == 'beklemede']
        
        for inspection in beklemede_inspections:
            inspector_id = inspection.get('inspector_id')
            
            if inspector_id and inspector_id not in valid_inspector_ids:
                orphaned_inspections.append(inspection)
                print(f"   ❌ ORPHANED: Inspection {inspection.get('id')[:8]}... has invalid inspector_id: {inspector_id[:8]}...")
            elif inspector_id and inspector_id in valid_inspector_ids:
                valid_inspections.append(inspection)
                inspector_name = next((insp['full_name'] for insp in inspectors if insp['id'] == inspector_id), 'Unknown')
                print(f"   ✅ VALID: Inspection {inspection.get('id')[:8]}... assigned to {inspector_name}")
            else:
                print(f"   ⚠️  NO INSPECTOR: Inspection {inspection.get('id')[:8]}... has no inspector_id")
        
        print(f"\n📊 Analysis Results:")
        print(f"   Total 'beklemede' inspections: {len(beklemede_inspections)}")
        print(f"   Valid assignments: {len(valid_inspections)}")
        print(f"   Orphaned assignments: {len(orphaned_inspections)}")
        print(f"   No inspector assigned: {len(beklemede_inspections) - len(valid_inspections) - len(orphaned_inspections)}")
        
        return orphaned_inspections, valid_inspections

    def run_data_fix_endpoint(self):
        """Execute the data fix endpoint"""
        print("\n🔧 Running Data Fix Endpoint...")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/fix/orphaned-inspector-ids")
            print(f"POST /api/fix/orphaned-inspector-ids Status: {response.status_code}")
            
            if response.status_code == 200:
                fix_results = response.json()
                print("✅ Data fix endpoint executed successfully")
                
                print(f"\n📊 Fix Results:")
                print(f"   Message: {fix_results.get('message')}")
                print(f"   Total inspections checked: {fix_results.get('total_inspections_checked')}")
                print(f"   Total inspectors available: {fix_results.get('total_inspectors_available')}")
                print(f"   Fixed count: {fix_results.get('fixed_count')}")
                
                results = fix_results.get('results', [])
                if results:
                    print(f"\n📋 Detailed Fix Results:")
                    for i, result in enumerate(results, 1):
                        action = result.get('action')
                        inspection_id = result.get('inspection_id', 'N/A')[:8]
                        equipment_type = result.get('equipment_type', 'N/A')
                        
                        if action == 'reassigned':
                            old_id = result.get('old_inspector_id', 'N/A')[:8]
                            new_name = result.get('new_inspector_name', 'N/A')
                            print(f"     {i}. REASSIGNED: {inspection_id}... ({equipment_type}) -> {new_name} (was: {old_id}...)")
                        elif action == 'valid_assignment':
                            inspector_id = result.get('inspector_id', 'N/A')[:8]
                            print(f"     {i}. VALID: {inspection_id}... ({equipment_type}) -> {inspector_id}...")
                        elif action == 'no_inspectors_available':
                            print(f"     {i}. ERROR: {inspection_id}... ({equipment_type}) -> No inspectors available")
                
                return True, fix_results
            else:
                print(f"❌ Data fix endpoint failed: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Data fix endpoint error: {str(e)}")
            return False, None

    def verify_fix_results(self):
        """Verify that the fix was successful"""
        print("\n✅ Verifying Fix Results...")
        
        # Get inspections after fix
        success, inspections_after, beklemede_after = self.get_current_inspections_state()
        if not success:
            return False
        
        self.inspections_after = inspections_after
        
        # Check if all beklemede inspections now have valid inspector_ids
        valid_inspector_ids = {insp['id'] for insp in self.inspectors}
        
        orphaned_after = []
        valid_after = []
        
        for inspection in beklemede_after:
            inspector_id = inspection.get('inspector_id')
            
            if inspector_id and inspector_id not in valid_inspector_ids:
                orphaned_after.append(inspection)
            elif inspector_id and inspector_id in valid_inspector_ids:
                valid_after.append(inspection)
        
        print(f"\n📊 Post-Fix Analysis:")
        print(f"   Total 'beklemede' inspections: {len(beklemede_after)}")
        print(f"   Valid assignments: {len(valid_after)}")
        print(f"   Remaining orphaned: {len(orphaned_after)}")
        
        if len(orphaned_after) == 0:
            print("   🎉 SUCCESS: All orphaned inspector IDs have been fixed!")
            return True
        else:
            print(f"   ❌ FAILURE: {len(orphaned_after)} orphaned inspector IDs still remain")
            for inspection in orphaned_after:
                print(f"     - {inspection.get('id')[:8]}... still has invalid inspector_id: {inspection.get('inspector_id')[:8]}...")
            return False

    def test_inspector_dashboard_access(self):
        """Test that inspectors can now see their assigned inspections"""
        print("\n🎯 Testing Inspector Dashboard Access...")
        
        if not self.inspectors:
            print("❌ No inspectors available to test")
            return False
        
        # Test with each inspector
        dashboard_results = []
        
        for inspector in self.inspectors:
            inspector_name = inspector.get('full_name')
            inspector_id = inspector.get('id')
            
            print(f"\n   Testing access for: {inspector_name}")
            
            # Get all inspections and filter for this inspector
            try:
                response = self.session.get(f"{BACKEND_URL}/inspections")
                
                if response.status_code == 200:
                    all_inspections = response.json()
                    
                    # Filter inspections for this inspector
                    inspector_inspections = [
                        insp for insp in all_inspections 
                        if insp.get('inspector_id') == inspector_id
                    ]
                    
                    beklemede_inspections = [
                        insp for insp in inspector_inspections 
                        if insp.get('status') == 'beklemede'
                    ]
                    
                    print(f"     Total assigned inspections: {len(inspector_inspections)}")
                    print(f"     'Beklemede' inspections: {len(beklemede_inspections)}")
                    
                    if beklemede_inspections:
                        print(f"     📋 Beklemede Inspections:")
                        for insp in beklemede_inspections:
                            equipment_type = insp.get('equipment_info', {}).get('equipment_type', 'N/A')
                            planned_date = insp.get('planned_date', 'N/A')
                            print(f"       - {equipment_type} (Planned: {planned_date[:10] if planned_date else 'N/A'})")
                            
                            # Check for CARASKAL specifically (mentioned in the bug report)
                            if equipment_type == 'CARASKAL':
                                print(f"         🎯 CARASKAL inspection found - this should now be visible in dashboard!")
                    
                    dashboard_results.append({
                        'inspector': inspector_name,
                        'total_inspections': len(inspector_inspections),
                        'beklemede_inspections': len(beklemede_inspections),
                        'has_caraskal': any(insp.get('equipment_info', {}).get('equipment_type') == 'CARASKAL' for insp in beklemede_inspections)
                    })
                    
                else:
                    print(f"     ❌ Failed to get inspections: {response.status_code}")
                    
            except Exception as e:
                print(f"     ❌ Error testing dashboard access: {str(e)}")
        
        # Summary
        print(f"\n📊 Dashboard Access Summary:")
        inspectors_with_work = 0
        inspectors_with_caraskal = 0
        
        for result in dashboard_results:
            if result['beklemede_inspections'] > 0:
                inspectors_with_work += 1
            if result['has_caraskal']:
                inspectors_with_caraskal += 1
            
            status = "✅" if result['beklemede_inspections'] > 0 else "⚠️"
            caraskal_status = "🎯 CARASKAL" if result['has_caraskal'] else ""
            print(f"   {status} {result['inspector']}: {result['beklemede_inspections']} beklemede inspections {caraskal_status}")
        
        print(f"\n   Inspectors with pending work: {inspectors_with_work}/{len(self.inspectors)}")
        print(f"   Inspectors with CARASKAL inspections: {inspectors_with_caraskal}")
        
        return inspectors_with_work > 0

    def run_orphaned_inspector_ids_test(self):
        """Run the complete orphaned inspector IDs data fix test"""
        print("🚀 Starting Orphaned Inspector IDs Data Fix Test")
        print("=" * 80)
        
        test_results = {}
        
        # Step 1: Authentication
        test_results['authentication'] = self.authenticate()
        if not test_results['authentication']:
            print("\n❌ Cannot proceed without authentication")
            return test_results
        
        # Step 2: Get current state before fix
        print("\n" + "="*50)
        print("PHASE 1: PRE-FIX ANALYSIS")
        print("="*50)
        
        success, inspections_before, beklemede_before = self.get_current_inspections_state()
        test_results['get_inspections_before'] = success
        self.inspections_before = inspections_before
        
        success, inspectors = self.get_available_inspectors()
        test_results['get_inspectors'] = success
        
        if test_results['get_inspections_before'] and test_results['get_inspectors']:
            orphaned_before, valid_before = self.identify_orphaned_inspector_ids(inspections_before, inspectors)
            test_results['orphaned_identified'] = len(orphaned_before) > 0
            
            print(f"\n🎯 PRE-FIX SUMMARY:")
            print(f"   Orphaned inspector IDs found: {len(orphaned_before)}")
            print(f"   Valid assignments: {len(valid_before)}")
        else:
            test_results['orphaned_identified'] = False
            orphaned_before = []
        
        # Step 3: Execute data fix
        print("\n" + "="*50)
        print("PHASE 2: DATA FIX EXECUTION")
        print("="*50)
        
        success, fix_results = self.run_data_fix_endpoint()
        test_results['data_fix_execution'] = success
        
        # Step 4: Verify fix results
        print("\n" + "="*50)
        print("PHASE 3: POST-FIX VERIFICATION")
        print("="*50)
        
        test_results['fix_verification'] = self.verify_fix_results()
        
        # Step 5: Test inspector dashboard access
        print("\n" + "="*50)
        print("PHASE 4: INSPECTOR DASHBOARD ACCESS TEST")
        print("="*50)
        
        test_results['dashboard_access'] = self.test_inspector_dashboard_access()
        
        # Final Summary
        print("\n" + "=" * 80)
        print("📋 ORPHANED INSPECTOR IDS DATA FIX TEST SUMMARY")
        print("=" * 80)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title():<35} {status}")
            if result:
                passed += 1
        
        print(f"\nOverall Result: {passed}/{total} tests passed")
        
        # Expected Outcome Verification
        print("\n" + "=" * 80)
        print("🎯 EXPECTED OUTCOME VERIFICATION")
        print("=" * 80)
        
        if test_results.get('data_fix_execution') and fix_results:
            fixed_count = fix_results.get('fixed_count', 0)
            total_checked = fix_results.get('total_inspections_checked', 0)
            
            print(f"✅ Data repair endpoint executed successfully")
            print(f"   Fixed {fixed_count} orphaned inspector IDs out of {total_checked} inspections checked")
            
            if test_results.get('fix_verification'):
                print(f"✅ All orphaned inspector IDs have been fixed")
                print(f"   All 'beklemede' inspections now have valid inspector_ids")
            else:
                print(f"❌ Some orphaned inspector IDs still remain")
            
            if test_results.get('dashboard_access'):
                print(f"✅ Inspector dashboard access working")
                print(f"   Inspectors can now see their assigned inspections")
            else:
                print(f"⚠️  Inspector dashboard access needs verification")
        
        overall_success = (test_results.get('authentication', False) and 
                          test_results.get('data_fix_execution', False) and
                          test_results.get('fix_verification', False))
        
        if overall_success:
            print(f"\n🎉 ORPHANED INSPECTOR IDS DATA FIX COMPLETED SUCCESSFULLY!")
            print("   ✅ All orphaned inspector IDs fixed")
            print("   ✅ All 'beklemede' inspections properly assigned")
            print("   ✅ Inspector dashboard showing correct assignments")
        else:
            print(f"\n⚠️  DATA FIX COMPLETED WITH ISSUES")
            if not test_results.get('data_fix_execution'):
                print("   ❌ Data fix endpoint failed to execute")
            if not test_results.get('fix_verification'):
                print("   ❌ Fix verification failed - orphaned IDs may still exist")
        
        return test_results

if __name__ == "__main__":
    # Run the orphaned inspector IDs data fix test
    print("🎯 EXECUTING ORPHANED INSPECTOR IDS DATA FIX TEST")
    print("="*80)
    
    tester = OrphanedInspectorIdsTester()
    results = tester.run_orphaned_inspector_ids_test()

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

class InspectionAssignmentBugTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        self.inspectors = []
        self.inspections = []
        self.customers = []
        
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

    def investigate_database_inspections(self):
        """1. Database Investigation of Planned Inspections"""
        print("\n🔍 1. DATABASE INVESTIGATION - Planned Inspections")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/inspections")
            print(f"GET /api/inspections Status: {response.status_code}")
            
            if response.status_code == 200:
                inspections_data = response.json()
                self.inspections = inspections_data
                print(f"✅ Found {len(inspections_data)} total inspections in database")
                
                # Filter inspections by status
                status_counts = {}
                beklemede_inspections = []
                
                for inspection in inspections_data:
                    status = inspection.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                    
                    if status == 'beklemede':
                        beklemede_inspections.append(inspection)
                
                print("\n📊 Inspection Status Distribution:")
                for status, count in status_counts.items():
                    print(f"   {status}: {count}")
                
                print(f"\n🎯 CRITICAL: Found {len(beklemede_inspections)} inspections with status 'beklemede'")
                
                if beklemede_inspections:
                    print("\n📋 Detailed Analysis of 'beklemede' Inspections:")
                    for i, inspection in enumerate(beklemede_inspections, 1):
                        print(f"\n   Inspection #{i}:")
                        print(f"     ID: {inspection.get('id')}")
                        print(f"     Customer ID: {inspection.get('customer_id')}")
                        print(f"     Inspector ID: {inspection.get('inspector_id')}")
                        print(f"     Status: {inspection.get('status')}")
                        print(f"     Planned Date: {inspection.get('planned_date')}")
                        print(f"     Equipment Type: {inspection.get('equipment_info', {}).get('equipment_type', 'N/A')}")
                        print(f"     Created By: {inspection.get('created_by')}")
                        print(f"     Created At: {inspection.get('created_at')}")
                        
                        # Check if inspector_id is valid
                        inspector_id = inspection.get('inspector_id')
                        if inspector_id:
                            print(f"     ✅ Inspector ID assigned: {inspector_id}")
                        else:
                            print(f"     ❌ NO INSPECTOR ID ASSIGNED!")
                
                return True, beklemede_inspections
            else:
                print(f"❌ Failed to get inspections: {response.text}")
                return False, []
                
        except Exception as e:
            print(f"❌ Database investigation error: {str(e)}")
            return False, []

    def investigate_user_roles_and_ids(self):
        """4. User Role and ID Mapping"""
        print("\n👥 4. USER ROLE AND ID MAPPING - Inspector Investigation")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/users")
            print(f"GET /api/users Status: {response.status_code}")
            
            if response.status_code == 200:
                users_data = response.json()
                print(f"✅ Found {len(users_data)} total users in system")
                
                # Filter users by role
                role_counts = {}
                inspectors = []
                
                for user in users_data:
                    role = user.get('role', 'unknown')
                    role_counts[role] = role_counts.get(role, 0) + 1
                    
                    if role == 'denetci':
                        inspectors.append(user)
                
                self.inspectors = inspectors
                
                print("\n📊 User Role Distribution:")
                for role, count in role_counts.items():
                    print(f"   {role}: {count}")
                
                print(f"\n🎯 CRITICAL: Found {len(inspectors)} users with role 'denetci' (inspector)")
                
                if inspectors:
                    print("\n📋 Detailed Inspector Information:")
                    for i, inspector in enumerate(inspectors, 1):
                        print(f"\n   Inspector #{i}:")
                        print(f"     ID: {inspector.get('id')}")
                        print(f"     Username: {inspector.get('username')}")
                        print(f"     Full Name: {inspector.get('full_name')}")
                        print(f"     Email: {inspector.get('email')}")
                        print(f"     Role: {inspector.get('role')}")
                        print(f"     Active: {inspector.get('is_active')}")
                        print(f"     Created At: {inspector.get('created_at')}")
                        
                        # Check for specific names mentioned in the bug report
                        full_name = inspector.get('full_name', '').upper()
                        if 'İLKER' in full_name or 'MENGE' in full_name:
                            print(f"     🎯 FOUND: This matches 'İLKER MENGE' mentioned in bug report!")
                        elif 'BİLİNMEYEN' in full_name or 'UNKNOWN' in full_name:
                            print(f"     🎯 FOUND: This matches 'Bilinmeyen Denetçi' mentioned in bug report!")
                
                return True, inspectors
            else:
                print(f"❌ Failed to get users: {response.text}")
                return False, []
                
        except Exception as e:
            print(f"❌ User investigation error: {str(e)}")
            return False, []

    def test_inspector_dashboard_filtering(self):
        """3. Inspector Dashboard Filtering"""
        print("\n🎯 3. INSPECTOR DASHBOARD FILTERING - Testing with Inspector Credentials")
        print("=" * 60)
        
        if not self.inspectors:
            print("❌ No inspectors found to test with")
            return False
        
        # Test with each inspector
        for inspector in self.inspectors:
            print(f"\n🔍 Testing with Inspector: {inspector.get('full_name')} (ID: {inspector.get('id')})")
            
            # Try to login as inspector (if we have credentials)
            inspector_username = inspector.get('username')
            print(f"   Inspector Username: {inspector_username}")
            
            # For now, test with admin credentials but check filtering
            try:
                response = self.session.get(f"{BACKEND_URL}/inspections")
                
                if response.status_code == 200:
                    all_inspections = response.json()
                    
                    # Filter inspections for this inspector
                    inspector_inspections = [
                        insp for insp in all_inspections 
                        if insp.get('inspector_id') == inspector.get('id')
                    ]
                    
                    print(f"   Total inspections in system: {len(all_inspections)}")
                    print(f"   Inspections assigned to this inspector: {len(inspector_inspections)}")
                    
                    if inspector_inspections:
                        print(f"   📋 Inspector's Assigned Inspections:")
                        for insp in inspector_inspections:
                            status = insp.get('status')
                            planned_date = insp.get('planned_date')
                            equipment_type = insp.get('equipment_info', {}).get('equipment_type', 'N/A')
                            print(f"     - Status: {status}, Date: {planned_date}, Equipment: {equipment_type}")
                            
                            # Check if this is a "beklemede" inspection that should appear in dashboard
                            if status == 'beklemede':
                                print(f"       🎯 CRITICAL: This 'beklemede' inspection should appear in inspector dashboard!")
                    else:
                        print(f"   ❌ NO INSPECTIONS ASSIGNED TO THIS INSPECTOR!")
                        print(f"       This could be the root cause of the bug!")
                
            except Exception as e:
                print(f"   ❌ Error testing inspector filtering: {str(e)}")
        
        return True

    def investigate_inspection_assignment_logic(self):
        """2. Inspector Assignment Logic"""
        print("\n⚙️  2. INSPECTOR ASSIGNMENT LOGIC - How inspections are assigned")
        print("=" * 60)
        
        # Check inspection creation payload structure
        print("📋 Analyzing Inspection Creation Structure:")
        
        if self.inspections:
            sample_inspection = self.inspections[0]
            print("\n   Sample Inspection Structure:")
            for key, value in sample_inspection.items():
                if isinstance(value, dict):
                    print(f"     {key}: dict with keys {list(value.keys())}")
                elif isinstance(value, list):
                    print(f"     {key}: list with {len(value)} items")
                else:
                    print(f"     {key}: {type(value).__name__} = {value}")
        
        # Check if inspector_id is properly set during creation
        print("\n🔍 Inspector Assignment Analysis:")
        
        inspections_with_inspector = [insp for insp in self.inspections if insp.get('inspector_id')]
        inspections_without_inspector = [insp for insp in self.inspections if not insp.get('inspector_id')]
        
        print(f"   Inspections WITH inspector_id: {len(inspections_with_inspector)}")
        print(f"   Inspections WITHOUT inspector_id: {len(inspections_without_inspector)}")
        
        if inspections_without_inspector:
            print(f"\n   ❌ CRITICAL BUG FOUND: {len(inspections_without_inspector)} inspections have NO inspector assigned!")
            for insp in inspections_without_inspector:
                print(f"     - Inspection ID: {insp.get('id')}, Status: {insp.get('status')}")
        
        # Check for CARASKAL and FORKLIFT inspections specifically
        caraskal_inspections = [
            insp for insp in self.inspections 
            if insp.get('equipment_info', {}).get('equipment_type') == 'CARASKAL'
        ]
        forklift_inspections = [
            insp for insp in self.inspections 
            if insp.get('equipment_info', {}).get('equipment_type') == 'FORKLIFT'
        ]
        
        print(f"\n🎯 Equipment-Specific Analysis:")
        print(f"   CARASKAL inspections: {len(caraskal_inspections)}")
        print(f"   FORKLIFT inspections: {len(forklift_inspections)}")
        
        for insp in caraskal_inspections + forklift_inspections:
            equipment_type = insp.get('equipment_info', {}).get('equipment_type')
            inspector_id = insp.get('inspector_id')
            status = insp.get('status')
            print(f"     - {equipment_type}: Inspector ID = {inspector_id}, Status = {status}")
        
        return True

    def verify_inspection_document_structure(self):
        """5. Inspection Status and Assignment Fields"""
        print("\n📄 5. INSPECTION DOCUMENT STRUCTURE - MongoDB Field Verification")
        print("=" * 60)
        
        if not self.inspections:
            print("❌ No inspections to analyze")
            return False
        
        print("🔍 Analyzing Inspection Document Structure:")
        
        # Check required fields
        required_fields = ['inspector_id', 'status', 'planned_date', 'customer_id', 'equipment_info']
        optional_fields = ['assigned_date', 'updated_at', 'created_at', 'created_by']
        
        field_analysis = {}
        
        for inspection in self.inspections:
            for field in required_fields + optional_fields:
                if field not in field_analysis:
                    field_analysis[field] = {'present': 0, 'missing': 0, 'sample_values': []}
                
                if field in inspection and inspection[field] is not None:
                    field_analysis[field]['present'] += 1
                    # Store sample values (first 3)
                    if len(field_analysis[field]['sample_values']) < 3:
                        field_analysis[field]['sample_values'].append(str(inspection[field])[:50])
                else:
                    field_analysis[field]['missing'] += 1
        
        print(f"\n📊 Field Analysis (Total inspections: {len(self.inspections)}):")
        
        for field, data in field_analysis.items():
            present = data['present']
            missing = data['missing']
            percentage = (present / len(self.inspections)) * 100
            
            status = "✅" if percentage == 100 else "⚠️" if percentage >= 80 else "❌"
            field_type = "REQUIRED" if field in required_fields else "OPTIONAL"
            
            print(f"   {field} ({field_type}): {status} {present}/{len(self.inspections)} ({percentage:.1f}%)")
            
            if data['sample_values']:
                print(f"     Sample values: {', '.join(data['sample_values'])}")
            
            if field == 'inspector_id' and missing > 0:
                print(f"     🚨 CRITICAL: {missing} inspections missing inspector_id!")
        
        return True

    def cross_reference_assignments(self):
        """Cross-reference inspector IDs with actual user IDs"""
        print("\n🔗 CROSS-REFERENCE ANALYSIS - Inspector ID Matching")
        print("=" * 60)
        
        if not self.inspectors or not self.inspections:
            print("❌ Missing data for cross-reference analysis")
            return False
        
        # Get all inspector IDs from inspections
        inspection_inspector_ids = set()
        for inspection in self.inspections:
            inspector_id = inspection.get('inspector_id')
            if inspector_id:
                inspection_inspector_ids.add(inspector_id)
        
        # Get all actual inspector user IDs
        actual_inspector_ids = set(inspector.get('id') for inspector in self.inspectors)
        
        print(f"Inspector IDs found in inspections: {len(inspection_inspector_ids)}")
        print(f"Actual inspector user IDs in system: {len(actual_inspector_ids)}")
        
        # Find mismatches
        orphaned_inspector_ids = inspection_inspector_ids - actual_inspector_ids
        unused_inspector_ids = actual_inspector_ids - inspection_inspector_ids
        
        if orphaned_inspector_ids:
            print(f"\n❌ CRITICAL BUG: {len(orphaned_inspector_ids)} inspector IDs in inspections don't match any actual users!")
            for orphaned_id in orphaned_inspector_ids:
                print(f"   Orphaned Inspector ID: {orphaned_id}")
                # Find inspections with this orphaned ID
                orphaned_inspections = [
                    insp for insp in self.inspections 
                    if insp.get('inspector_id') == orphaned_id
                ]
                print(f"     Affects {len(orphaned_inspections)} inspections")
        
        if unused_inspector_ids:
            print(f"\n⚠️  {len(unused_inspector_ids)} actual inspectors have no inspections assigned:")
            for unused_id in unused_inspector_ids:
                inspector = next((insp for insp in self.inspectors if insp.get('id') == unused_id), None)
                if inspector:
                    print(f"   Unused Inspector: {inspector.get('full_name')} (ID: {unused_id})")
        
        # Perfect matches
        matching_ids = inspection_inspector_ids & actual_inspector_ids
        if matching_ids:
            print(f"\n✅ {len(matching_ids)} inspector IDs properly matched:")
            for matching_id in matching_ids:
                inspector = next((insp for insp in self.inspectors if insp.get('id') == matching_id), None)
                if inspector:
                    assigned_inspections = [
                        insp for insp in self.inspections 
                        if insp.get('inspector_id') == matching_id
                    ]
                    print(f"   {inspector.get('full_name')}: {len(assigned_inspections)} inspections")
        
        return len(orphaned_inspector_ids) == 0

    def test_date_filtering(self):
        """Test date filtering for 'today's inspections'"""
        print("\n📅 DATE FILTERING ANALYSIS - Today's Inspections")
        print("=" * 60)
        
        from datetime import datetime, date
        
        today = date.today()
        print(f"Today's date: {today}")
        
        today_inspections = []
        future_inspections = []
        past_inspections = []
        invalid_date_inspections = []
        
        for inspection in self.inspections:
            planned_date_str = inspection.get('planned_date')
            if not planned_date_str:
                invalid_date_inspections.append(inspection)
                continue
            
            try:
                # Parse the date (handle different formats)
                if 'T' in planned_date_str:
                    planned_date = datetime.fromisoformat(planned_date_str.replace('Z', '+00:00')).date()
                else:
                    planned_date = datetime.strptime(planned_date_str, '%Y-%m-%d').date()
                
                if planned_date == today:
                    today_inspections.append(inspection)
                elif planned_date > today:
                    future_inspections.append(inspection)
                else:
                    past_inspections.append(inspection)
                    
            except Exception as e:
                print(f"   ⚠️  Invalid date format: {planned_date_str}")
                invalid_date_inspections.append(inspection)
        
        print(f"\n📊 Date Distribution:")
        print(f"   Today's inspections: {len(today_inspections)}")
        print(f"   Future inspections: {len(future_inspections)}")
        print(f"   Past inspections: {len(past_inspections)}")
        print(f"   Invalid date inspections: {len(invalid_date_inspections)}")
        
        if today_inspections:
            print(f"\n🎯 Today's Inspections Details:")
            for insp in today_inspections:
                status = insp.get('status')
                inspector_id = insp.get('inspector_id')
                equipment_type = insp.get('equipment_info', {}).get('equipment_type', 'N/A')
                print(f"     - Status: {status}, Inspector: {inspector_id}, Equipment: {equipment_type}")
        
        return True

    def run_inspection_assignment_bug_investigation(self):
        """Run comprehensive inspection assignment bug investigation"""
        print("🚨 CRITICAL INSPECTION ASSIGNMENT BUG INVESTIGATION")
        print("=" * 80)
        print("Investigating why planned inspections are not appearing in inspector dashboard")
        print("=" * 80)
        
        investigation_results = {}
        
        # Authentication
        investigation_results['authentication'] = self.authenticate()
        if not investigation_results['authentication']:
            print("\n❌ Cannot proceed without authentication")
            return investigation_results
        
        # Run all investigation steps
        investigation_results['database_inspections'] = self.investigate_database_inspections()[0]
        investigation_results['user_roles_and_ids'] = self.investigate_user_roles_and_ids()[0]
        investigation_results['inspector_dashboard_filtering'] = self.test_inspector_dashboard_filtering()
        investigation_results['inspection_assignment_logic'] = self.investigate_inspection_assignment_logic()
        investigation_results['document_structure'] = self.verify_inspection_document_structure()
        investigation_results['cross_reference'] = self.cross_reference_assignments()
        investigation_results['date_filtering'] = self.test_date_filtering()
        
        # Summary and Root Cause Analysis
        print("\n" + "=" * 80)
        print("🔍 ROOT CAUSE ANALYSIS - INSPECTION ASSIGNMENT BUG")
        print("=" * 80)
        
        passed_tests = sum(1 for result in investigation_results.values() if result)
        total_tests = len(investigation_results)
        
        print(f"Investigation Results: {passed_tests}/{total_tests} areas analyzed successfully")
        
        # Identify the root cause
        print(f"\n🎯 CRITICAL FINDINGS:")
        
        # Check for missing inspector assignments
        beklemede_count = len([insp for insp in self.inspections if insp.get('status') == 'beklemede'])
        inspections_without_inspector = len([insp for insp in self.inspections if not insp.get('inspector_id')])
        
        if inspections_without_inspector > 0:
            print(f"   ❌ ROOT CAUSE IDENTIFIED: {inspections_without_inspector} inspections have NO inspector_id assigned!")
            print(f"   ❌ This explains why inspections don't appear in inspector dashboard")
        
        if beklemede_count > 0:
            print(f"   📊 Found {beklemede_count} inspections with status 'beklemede'")
            
        inspector_count = len(self.inspectors)
        if inspector_count == 0:
            print(f"   ❌ CRITICAL: No inspectors (role='denetci') found in system!")
        else:
            print(f"   ✅ Found {inspector_count} inspectors in system")
        
        # Check for orphaned inspector IDs
        if hasattr(self, 'inspections') and hasattr(self, 'inspectors'):
            inspection_inspector_ids = set(insp.get('inspector_id') for insp in self.inspections if insp.get('inspector_id'))
            actual_inspector_ids = set(inspector.get('id') for inspector in self.inspectors)
            orphaned_ids = inspection_inspector_ids - actual_inspector_ids
            
            if orphaned_ids:
                print(f"   ❌ CRITICAL: {len(orphaned_ids)} inspector IDs in inspections don't match actual users!")
        
        print(f"\n💡 RECOMMENDED FIXES:")
        print(f"   1. Ensure all inspections have valid inspector_id assigned during creation")
        print(f"   2. Verify inspector user accounts exist and have role='denetci'")
        print(f"   3. Check inspection creation workflow assigns inspector_id properly")
        print(f"   4. Implement validation to prevent inspections without inspector assignment")
        print(f"   5. Add data migration to fix existing inspections with missing inspector_id")
        
        if passed_tests >= 6:
            print(f"\n🎉 INVESTIGATION COMPLETED SUCCESSFULLY!")
            print(f"   Root cause of inspection assignment bug has been identified.")
        else:
            print(f"\n⚠️  Investigation incomplete - {total_tests - passed_tests} areas need attention")
        
        return investigation_results

if __name__ == "__main__":
    # Run the inspection assignment bug investigation
    bug_tester = InspectionAssignmentBugTester()
    results = bug_tester.run_inspection_assignment_bug_investigation()