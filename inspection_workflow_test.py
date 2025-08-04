#!/usr/bin/env python3
"""
Critical Inspection Workflow Testing for RoyalCert System
Focus: Testing critical workflow problems in the inspection system

Issues to test:
1. Inspector Assignment Visibility Issue
2. Inspection Status Workflow Problems  
3. Technical Manager Report Queue Missing
4. Duplicate Inspection Prevention Issue
5. Database Investigation
"""

import requests
import json
from datetime import datetime, timedelta
import uuid

# Configuration
BACKEND_URL = "https://405a5b7a-3c02-4793-9fcc-5203d2944620.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class InspectionWorkflowTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user = None
        self.inspector_token = None
        self.inspector_user = None
        self.tech_manager_token = None
        self.tech_manager_user = None
        self.test_customer_id = None
        self.test_inspections = []
        
    def authenticate_admin(self):
        """Authenticate with admin credentials"""
        print("🔐 Authenticating as Admin...")
        
        login_data = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            print(f"Admin Login Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.admin_user = data["user"]
                print(f"✅ Admin authentication successful: {self.admin_user['full_name']}")
                return True
            else:
                print(f"❌ Admin authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Admin authentication error: {str(e)}")
            return False

    def setup_test_users(self):
        """Create test inspector and technical manager users"""
        print("\n👥 Setting up test users...")
        
        # Set admin authorization
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create test inspector
        inspector_data = {
            "username": "test_inspector",
            "email": "inspector@test.com",
            "full_name": "Test Inspector",
            "password": "test123",
            "role": "denetci"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=inspector_data, headers=headers)
            if response.status_code == 200:
                print("✅ Test inspector created")
            elif "already registered" in response.text:
                print("ℹ️  Test inspector already exists")
            else:
                print(f"⚠️  Inspector creation issue: {response.text}")
        except Exception as e:
            print(f"⚠️  Inspector creation error: {str(e)}")
        
        # Create test technical manager
        tech_manager_data = {
            "username": "test_tech_manager",
            "email": "techmanager@test.com", 
            "full_name": "Test Technical Manager",
            "password": "test123",
            "role": "teknik_yonetici"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=tech_manager_data, headers=headers)
            if response.status_code == 200:
                print("✅ Test technical manager created")
            elif "already registered" in response.text:
                print("ℹ️  Test technical manager already exists")
            else:
                print(f"⚠️  Tech manager creation issue: {response.text}")
        except Exception as e:
            print(f"⚠️  Tech manager creation error: {str(e)}")
        
        return True

    def authenticate_inspector(self):
        """Authenticate as test inspector"""
        print("\n🔐 Authenticating as Inspector...")
        
        login_data = {
            "username": "test_inspector",
            "password": "test123"
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
            print(f"Inspector Login Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.inspector_token = data["access_token"]
                self.inspector_user = data["user"]
                print(f"✅ Inspector authentication successful: {self.inspector_user['full_name']}")
                return True
            else:
                print(f"❌ Inspector authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Inspector authentication error: {str(e)}")
            return False

    def authenticate_tech_manager(self):
        """Authenticate as test technical manager"""
        print("\n🔐 Authenticating as Technical Manager...")
        
        login_data = {
            "username": "test_tech_manager",
            "password": "test123"
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
            print(f"Tech Manager Login Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.tech_manager_token = data["access_token"]
                self.tech_manager_user = data["user"]
                print(f"✅ Tech Manager authentication successful: {self.tech_manager_user['full_name']}")
                return True
            else:
                print(f"❌ Tech Manager authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Tech Manager authentication error: {str(e)}")
            return False

    def setup_test_customer(self):
        """Create a test customer for inspections"""
        print("\n🏢 Setting up test customer...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        customer_data = {
            "company_name": "Test Company Ltd",
            "contact_person": "John Doe",
            "phone": "+90 555 123 4567",
            "email": "contact@testcompany.com",
            "address": "Test Address, Istanbul, Turkey",
            "equipments": [
                {
                    "equipment_type": "CARASKAL",
                    "serial_number": "TEST-001",
                    "manufacturer": "Test Manufacturer",
                    "model": "Test Model",
                    "capacity": "5000 kg"
                }
            ]
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/customers", json=customer_data, headers=headers)
            print(f"Customer Creation Status: {response.status_code}")
            
            if response.status_code == 200:
                customer = response.json()
                self.test_customer_id = customer['id']
                print(f"✅ Test customer created: {customer['company_name']}")
                return True
            else:
                print(f"❌ Customer creation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Customer creation error: {str(e)}")
            return False

    def test_inspector_assignment_visibility(self):
        """Test Issue 1: Inspector Assignment Visibility Issue"""
        print("\n🔍 TESTING ISSUE 1: Inspector Assignment Visibility")
        print("=" * 60)
        
        if not self.inspector_user:
            print("❌ Inspector user not available")
            return False
        
        # Create inspection assigned to test inspector
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        inspection_data = {
            "customer_id": self.test_customer_id,
            "equipment_info": {
                "equipment_type": "CARASKAL",
                "serial_number": "TEST-001",
                "manufacturer": "Test Manufacturer",
                "model": "Test Model",
                "capacity": "5000 kg"
            },
            "inspector_id": self.inspector_user['id'],
            "planned_date": (datetime.now() + timedelta(days=1)).isoformat()
        }
        
        try:
            # Create inspection as admin
            response = self.session.post(f"{BACKEND_URL}/inspections", json=inspection_data, headers=headers)
            print(f"Inspection Creation Status: {response.status_code}")
            
            if response.status_code == 200:
                inspection = response.json()
                self.test_inspections.append(inspection['id'])
                print(f"✅ Test inspection created: {inspection['id']}")
                
                # Now test if inspector can see their assigned inspections
                inspector_headers = {"Authorization": f"Bearer {self.inspector_token}"}
                
                response = requests.get(f"{BACKEND_URL}/inspections", headers=inspector_headers)
                print(f"Inspector GET /inspections Status: {response.status_code}")
                
                if response.status_code == 200:
                    inspections = response.json()
                    print(f"Inspector sees {len(inspections)} inspections")
                    
                    # Check if the assigned inspection is visible
                    assigned_inspection = next((i for i in inspections if i['id'] == inspection['id']), None)
                    
                    if assigned_inspection:
                        print("✅ PASS: Inspector can see assigned inspection")
                        print(f"   Inspection ID: {assigned_inspection['id']}")
                        print(f"   Status: {assigned_inspection['status']}")
                        print(f"   Inspector ID: {assigned_inspection['inspector_id']}")
                        
                        # Verify inspector_id matching
                        if assigned_inspection['inspector_id'] == self.inspector_user['id']:
                            print("✅ PASS: Inspector ID matching works correctly")
                            return True
                        else:
                            print(f"❌ FAIL: Inspector ID mismatch - Expected: {self.inspector_user['id']}, Got: {assigned_inspection['inspector_id']}")
                            return False
                    else:
                        print("❌ FAIL: Inspector cannot see assigned inspection")
                        print("   This indicates inspector assignment visibility issue")
                        return False
                else:
                    print(f"❌ FAIL: Inspector cannot access inspections endpoint: {response.text}")
                    return False
            else:
                print(f"❌ Failed to create test inspection: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Inspector assignment visibility test error: {str(e)}")
            return False

    def test_inspection_status_workflow(self):
        """Test Issue 2: Inspection Status Workflow Problems"""
        print("\n🔄 TESTING ISSUE 2: Inspection Status Workflow Problems")
        print("=" * 60)
        
        if not self.test_inspections:
            print("❌ No test inspections available")
            return False
        
        inspection_id = self.test_inspections[0]
        inspector_headers = {"Authorization": f"Bearer {self.inspector_token}"}
        
        try:
            # Test status transitions: beklemede -> devam_ediyor -> rapor_yazildi -> onaylandi
            print("Testing status transitions...")
            
            # 1. Check initial status (should be 'beklemede')
            response = requests.get(f"{BACKEND_URL}/inspections/{inspection_id}", headers=inspector_headers)
            if response.status_code == 200:
                inspection = response.json()
                print(f"Initial status: {inspection['status']}")
                
                if inspection['status'] != 'beklemede':
                    print(f"⚠️  Expected 'beklemede', got '{inspection['status']}'")
            
            # 2. Update status to 'devam_ediyor'
            update_data = {"status": "devam_ediyor"}
            response = requests.put(f"{BACKEND_URL}/inspections/{inspection_id}", json=update_data, headers=inspector_headers)
            print(f"Update to 'devam_ediyor' Status: {response.status_code}")
            
            if response.status_code == 200:
                inspection = response.json()
                if inspection['status'] == 'devam_ediyor':
                    print("✅ PASS: Status updated to 'devam_ediyor'")
                else:
                    print(f"❌ FAIL: Status not updated correctly, got: {inspection['status']}")
            
            # 3. Submit completed inspection (rapor_yazildi)
            form_data = {
                "form_data": {
                    "item_1": {"value": "U", "comment": "Test comment"},
                    "item_2": {"value": "UD", "comment": "Test defect"}
                },
                "general_info": {
                    "inspection_date": datetime.now().isoformat(),
                    "weather": "Clear"
                },
                "is_draft": False,
                "completion_percentage": 100
            }
            
            response = requests.put(f"{BACKEND_URL}/inspections/{inspection_id}/form", json=form_data, headers=inspector_headers)
            print(f"Submit completed form Status: {response.status_code}")
            
            if response.status_code == 200:
                # Check if status changed to 'rapor_yazildi'
                response = requests.get(f"{BACKEND_URL}/inspections/{inspection_id}", headers=inspector_headers)
                if response.status_code == 200:
                    inspection = response.json()
                    if inspection['status'] == 'rapor_yazildi':
                        print("✅ PASS: Status updated to 'rapor_yazildi' after form submission")
                        
                        # 4. Check if completed inspection still visible to inspector
                        response = requests.get(f"{BACKEND_URL}/inspections", headers=inspector_headers)
                        if response.status_code == 200:
                            inspections = response.json()
                            completed_inspection = next((i for i in inspections if i['id'] == inspection_id), None)
                            
                            if completed_inspection:
                                print("✅ PASS: Completed inspection still visible to inspector")
                                return True
                            else:
                                print("❌ FAIL: Completed inspection disappeared from inspector's view")
                                print("   This indicates the workflow problem where completed inspections disappear")
                                return False
                    else:
                        print(f"❌ FAIL: Status not updated to 'rapor_yazildi', got: {inspection['status']}")
                        return False
            else:
                print(f"❌ FAIL: Form submission failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Status workflow test error: {str(e)}")
            return False

    def test_technical_manager_report_queue(self):
        """Test Issue 3: Technical Manager Report Queue Missing"""
        print("\n📋 TESTING ISSUE 3: Technical Manager Report Queue Missing")
        print("=" * 60)
        
        if not self.tech_manager_user:
            print("❌ Technical manager user not available")
            return False
        
        tech_manager_headers = {"Authorization": f"Bearer {self.tech_manager_token}"}
        
        try:
            # 1. Test GET /api/inspections with tech manager credentials
            print("Testing inspections access for technical manager...")
            response = requests.get(f"{BACKEND_URL}/inspections", headers=tech_manager_headers)
            print(f"Tech Manager GET /inspections Status: {response.status_code}")
            
            if response.status_code == 200:
                inspections = response.json()
                print(f"Tech Manager sees {len(inspections)} inspections")
                
                # Check for inspections with status 'rapor_yazildi'
                pending_reports = [i for i in inspections if i.get('status') == 'rapor_yazildi']
                print(f"Inspections with status 'rapor_yazildi': {len(pending_reports)}")
                
                if pending_reports:
                    print("✅ PASS: Technical manager can see pending reports")
                    
                    # Test specific endpoint for pending approval
                    response = requests.get(f"{BACKEND_URL}/inspections/pending-approval", headers=tech_manager_headers)
                    print(f"GET /inspections/pending-approval Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        pending_approval = response.json()
                        print(f"Pending approval inspections: {len(pending_approval)}")
                        print("✅ PASS: Pending approval endpoint working")
                        
                        # Test approval workflow
                        if pending_approval:
                            test_inspection_id = pending_approval[0]['id']
                            approval_data = {
                                "action": "approve",
                                "notes": "Test approval"
                            }
                            
                            response = requests.post(f"{BACKEND_URL}/inspections/{test_inspection_id}/approve", 
                                                   json=approval_data, headers=tech_manager_headers)
                            print(f"Approval test Status: {response.status_code}")
                            
                            if response.status_code == 200:
                                print("✅ PASS: Report approval workflow working")
                                return True
                            else:
                                print(f"❌ FAIL: Report approval failed: {response.text}")
                                return False
                        else:
                            print("ℹ️  No pending reports to test approval workflow")
                            return True
                    else:
                        print(f"❌ FAIL: Pending approval endpoint not working: {response.text}")
                        return False
                else:
                    print("ℹ️  No pending reports found (status: rapor_yazildi)")
                    print("   This might indicate the report queue issue")
                    return False
            else:
                print(f"❌ FAIL: Technical manager cannot access inspections: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Technical manager report queue test error: {str(e)}")
            return False

    def test_duplicate_inspection_prevention(self):
        """Test Issue 4: Duplicate Inspection Prevention Issue"""
        print("\n🚫 TESTING ISSUE 4: Duplicate Inspection Prevention")
        print("=" * 60)
        
        if not self.test_customer_id or not self.inspector_user:
            print("❌ Test customer or inspector not available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create first inspection
        inspection_data = {
            "customer_id": self.test_customer_id,
            "equipment_info": {
                "equipment_type": "CARASKAL",
                "serial_number": "DUPLICATE-TEST-001",
                "manufacturer": "Test Manufacturer",
                "model": "Test Model",
                "capacity": "5000 kg"
            },
            "inspector_id": self.inspector_user['id'],
            "planned_date": (datetime.now() + timedelta(days=2)).isoformat()
        }
        
        try:
            # Create first inspection
            response = self.session.post(f"{BACKEND_URL}/inspections", json=inspection_data, headers=headers)
            print(f"First inspection creation Status: {response.status_code}")
            
            if response.status_code == 200:
                first_inspection = response.json()
                print(f"✅ First inspection created: {first_inspection['id']}")
                
                # Try to create duplicate inspection (same customer + equipment)
                response = self.session.post(f"{BACKEND_URL}/inspections", json=inspection_data, headers=headers)
                print(f"Duplicate inspection creation Status: {response.status_code}")
                
                if response.status_code == 400:
                    print("✅ PASS: Duplicate inspection prevented (400 error)")
                    print(f"   Error message: {response.text}")
                    return True
                elif response.status_code == 200:
                    duplicate_inspection = response.json()
                    print("❌ FAIL: Duplicate inspection was created")
                    print(f"   First ID: {first_inspection['id']}")
                    print(f"   Duplicate ID: {duplicate_inspection['id']}")
                    print("   This indicates duplicate prevention is not working")
                    return False
                else:
                    print(f"⚠️  Unexpected response: {response.status_code} - {response.text}")
                    return False
            else:
                print(f"❌ Failed to create first inspection: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Duplicate prevention test error: {str(e)}")
            return False

    def investigate_database_integrity(self):
        """Test Issue 5: Database Investigation"""
        print("\n🔍 TESTING ISSUE 5: Database Investigation")
        print("=" * 60)
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # 1. Check existing inspections in database
            print("Investigating existing inspections...")
            response = self.session.get(f"{BACKEND_URL}/inspections", headers=headers)
            print(f"GET /inspections Status: {response.status_code}")
            
            if response.status_code == 200:
                inspections = response.json()
                print(f"Total inspections in database: {len(inspections)}")
                
                # Analyze inspection data integrity
                status_counts = {}
                assignment_issues = []
                
                for inspection in inspections:
                    # Count statuses
                    status = inspection.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                    
                    # Check assignment data integrity
                    if not inspection.get('inspector_id'):
                        assignment_issues.append(f"Inspection {inspection['id']} has no inspector_id")
                    
                    if not inspection.get('customer_id'):
                        assignment_issues.append(f"Inspection {inspection['id']} has no customer_id")
                
                print("Status distribution:")
                for status, count in status_counts.items():
                    print(f"   {status}: {count}")
                
                if assignment_issues:
                    print("❌ Assignment data integrity issues found:")
                    for issue in assignment_issues[:5]:  # Show first 5 issues
                        print(f"   {issue}")
                else:
                    print("✅ No assignment data integrity issues found")
                
                # 2. Check customers
                response = self.session.get(f"{BACKEND_URL}/customers", headers=headers)
                if response.status_code == 200:
                    customers = response.json()
                    print(f"Total customers in database: {len(customers)}")
                    
                    # Check customer-equipment relationships
                    customers_with_equipment = [c for c in customers if c.get('equipments')]
                    print(f"Customers with equipment: {len(customers_with_equipment)}")
                
                # 3. Check users
                response = self.session.get(f"{BACKEND_URL}/users", headers=headers)
                if response.status_code == 200:
                    users = response.json()
                    print(f"Total users in database: {len(users)}")
                    
                    role_counts = {}
                    for user in users:
                        role = user.get('role', 'unknown')
                        role_counts[role] = role_counts.get(role, 0) + 1
                    
                    print("User role distribution:")
                    for role, count in role_counts.items():
                        print(f"   {role}: {count}")
                
                print("✅ Database investigation completed")
                return True
            else:
                print(f"❌ Failed to access inspections: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Database investigation error: {str(e)}")
            return False

    def run_workflow_tests(self):
        """Run all critical workflow tests"""
        print("🚀 Starting Critical Inspection Workflow Tests")
        print("=" * 70)
        
        test_results = {}
        
        # Setup phase
        print("SETUP PHASE")
        print("-" * 30)
        
        test_results['admin_auth'] = self.authenticate_admin()
        if not test_results['admin_auth']:
            print("❌ Cannot proceed without admin authentication")
            return test_results
        
        test_results['setup_users'] = self.setup_test_users()
        test_results['inspector_auth'] = self.authenticate_inspector()
        test_results['tech_manager_auth'] = self.authenticate_tech_manager()
        test_results['setup_customer'] = self.setup_test_customer()
        
        # Critical workflow tests
        print("\nCRITICAL WORKFLOW TESTS")
        print("-" * 30)
        
        test_results['inspector_assignment_visibility'] = self.test_inspector_assignment_visibility()
        test_results['inspection_status_workflow'] = self.test_inspection_status_workflow()
        test_results['technical_manager_report_queue'] = self.test_technical_manager_report_queue()
        test_results['duplicate_inspection_prevention'] = self.test_duplicate_inspection_prevention()
        test_results['database_integrity'] = self.investigate_database_integrity()
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 CRITICAL WORKFLOW TEST SUMMARY")
        print("=" * 70)
        
        critical_tests = [
            'inspector_assignment_visibility',
            'inspection_status_workflow', 
            'technical_manager_report_queue',
            'duplicate_inspection_prevention',
            'database_integrity'
        ]
        
        passed = 0
        failed_tests = []
        
        for test_name in critical_tests:
            result = test_results.get(test_name, False)
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title():<40} {status}")
            
            if result:
                passed += 1
            else:
                failed_tests.append(test_name)
        
        print(f"\nCritical Tests Result: {passed}/{len(critical_tests)} passed")
        
        if failed_tests:
            print("\n❌ FAILED CRITICAL TESTS:")
            for test in failed_tests:
                print(f"   • {test.replace('_', ' ').title()}")
        
        if passed == len(critical_tests):
            print("\n🎉 All critical workflow tests passed!")
        else:
            print(f"\n⚠️  {len(critical_tests) - passed} critical workflow issue(s) identified")
        
        return test_results

if __name__ == "__main__":
    tester = InspectionWorkflowTester()
    results = tester.run_workflow_tests()