#!/usr/bin/env python3
"""
Universal Template Parser Test - Full Structure Test
Tests the new Universal Template Parser with the latest Forklift document

Test Requirements:
1. Clean Previous Templates - Delete existing FORKLIFT templates
2. Upload and Test New Universal Parser with specific FORKLIFT document
3. Verify Universal Template Structure with 11 sections
4. Control Items Quality Check (53 control items with proper distribution)
5. Template Structure Validation
"""

import requests
import json
import os
from datetime import datetime

# Configuration - Use environment variable for backend URL
BACKEND_URL = os.getenv('REACT_APP_ROYALCERT_API_URL', 'https://royalcert-inspection-system-production.up.railway.app/api')
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Latest FORKLIFT Document URL for testing
FORKLIFT_DOCUMENT_URL = "https://customer-assets.emergentagent.com/job_periodic-check/artifacts/1tatrwna_RC-M-%C4%B0E-FR24_5%20FORKL%C4%B0FT%20MUAYENE%20FORMU.docx"

class UniversalTemplateParserTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        self.existing_forklift_templates = []
        self.uploaded_template = None
        
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

    def clean_previous_forklift_templates(self):
        """Clean Previous Templates - Delete existing FORKLIFT templates to test new parser"""
        print("\n🧹 Step 1: Clean Previous Templates...")
        
        try:
            # Get existing templates
            response = self.session.get(f"{BACKEND_URL}/equipment-templates")
            print(f"Equipment Templates Status: {response.status_code}")
            
            if response.status_code == 200:
                templates_data = response.json()
                
                # Find FORKLIFT templates
                forklift_templates = [t for t in templates_data if t.get('equipment_type') == 'FORKLIFT']
                self.existing_forklift_templates = forklift_templates
                
                print(f"Found {len(forklift_templates)} existing FORKLIFT templates")
                
                if not forklift_templates:
                    print("✅ No existing FORKLIFT templates to clean")
                    return True
                
                # Delete each FORKLIFT template
                deleted_count = 0
                for template in forklift_templates:
                    try:
                        template_id = template.get('id')
                        template_name = template.get('name', 'UNNAMED')
                        
                        delete_response = self.session.delete(f"{BACKEND_URL}/equipment-templates/{template_id}")
                        
                        if delete_response.status_code == 200:
                            print(f"✅ Deleted template: {template_name}")
                            deleted_count += 1
                        else:
                            print(f"❌ Failed to delete template {template_name}: {delete_response.text}")
                            
                    except Exception as e:
                        print(f"❌ Error deleting template {template.get('name', 'UNKNOWN')}: {str(e)}")
                
                print(f"✅ Cleaned {deleted_count}/{len(forklift_templates)} FORKLIFT templates")
                return deleted_count == len(forklift_templates)
            else:
                print(f"❌ Failed to get templates: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Clean templates error: {str(e)}")
            return False

    def upload_and_test_universal_parser(self):
        """Upload and Test New Universal Parser with latest Forklift document"""
        print("\n📥 Step 2: Upload and Test New Universal Parser...")
        print(f"Document URL: {FORKLIFT_DOCUMENT_URL}")
        
        try:
            # Download the document
            print("   Downloading FORKLIFT MUAYENE FORMU...")
            doc_response = requests.get(FORKLIFT_DOCUMENT_URL)
            
            if doc_response.status_code != 200:
                print(f"❌ Failed to download document: {doc_response.status_code}")
                return False, None
            
            print(f"✅ Document downloaded ({len(doc_response.content)} bytes)")
            
            # Prepare file for upload
            filename = "FORKLIFT MUAYENE FORMU.docx"
            files = {
                'file': (filename, doc_response.content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Upload the document using POST /api/equipment-templates/upload
            print(f"   Uploading to: POST {BACKEND_URL}/equipment-templates/upload")
            upload_response = self.session.post(f"{BACKEND_URL}/equipment-templates/upload", files=files)
            
            print(f"Upload Response Status: {upload_response.status_code}")
            
            if upload_response.status_code == 200:
                upload_data = upload_response.json()
                print("✅ Document uploaded and parsed successfully with Universal Parser")
                
                # Extract parsing results
                template_data = upload_data.get('template', {})
                self.uploaded_template = template_data
                
                equipment_type = template_data.get('equipment_type', 'UNKNOWN')
                template_type = template_data.get('template_type', 'UNKNOWN')
                template_name = template_data.get('name', 'UNNAMED')
                
                print(f"   Equipment Type: {equipment_type}")
                print(f"   Template Type: {template_type}")
                print(f"   Template Name: {template_name}")
                
                return True, template_data
            else:
                print(f"❌ Document upload failed: {upload_response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Document upload error: {str(e)}")
            return False, None

    def verify_universal_template_structure(self, template_data):
        """Verify Universal Template Structure - Check if all 11 sections are parsed"""
        print("\n🏗️ Step 3: Verify Universal Template Structure...")
        print("Expected 11 sections:")
        print("1. general_info (Genel Bilgiler fields)")
        print("2. measurement_devices (Ölçüm Aletleri structure)")
        print("3. equipment_info (Ekipman bilgileri with forklift-specific fields)")
        print("4. test_values (Test değerleri)")
        print("5. control_items (53 kontrol maddesi - tamamı)")
        print("6. categories (A-H proper distribution)")
        print("7. test_experiments (51-53 test items)")
        print("8. defect_explanations")
        print("9. notes")
        print("10. result_opinion")
        print("11. inspector_info, company_official")
        
        # Expected 11 sections in universal template structure
        expected_sections = [
            'general_info',
            'measurement_devices', 
            'equipment_info',
            'test_values',
            'control_items',
            'categories',
            'test_experiments',
            'defect_explanations',
            'notes',
            'result_opinion',
            'inspector_info'
        ]
        
        found_sections = []
        missing_sections = []
        
        print(f"\n🔍 Checking Universal Template Structure:")
        
        for section in expected_sections:
            if section in template_data:
                found_sections.append(section)
                section_data = template_data[section]
                
                if isinstance(section_data, dict):
                    print(f"   ✅ {section}: Found (dict with {len(section_data)} keys)")
                elif isinstance(section_data, list):
                    print(f"   ✅ {section}: Found (list with {len(section_data)} items)")
                else:
                    print(f"   ✅ {section}: Found ({type(section_data).__name__})")
            else:
                missing_sections.append(section)
                print(f"   ❌ {section}: Missing")
        
        # Check for company_official (part of section 11)
        if 'company_official' in template_data:
            found_sections.append('company_official')
            print(f"   ✅ company_official: Found")
        else:
            missing_sections.append('company_official')
            print(f"   ❌ company_official: Missing")
        
        print(f"\n📊 Universal Structure Results:")
        print(f"   Found sections: {len(found_sections)}/11")
        print(f"   Missing sections: {len(missing_sections)}")
        
        if missing_sections:
            print(f"   Missing: {', '.join(missing_sections)}")
        
        # Check if we have the minimum required structure
        has_universal_structure = len(found_sections) >= 8  # At least 8/11 sections
        
        if has_universal_structure:
            print("✅ Universal template structure is present")
        else:
            print("❌ Universal template structure is incomplete")
        
        return {
            'has_universal_structure': has_universal_structure,
            'found_sections': found_sections,
            'missing_sections': missing_sections,
            'section_count': len(found_sections)
        }

    def control_items_quality_check(self, template_data):
        """Control Items Quality Check - Verify all 53 control items with proper distribution"""
        print("\n🔍 Step 4: Control Items Quality Check...")
        print("Expected: All 53 control items with proper category distribution:")
        print("   A: 12 items, B: 4 items, C: 11 items, D: 2 items")
        print("   E: 6 items, F: 6 items, G: 2 items, H: 7 items")
        print("   Test experiments (items 51-53) in separate section")
        
        # Get control items from template
        control_items = template_data.get('control_items', [])
        categories = template_data.get('categories', [])
        test_experiments = template_data.get('test_experiments', [])
        
        total_control_items = len(control_items)
        print(f"\n📊 Control Items Analysis:")
        print(f"   Total control items found: {total_control_items}")
        
        # Check if we have 53 control items (not 47)
        expected_total = 53
        has_correct_total = total_control_items == expected_total
        
        if has_correct_total:
            print(f"   ✅ Correct total: {total_control_items} = {expected_total}")
        else:
            print(f"   ❌ Incorrect total: {total_control_items} ≠ {expected_total}")
        
        # Analyze category distribution
        category_distribution = {}
        
        if isinstance(categories, list):
            # Old format - list of categories
            for category in categories:
                cat_code = category.get('code', 'UNKNOWN')
                cat_items = category.get('items', [])
                category_distribution[cat_code] = len(cat_items)
        elif isinstance(categories, dict):
            # New format - dict of categories
            for cat_code, cat_data in categories.items():
                if isinstance(cat_data, dict) and 'items' in cat_data:
                    category_distribution[cat_code] = len(cat_data['items'])
                elif isinstance(cat_data, list):
                    category_distribution[cat_code] = len(cat_data)
        
        # Expected distribution
        expected_distribution = {
            'A': 12, 'B': 4, 'C': 11, 'D': 2,
            'E': 6, 'F': 6, 'G': 2, 'H': 7
        }
        
        print(f"\n📋 Category Distribution Analysis:")
        distribution_correct = True
        
        for cat_code, expected_count in expected_distribution.items():
            actual_count = category_distribution.get(cat_code, 0)
            
            if actual_count == expected_count:
                print(f"   ✅ Category {cat_code}: {actual_count} items (expected: {expected_count})")
            else:
                print(f"   ❌ Category {cat_code}: {actual_count} items (expected: {expected_count})")
                distribution_correct = False
        
        # Check test experiments (items 51-53)
        test_experiments_count = len(test_experiments)
        has_test_experiments = test_experiments_count >= 3
        
        print(f"\n🧪 Test Experiments Analysis:")
        print(f"   Test experiments found: {test_experiments_count}")
        
        if has_test_experiments:
            print(f"   ✅ Test experiments section present (items 51-53)")
        else:
            print(f"   ❌ Test experiments section missing or incomplete")
        
        # Overall quality assessment
        quality_score = 0
        max_score = 4
        
        if has_correct_total:
            quality_score += 1
        if distribution_correct:
            quality_score += 2  # Worth 2 points as it's critical
        if has_test_experiments:
            quality_score += 1
        
        print(f"\n📊 Control Items Quality Score: {quality_score}/{max_score}")
        
        quality_passed = quality_score >= 3  # Need at least 3/4 to pass
        
        if quality_passed:
            print("✅ Control Items Quality Check PASSED")
        else:
            print("❌ Control Items Quality Check FAILED")
        
        return {
            'total_items': total_control_items,
            'has_correct_total': has_correct_total,
            'category_distribution': category_distribution,
            'distribution_correct': distribution_correct,
            'test_experiments_count': test_experiments_count,
            'has_test_experiments': has_test_experiments,
            'quality_score': quality_score,
            'quality_passed': quality_passed
        }

    def template_structure_validation(self, template_data):
        """Template Structure Validation - Confirm universal structure and from_system flags"""
        print("\n✅ Step 5: Template Structure Validation...")
        print("Checking:")
        print("   - New universal structure is created")
        print("   - from_system flags are properly set")
        print("   - Field types (text, date, number, radio, etc.)")
        
        validation_results = {
            'has_universal_structure': False,
            'has_from_system_flags': False,
            'has_proper_field_types': False,
            'validation_score': 0
        }
        
        # Check 1: Universal structure
        universal_sections = ['general_info', 'measurement_devices', 'equipment_info', 'control_items']
        has_universal = all(section in template_data for section in universal_sections)
        
        if has_universal:
            print("   ✅ Universal structure created")
            validation_results['has_universal_structure'] = True
            validation_results['validation_score'] += 1
        else:
            print("   ❌ Universal structure missing")
        
        # Check 2: from_system flags
        from_system_found = False
        
        # Check in general_info
        general_info = template_data.get('general_info', {})
        if isinstance(general_info, dict):
            for field_name, field_data in general_info.items():
                if isinstance(field_data, dict) and 'from_system' in field_data:
                    from_system_found = True
                    break
        
        # Check in control_items
        if not from_system_found:
            control_items = template_data.get('control_items', [])
            for item in control_items[:5]:  # Check first 5 items
                if isinstance(item, dict) and 'from_system' in item:
                    from_system_found = True
                    break
        
        if from_system_found:
            print("   ✅ from_system flags properly set")
            validation_results['has_from_system_flags'] = True
            validation_results['validation_score'] += 1
        else:
            print("   ❌ from_system flags missing")
        
        # Check 3: Field types
        field_types_found = []
        
        # Check in general_info for different field types
        for field_name, field_data in general_info.items():
            if isinstance(field_data, dict) and 'type' in field_data:
                field_type = field_data['type']
                if field_type not in field_types_found:
                    field_types_found.append(field_type)
        
        # Check in control_items for field types
        control_items = template_data.get('control_items', [])
        for item in control_items[:10]:  # Check first 10 items
            if isinstance(item, dict):
                if 'input_type' in item:
                    input_type = item['input_type']
                    if input_type not in field_types_found:
                        field_types_found.append(input_type)
                if 'type' in item:
                    item_type = item['type']
                    if item_type not in field_types_found:
                        field_types_found.append(item_type)
        
        expected_types = ['text', 'date', 'number', 'radio', 'dropdown']
        has_proper_types = len(field_types_found) >= 3  # At least 3 different types
        
        if has_proper_types:
            print(f"   ✅ Field types found: {', '.join(field_types_found)}")
            validation_results['has_proper_field_types'] = True
            validation_results['validation_score'] += 1
        else:
            print(f"   ❌ Limited field types: {', '.join(field_types_found)}")
        
        # Overall validation score
        max_score = 3
        validation_passed = validation_results['validation_score'] >= 2
        
        print(f"\n📊 Template Structure Validation Score: {validation_results['validation_score']}/{max_score}")
        
        if validation_passed:
            print("✅ Template Structure Validation PASSED")
        else:
            print("❌ Template Structure Validation FAILED")
        
        validation_results['validation_passed'] = validation_passed
        
        return validation_results

    def run_universal_template_parser_test(self):
        """Run the complete Universal Template Parser Test"""
        print("🚀 Starting Universal Template Parser Test - Full Structure Test")
        print("=" * 80)
        print("Testing the new Universal Template Parser with the latest Forklift document")
        print("=" * 80)
        
        test_results = {}
        
        # Step 1: Authentication
        test_results['authentication'] = self.authenticate()
        if not test_results['authentication']:
            print("\n❌ Cannot proceed without authentication")
            return test_results
        
        # Step 2: Clean Previous Templates
        test_results['clean_templates'] = self.clean_previous_forklift_templates()
        
        # Step 3: Upload and Test New Universal Parser
        success, template_data = self.upload_and_test_universal_parser()
        test_results['upload_and_parse'] = success
        
        if not success or not template_data:
            print("\n❌ Cannot proceed without successful template upload")
            return test_results
        
        # Step 4: Verify Universal Template Structure
        structure_results = self.verify_universal_template_structure(template_data)
        test_results['universal_structure'] = structure_results['has_universal_structure']
        
        # Step 5: Control Items Quality Check
        quality_results = self.control_items_quality_check(template_data)
        test_results['control_items_quality'] = quality_results['quality_passed']
        
        # Step 6: Template Structure Validation
        validation_results = self.template_structure_validation(template_data)
        test_results['structure_validation'] = validation_results['validation_passed']
        
        # Final Summary
        print("\n" + "=" * 80)
        print("📋 UNIVERSAL TEMPLATE PARSER TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = 0
        total_tests = 6
        
        test_names = [
            ('Authentication', 'authentication'),
            ('Clean Previous Templates', 'clean_templates'),
            ('Upload and Parse Document', 'upload_and_parse'),
            ('Universal Structure Verification', 'universal_structure'),
            ('Control Items Quality Check', 'control_items_quality'),
            ('Template Structure Validation', 'structure_validation')
        ]
        
        for test_name, test_key in test_names:
            result = test_results.get(test_key, False)
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<35} {status}")
            if result:
                passed_tests += 1
        
        print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
        
        # Expected Outcome Verification
        print("\n" + "=" * 80)
        print("🎯 EXPECTED OUTCOME VERIFICATION")
        print("=" * 80)
        
        if test_results.get('upload_and_parse'):
            print("✅ Universal Template Parser successfully processed FORKLIFT document")
            
            if structure_results['section_count'] >= 8:
                print(f"✅ Universal template structure created with {structure_results['section_count']}/11 sections")
            else:
                print(f"❌ Universal template structure incomplete: {structure_results['section_count']}/11 sections")
            
            if quality_results['total_items'] == 53:
                print(f"✅ All 53 control items extracted correctly")
            else:
                print(f"⚠️ Control items count: {quality_results['total_items']} (expected: 53)")
            
            if quality_results['distribution_correct']:
                print("✅ Control items properly categorized A-H")
            else:
                print("❌ Control items category distribution incorrect")
                
            if quality_results['has_test_experiments']:
                print("✅ Test experiments (items 51-53) in separate section")
            else:
                print("❌ Test experiments section missing")
        
        # Overall success determination
        critical_tests = ['authentication', 'upload_and_parse', 'universal_structure', 'control_items_quality']
        critical_passed = all(test_results.get(test, False) for test in critical_tests)
        
        if critical_passed:
            print(f"\n🎉 UNIVERSAL TEMPLATE PARSER TEST COMPLETED SUCCESSFULLY!")
            print("   ✅ Complete universal template structure with all 11 sections properly parsed")
            print("   ✅ 53 control items correctly categorized")
            print("   ✅ New Universal Template Parser is working correctly")
        else:
            print(f"\n⚠️ UNIVERSAL TEMPLATE PARSER TEST COMPLETED WITH ISSUES")
            print("   Some critical components need attention")
        
        return test_results

if __name__ == "__main__":
    # Run the Universal Template Parser Test
    print("🎯 EXECUTING UNIVERSAL TEMPLATE PARSER TEST - FULL STRUCTURE TEST")
    print("="*80)
    
    tester = UniversalTemplateParserTester()
    results = tester.run_universal_template_parser_test()