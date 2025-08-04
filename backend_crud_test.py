#!/usr/bin/env python3
"""
CRITICAL DATABASE CRUD OPERATIONS TESTING
Tests all database CRUD operations to identify why changes/deletions are not reflected in the database
Focus: Database connection, DELETE operations, UPDATE operations, data persistence verification
"""

import requests
import json
import time
from datetime import datetime
from pymongo import MongoClient
import os

# Configuration
BACKEND_URL = "https://405a5b7a-3c02-4793-9fcc-5203d2944620.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# MongoDB connection for direct database verification
MONGO_URL = "mongodb+srv://royalcert_user:Ccpp1144..@royalcert-cluster.l1hqqn.mongodb.net/"
DATABASE_NAME = "royalcert_db"

class CRUDOperationsTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        self.mongo_client = None
        self.db = None
        
    def connect_to_mongodb(self):
        """Connect directly to MongoDB for verification"""
        print("🔗 Connecting to MongoDB...")
        try:
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client[DATABASE_NAME]
            
            # Test connection
            self.db.command('ping')
            print("✅ MongoDB connection successful")
            
            # List collections
            collections = self.db.list_collection_names()
            print(f"   Available collections: {collections}")
            
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
            return False
    
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

    def get_collection_count(self, collection_name):
        """Get document count from MongoDB collection"""
        try:
            count = self.db[collection_name].count_documents({})
            return count
        except Exception as e:
            print(f"❌ Error getting count for {collection_name}: {str(e)}")
            return -1

    def verify_document_exists(self, collection_name, document_id):
        """Verify if document exists in MongoDB"""
        try:
            doc = self.db[collection_name].find_one({"id": document_id})
            return doc is not None
        except Exception as e:
            print(f"❌ Error checking document existence: {str(e)}")
            return False

    def test_user_crud_operations(self):
        """Test user CRUD operations with database verification"""
        print("\n👤 Testing USER CRUD Operations...")
        
        # Get initial count
        initial_count = self.get_collection_count("users")
        print(f"   Initial users count: {initial_count}")
        
        # CREATE - Create a test user
        print("\n   🔨 Testing USER CREATE...")
        test_user_data = {
            "username": f"testuser_{int(time.time())}",
            "email": "testuser@example.com",
            "full_name": "Test User CRUD",
            "password": "testpass123",
            "role": "denetci"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=test_user_data)
            print(f"   Create User Status: {response.status_code}")
            
            if response.status_code == 200:
                created_user = response.json()
                test_user_id = created_user["id"]
                print(f"   ✅ User created: {test_user_id}")
                
                # Verify in database
                time.sleep(1)  # Wait for database sync
                db_count_after_create = self.get_collection_count("users")
                db_user_exists = self.verify_document_exists("users", test_user_id)
                
                print(f"   Database count after create: {db_count_after_create}")
                print(f"   User exists in database: {db_user_exists}")
                
                if db_count_after_create > initial_count and db_user_exists:
                    print("   ✅ CREATE operation verified in database")
                else:
                    print("   ❌ CREATE operation NOT reflected in database")
                    return False
                
                # UPDATE - Update the user
                print("\n   ✏️  Testing USER UPDATE...")
                update_data = {
                    "full_name": "Updated Test User CRUD",
                    "email": "updated@example.com"
                }
                
                response = self.session.put(f"{BACKEND_URL}/users/{test_user_id}", json=update_data)
                print(f"   Update User Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Update API call successful")
                    
                    # Verify update in database
                    time.sleep(1)  # Wait for database sync
                    db_user = self.db["users"].find_one({"id": test_user_id})
                    
                    if db_user:
                        db_full_name = db_user.get("full_name")
                        db_email = db_user.get("email")
                        
                        print(f"   Database full_name: {db_full_name}")
                        print(f"   Database email: {db_email}")
                        
                        if db_full_name == update_data["full_name"] and db_email == update_data["email"]:
                            print("   ✅ UPDATE operation verified in database")
                        else:
                            print("   ❌ UPDATE operation NOT reflected in database")
                            print(f"   Expected: {update_data}")
                            print(f"   Actual: {{'full_name': '{db_full_name}', 'email': '{db_email}'}}")
                            return False
                    else:
                        print("   ❌ User not found in database after update")
                        return False
                else:
                    print(f"   ❌ Update failed: {response.text}")
                    return False
                
                # DELETE - Delete the user
                print("\n   🗑️  Testing USER DELETE...")
                response = self.session.delete(f"{BACKEND_URL}/users/{test_user_id}")
                print(f"   Delete User Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Delete API call successful")
                    
                    # Verify deletion in database
                    time.sleep(1)  # Wait for database sync
                    db_count_after_delete = self.get_collection_count("users")
                    db_user_exists_after_delete = self.verify_document_exists("users", test_user_id)
                    
                    print(f"   Database count after delete: {db_count_after_delete}")
                    print(f"   User exists in database after delete: {db_user_exists_after_delete}")
                    
                    if db_count_after_delete == initial_count and not db_user_exists_after_delete:
                        print("   ✅ DELETE operation verified in database")
                        return True
                    else:
                        print("   ❌ DELETE operation NOT reflected in database")
                        return False
                else:
                    print(f"   ❌ Delete failed: {response.text}")
                    return False
            else:
                print(f"   ❌ Create failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ User CRUD test error: {str(e)}")
            return False

    def test_customer_crud_operations(self):
        """Test customer CRUD operations with database verification"""
        print("\n🏢 Testing CUSTOMER CRUD Operations...")
        
        # Get initial count
        initial_count = self.get_collection_count("customers")
        print(f"   Initial customers count: {initial_count}")
        
        # CREATE - Create a test customer
        print("\n   🔨 Testing CUSTOMER CREATE...")
        test_customer_data = {
            "company_name": f"Test Company CRUD {int(time.time())}",
            "contact_person": "Test Contact Person",
            "phone": "+90 555 123 4567",
            "email": "test@company.com",
            "address": "Test Address, Istanbul, Turkey",
            "equipments": [
                {
                    "equipment_type": "CARASKAL",
                    "serial_number": "TEST-001",
                    "manufacturer": "Test Manufacturer"
                }
            ]
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/customers", json=test_customer_data)
            print(f"   Create Customer Status: {response.status_code}")
            
            if response.status_code == 200:
                created_customer = response.json()
                test_customer_id = created_customer["id"]
                print(f"   ✅ Customer created: {test_customer_id}")
                
                # Verify in database
                time.sleep(1)  # Wait for database sync
                db_count_after_create = self.get_collection_count("customers")
                db_customer_exists = self.verify_document_exists("customers", test_customer_id)
                
                print(f"   Database count after create: {db_count_after_create}")
                print(f"   Customer exists in database: {db_customer_exists}")
                
                if db_count_after_create > initial_count and db_customer_exists:
                    print("   ✅ CREATE operation verified in database")
                else:
                    print("   ❌ CREATE operation NOT reflected in database")
                    return False
                
                # UPDATE - Update the customer
                print("\n   ✏️  Testing CUSTOMER UPDATE...")
                update_data = {
                    "company_name": "Updated Test Company CRUD",
                    "contact_person": "Updated Contact Person",
                    "phone": "+90 555 999 8888",
                    "email": "updated@company.com",
                    "address": "Updated Address, Ankara, Turkey",
                    "equipments": test_customer_data["equipments"]
                }
                
                response = self.session.put(f"{BACKEND_URL}/customers/{test_customer_id}", json=update_data)
                print(f"   Update Customer Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Update API call successful")
                    
                    # Verify update in database
                    time.sleep(1)  # Wait for database sync
                    db_customer = self.db["customers"].find_one({"id": test_customer_id})
                    
                    if db_customer:
                        db_company_name = db_customer.get("company_name")
                        db_contact_person = db_customer.get("contact_person")
                        
                        print(f"   Database company_name: {db_company_name}")
                        print(f"   Database contact_person: {db_contact_person}")
                        
                        if db_company_name == update_data["company_name"] and db_contact_person == update_data["contact_person"]:
                            print("   ✅ UPDATE operation verified in database")
                        else:
                            print("   ❌ UPDATE operation NOT reflected in database")
                            return False
                    else:
                        print("   ❌ Customer not found in database after update")
                        return False
                else:
                    print(f"   ❌ Update failed: {response.text}")
                    return False
                
                # DELETE - Delete the customer
                print("\n   🗑️  Testing CUSTOMER DELETE...")
                response = self.session.delete(f"{BACKEND_URL}/customers/{test_customer_id}")
                print(f"   Delete Customer Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Delete API call successful")
                    
                    # Verify deletion in database
                    time.sleep(1)  # Wait for database sync
                    db_count_after_delete = self.get_collection_count("customers")
                    db_customer_exists_after_delete = self.verify_document_exists("customers", test_customer_id)
                    
                    print(f"   Database count after delete: {db_count_after_delete}")
                    print(f"   Customer exists in database after delete: {db_customer_exists_after_delete}")
                    
                    if db_count_after_delete == initial_count and not db_customer_exists_after_delete:
                        print("   ✅ DELETE operation verified in database")
                        return True
                    else:
                        print("   ❌ DELETE operation NOT reflected in database")
                        return False
                else:
                    print(f"   ❌ Delete failed: {response.text}")
                    return False
            else:
                print(f"   ❌ Create failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Customer CRUD test error: {str(e)}")
            return False

    def test_equipment_template_crud_operations(self):
        """Test equipment template CRUD operations with database verification"""
        print("\n⚙️  Testing EQUIPMENT TEMPLATE CRUD Operations...")
        
        # Get initial count
        initial_count = self.get_collection_count("equipment_templates")
        print(f"   Initial templates count: {initial_count}")
        
        # CREATE - Create a test template
        print("\n   🔨 Testing TEMPLATE CREATE...")
        test_template_data = {
            "name": f"Test Template CRUD {int(time.time())}",
            "equipment_type": f"TEST_EQUIPMENT_{int(time.time())}",
            "template_type": "FORM",
            "description": "Test template for CRUD operations",
            "categories": [
                {
                    "code": "A",
                    "name": "Test Category A",
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
            ]
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/equipment-templates", json=test_template_data)
            print(f"   Create Template Status: {response.status_code}")
            
            if response.status_code == 200:
                created_template = response.json()
                test_template_id = created_template["id"]
                print(f"   ✅ Template created: {test_template_id}")
                
                # Verify in database
                time.sleep(1)  # Wait for database sync
                db_count_after_create = self.get_collection_count("equipment_templates")
                db_template_exists = self.verify_document_exists("equipment_templates", test_template_id)
                
                print(f"   Database count after create: {db_count_after_create}")
                print(f"   Template exists in database: {db_template_exists}")
                
                if db_count_after_create > initial_count and db_template_exists:
                    print("   ✅ CREATE operation verified in database")
                else:
                    print("   ❌ CREATE operation NOT reflected in database")
                    return False
                
                # UPDATE - Update the template
                print("\n   ✏️  Testing TEMPLATE UPDATE...")
                update_data = {
                    "name": "Updated Test Template CRUD",
                    "equipment_type": test_template_data["equipment_type"],
                    "template_type": "FORM",
                    "description": "Updated test template description",
                    "categories": test_template_data["categories"]
                }
                
                response = self.session.put(f"{BACKEND_URL}/equipment-templates/{test_template_id}", json=update_data)
                print(f"   Update Template Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Update API call successful")
                    
                    # Verify update in database
                    time.sleep(1)  # Wait for database sync
                    db_template = self.db["equipment_templates"].find_one({"id": test_template_id})
                    
                    if db_template:
                        db_name = db_template.get("name")
                        db_description = db_template.get("description")
                        
                        print(f"   Database name: {db_name}")
                        print(f"   Database description: {db_description}")
                        
                        if db_name == update_data["name"] and db_description == update_data["description"]:
                            print("   ✅ UPDATE operation verified in database")
                        else:
                            print("   ❌ UPDATE operation NOT reflected in database")
                            return False
                    else:
                        print("   ❌ Template not found in database after update")
                        return False
                else:
                    print(f"   ❌ Update failed: {response.text}")
                    return False
                
                # DELETE - Delete the template (soft delete - sets is_active to false)
                print("\n   🗑️  Testing TEMPLATE DELETE...")
                response = self.session.delete(f"{BACKEND_URL}/equipment-templates/{test_template_id}")
                print(f"   Delete Template Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Delete API call successful")
                    
                    # Verify soft deletion in database (is_active should be false)
                    time.sleep(1)  # Wait for database sync
                    db_template_after_delete = self.db["equipment_templates"].find_one({"id": test_template_id})
                    
                    if db_template_after_delete:
                        is_active = db_template_after_delete.get("is_active", True)
                        print(f"   Template is_active after delete: {is_active}")
                        
                        if not is_active:
                            print("   ✅ SOFT DELETE operation verified in database")
                            return True
                        else:
                            print("   ❌ SOFT DELETE operation NOT reflected in database")
                            return False
                    else:
                        print("   ❌ Template not found in database after delete")
                        return False
                else:
                    print(f"   ❌ Delete failed: {response.text}")
                    return False
            else:
                print(f"   ❌ Create failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Template CRUD test error: {str(e)}")
            return False

    def test_database_connection_status(self):
        """Test database connection and basic operations"""
        print("\n🔗 Testing Database Connection Status...")
        
        try:
            # Test basic connection
            result = self.db.command('ping')
            print("   ✅ Database ping successful")
            
            # Test database name
            current_db = self.mongo_client.get_database().name
            print(f"   Current database: {current_db}")
            
            # List all collections and their counts
            collections = self.db.list_collection_names()
            print(f"   Available collections: {len(collections)}")
            
            for collection in collections:
                count = self.get_collection_count(collection)
                print(f"     {collection}: {count} documents")
            
            # Test write operation
            test_collection = "test_crud_operations"
            test_doc = {"test": True, "timestamp": datetime.utcnow()}
            
            # Insert test document
            insert_result = self.db[test_collection].insert_one(test_doc)
            print(f"   Test insert result: {insert_result.inserted_id}")
            
            # Read test document
            read_result = self.db[test_collection].find_one({"_id": insert_result.inserted_id})
            print(f"   Test read result: {read_result is not None}")
            
            # Update test document
            update_result = self.db[test_collection].update_one(
                {"_id": insert_result.inserted_id},
                {"$set": {"updated": True}}
            )
            print(f"   Test update result: {update_result.modified_count}")
            
            # Delete test document
            delete_result = self.db[test_collection].delete_one({"_id": insert_result.inserted_id})
            print(f"   Test delete result: {delete_result.deleted_count}")
            
            # Clean up test collection
            self.db.drop_collection(test_collection)
            
            print("   ✅ Database connection and operations working correctly")
            return True
            
        except Exception as e:
            print(f"   ❌ Database connection test failed: {str(e)}")
            return False

    def run_crud_tests(self):
        """Run all CRUD operation tests"""
        print("🚀 Starting CRITICAL DATABASE CRUD OPERATIONS TESTING")
        print("=" * 80)
        
        test_results = {}
        
        # Connect to MongoDB
        test_results['mongodb_connection'] = self.connect_to_mongodb()
        
        if not test_results['mongodb_connection']:
            print("\n❌ Cannot proceed without MongoDB connection")
            return test_results
        
        # Test database connection status
        test_results['database_connection_status'] = self.test_database_connection_status()
        
        # Authentication test
        test_results['authentication'] = self.authenticate()
        
        if not test_results['authentication']:
            print("\n❌ Cannot proceed without authentication")
            return test_results
        
        # Test CRUD operations
        test_results['user_crud_operations'] = self.test_user_crud_operations()
        test_results['customer_crud_operations'] = self.test_customer_crud_operations()
        test_results['template_crud_operations'] = self.test_equipment_template_crud_operations()
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 CRITICAL DATABASE CRUD OPERATIONS TEST SUMMARY")
        print("=" * 80)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title():<40} {status}")
            if result:
                passed += 1
        
        print(f"\nOverall Result: {passed}/{total} tests passed")
        
        # Analysis and recommendations
        print("\n" + "=" * 80)
        print("🔍 CRUD OPERATIONS ANALYSIS")
        print("=" * 80)
        
        if passed == total:
            print("🎉 ALL CRUD OPERATIONS WORKING CORRECTLY!")
            print("   ✅ Database connection is working")
            print("   ✅ CREATE operations persist data correctly")
            print("   ✅ UPDATE operations modify data correctly")
            print("   ✅ DELETE operations remove data correctly")
            print("   ✅ All changes are reflected in MongoDB")
        else:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            
            if not test_results.get('mongodb_connection'):
                print("   ❌ MongoDB connection failed - check connection string and credentials")
            
            if not test_results.get('database_connection_status'):
                print("   ❌ Database operations failed - check database permissions")
            
            if not test_results.get('user_crud_operations'):
                print("   ❌ User CRUD operations failed - check user management endpoints")
            
            if not test_results.get('customer_crud_operations'):
                print("   ❌ Customer CRUD operations failed - check customer management endpoints")
            
            if not test_results.get('template_crud_operations'):
                print("   ❌ Template CRUD operations failed - check template management endpoints")
            
            print("\n🔧 RECOMMENDED FIXES:")
            print("   1. Check MongoDB connection string and credentials")
            print("   2. Verify database write permissions")
            print("   3. Check if operations are using transactions correctly")
            print("   4. Verify async/await implementation in backend")
            print("   5. Check for any middleware blocking database writes")
        
        return test_results

if __name__ == "__main__":
    tester = CRUDOperationsTester()
    results = tester.run_crud_tests()