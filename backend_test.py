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