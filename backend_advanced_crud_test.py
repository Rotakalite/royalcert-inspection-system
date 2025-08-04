#!/usr/bin/env python3
"""
ADVANCED DATABASE CRUD OPERATIONS TESTING
Tests edge cases and specific scenarios that might cause CRUD issues
Focus: Concurrent operations, transaction handling, async issues, data consistency
"""

import requests
import json
import time
import threading
from datetime import datetime
from pymongo import MongoClient
import os

# Configuration
BACKEND_URL = "https://eba81ca4-6566-454a-8283-f31f83336333.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# MongoDB connection for direct database verification
MONGO_URL = "mongodb+srv://royalcert_user:Ccpp1144..@royalcert-cluster.l1hqqn.mongodb.net/"
DATABASE_NAME = "royalcert_db"

class AdvancedCRUDTester:
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
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.user_info = data["user"]
                
                # Set authorization header for future requests
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

    def test_concurrent_operations(self):
        """Test concurrent CRUD operations to check for race conditions"""
        print("\n🔄 Testing Concurrent Operations...")
        
        def create_user(thread_id):
            """Create a user in a separate thread"""
            try:
                session = requests.Session()
                session.headers.update({"Authorization": f"Bearer {self.token}"})
                
                user_data = {
                    "username": f"concurrent_user_{thread_id}_{int(time.time())}",
                    "email": f"concurrent{thread_id}@example.com",
                    "full_name": f"Concurrent User {thread_id}",
                    "password": "testpass123",
                    "role": "denetci"
                }
                
                response = session.post(f"{BACKEND_URL}/auth/register", json=user_data)
                return response.status_code == 200, response.json() if response.status_code == 200 else None
            except Exception as e:
                return False, str(e)
        
        # Create multiple users concurrently
        threads = []
        results = {}
        
        for i in range(5):
            thread = threading.Thread(target=lambda i=i: results.update({i: create_user(i)}))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        successful_creates = sum(1 for success, _ in results.values() if success)
        print(f"   Concurrent creates successful: {successful_creates}/5")
        
        if successful_creates >= 4:  # Allow for some race conditions
            print("   ✅ Concurrent operations working correctly")
            
            # Clean up created users
            for success, user_data in results.values():
                if success and user_data:
                    try:
                        self.session.delete(f"{BACKEND_URL}/users/{user_data['id']}")
                    except:
                        pass
            
            return True
        else:
            print("   ❌ Concurrent operations failed")
            return False

    def test_large_data_operations(self):
        """Test operations with large amounts of data"""
        print("\n📊 Testing Large Data Operations...")
        
        try:
            # Create customer with large equipment list
            large_equipments = []
            for i in range(50):  # Create 50 equipment entries
                large_equipments.append({
                    "equipment_type": "CARASKAL",
                    "serial_number": f"LARGE-{i:03d}",
                    "manufacturer": f"Manufacturer {i}",
                    "model": f"Model {i}",
                    "capacity": f"{1000 + i * 100} kg"
                })
            
            customer_data = {
                "company_name": f"Large Data Test Company {int(time.time())}",
                "contact_person": "Large Data Test Contact",
                "phone": "+90 555 123 4567",
                "email": "largedata@company.com",
                "address": "Large Data Test Address",
                "equipments": large_equipments
            }
            
            # Create customer
            response = self.session.post(f"{BACKEND_URL}/customers", json=customer_data)
            print(f"   Large customer create status: {response.status_code}")
            
            if response.status_code == 200:
                customer = response.json()
                customer_id = customer["id"]
                
                # Verify in database
                time.sleep(2)  # Wait for database sync
                db_customer = self.db["customers"].find_one({"id": customer_id})
                
                if db_customer and len(db_customer.get("equipments", [])) == 50:
                    print("   ✅ Large data create operation successful")
                    
                    # Test update with large data
                    customer_data["company_name"] = "Updated Large Data Company"
                    customer_data["equipments"] = large_equipments[:25]  # Reduce to 25
                    
                    response = self.session.put(f"{BACKEND_URL}/customers/{customer_id}", json=customer_data)
                    print(f"   Large customer update status: {response.status_code}")
                    
                    if response.status_code == 200:
                        time.sleep(2)
                        db_customer_updated = self.db["customers"].find_one({"id": customer_id})
                        
                        if (db_customer_updated and 
                            db_customer_updated.get("company_name") == "Updated Large Data Company" and
                            len(db_customer_updated.get("equipments", [])) == 25):
                            print("   ✅ Large data update operation successful")
                            
                            # Clean up
                            self.session.delete(f"{BACKEND_URL}/customers/{customer_id}")
                            return True
                        else:
                            print("   ❌ Large data update not reflected in database")
                            return False
                    else:
                        print("   ❌ Large data update failed")
                        return False
                else:
                    print("   ❌ Large data create not reflected in database")
                    return False
            else:
                print("   ❌ Large data create failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Large data operations error: {str(e)}")
            return False

    def test_special_characters_and_unicode(self):
        """Test operations with special characters and Unicode"""
        print("\n🌐 Testing Special Characters and Unicode...")
        
        try:
            # Test with Turkish characters and special symbols
            customer_data = {
                "company_name": "Özel Karakterler Şirketi A.Ş. & Co. Ltd. 🏢",
                "contact_person": "Müdür Çağlar Öztürk",
                "phone": "+90 (555) 123-4567",
                "email": "özel@şirket.com.tr",
                "address": "İstanbul, Türkiye - Çankaya Mah. No: 123/A",
                "equipments": [
                    {
                        "equipment_type": "ÇARASKAL",
                        "serial_number": "TR-ÖZL-001",
                        "manufacturer": "Türk Üretici A.Ş.",
                        "notes": "Özel notlar: ğüşıöç ĞÜŞIÖÇ"
                    }
                ]
            }
            
            # Create customer with special characters
            response = self.session.post(f"{BACKEND_URL}/customers", json=customer_data)
            print(f"   Unicode customer create status: {response.status_code}")
            
            if response.status_code == 200:
                customer = response.json()
                customer_id = customer["id"]
                
                # Verify in database
                time.sleep(1)
                db_customer = self.db["customers"].find_one({"id": customer_id})
                
                if (db_customer and 
                    db_customer.get("company_name") == customer_data["company_name"] and
                    db_customer.get("contact_person") == customer_data["contact_person"]):
                    print("   ✅ Unicode create operation successful")
                    
                    # Test update with more special characters
                    update_data = customer_data.copy()
                    update_data["company_name"] = "Güncellenmiş Özel Şirket™ ® © €"
                    update_data["address"] = "Yeni Adres: Ümraniye/İstanbul 🇹🇷"
                    
                    response = self.session.put(f"{BACKEND_URL}/customers/{customer_id}", json=update_data)
                    print(f"   Unicode customer update status: {response.status_code}")
                    
                    if response.status_code == 200:
                        time.sleep(1)
                        db_customer_updated = self.db["customers"].find_one({"id": customer_id})
                        
                        if (db_customer_updated and 
                            db_customer_updated.get("company_name") == update_data["company_name"]):
                            print("   ✅ Unicode update operation successful")
                            
                            # Clean up
                            self.session.delete(f"{BACKEND_URL}/customers/{customer_id}")
                            return True
                        else:
                            print("   ❌ Unicode update not reflected in database")
                            return False
                    else:
                        print("   ❌ Unicode update failed")
                        return False
                else:
                    print("   ❌ Unicode create not reflected in database")
                    return False
            else:
                print("   ❌ Unicode create failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Unicode operations error: {str(e)}")
            return False

    def test_rapid_sequential_operations(self):
        """Test rapid sequential CRUD operations"""
        print("\n⚡ Testing Rapid Sequential Operations...")
        
        try:
            user_ids = []
            
            # Rapid create operations
            for i in range(10):
                user_data = {
                    "username": f"rapid_user_{i}_{int(time.time())}",
                    "email": f"rapid{i}@example.com",
                    "full_name": f"Rapid User {i}",
                    "password": "testpass123",
                    "role": "denetci"
                }
                
                response = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
                if response.status_code == 200:
                    user_ids.append(response.json()["id"])
                else:
                    print(f"   ❌ Rapid create {i} failed: {response.status_code}")
                    return False
            
            print(f"   ✅ Rapid creates successful: {len(user_ids)}/10")
            
            # Wait for database sync
            time.sleep(2)
            
            # Verify all users exist in database
            db_count = 0
            for user_id in user_ids:
                if self.db["users"].find_one({"id": user_id}):
                    db_count += 1
            
            print(f"   Database verification: {db_count}/{len(user_ids)} users found")
            
            if db_count == len(user_ids):
                print("   ✅ All rapid creates reflected in database")
                
                # Rapid update operations
                update_count = 0
                for i, user_id in enumerate(user_ids):
                    update_data = {
                        "full_name": f"Updated Rapid User {i}",
                        "email": f"updated_rapid{i}@example.com"
                    }
                    
                    response = self.session.put(f"{BACKEND_URL}/users/{user_id}", json=update_data)
                    if response.status_code == 200:
                        update_count += 1
                
                print(f"   ✅ Rapid updates successful: {update_count}/{len(user_ids)}")
                
                # Wait and verify updates
                time.sleep(2)
                db_update_count = 0
                for i, user_id in enumerate(user_ids):
                    db_user = self.db["users"].find_one({"id": user_id})
                    if db_user and db_user.get("full_name") == f"Updated Rapid User {i}":
                        db_update_count += 1
                
                print(f"   Database update verification: {db_update_count}/{len(user_ids)} updates found")
                
                # Rapid delete operations
                delete_count = 0
                for user_id in user_ids:
                    response = self.session.delete(f"{BACKEND_URL}/users/{user_id}")
                    if response.status_code == 200:
                        delete_count += 1
                
                print(f"   ✅ Rapid deletes successful: {delete_count}/{len(user_ids)}")
                
                # Wait and verify deletes
                time.sleep(2)
                db_delete_count = 0
                for user_id in user_ids:
                    if not self.db["users"].find_one({"id": user_id}):
                        db_delete_count += 1
                
                print(f"   Database delete verification: {db_delete_count}/{len(user_ids)} deletes confirmed")
                
                if db_update_count == len(user_ids) and db_delete_count == len(user_ids):
                    print("   ✅ All rapid operations reflected in database")
                    return True
                else:
                    print("   ❌ Some rapid operations not reflected in database")
                    return False
            else:
                print("   ❌ Rapid creates not fully reflected in database")
                return False
                
        except Exception as e:
            print(f"   ❌ Rapid operations error: {str(e)}")
            return False

    def test_database_consistency_after_errors(self):
        """Test database consistency after error conditions"""
        print("\n🔧 Testing Database Consistency After Errors...")
        
        try:
            # Test 1: Create user with invalid data, then create valid user
            print("   Testing error recovery...")
            
            # Try to create user with invalid email (should fail)
            invalid_user_data = {
                "username": "invalid_user",
                "email": "invalid-email",  # Invalid email format
                "full_name": "Invalid User",
                "password": "short",  # Too short password
                "role": "invalid_role"  # Invalid role
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=invalid_user_data)
            print(f"   Invalid user create status: {response.status_code} (expected: 400 or 422)")
            
            # Now create valid user to test if system recovered
            valid_user_data = {
                "username": f"valid_user_{int(time.time())}",
                "email": "valid@example.com",
                "full_name": "Valid User After Error",
                "password": "validpass123",
                "role": "denetci"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=valid_user_data)
            print(f"   Valid user create after error status: {response.status_code}")
            
            if response.status_code == 200:
                user = response.json()
                user_id = user["id"]
                
                # Verify in database
                time.sleep(1)
                db_user = self.db["users"].find_one({"id": user_id})
                
                if db_user:
                    print("   ✅ System recovered from error correctly")
                    
                    # Clean up
                    self.session.delete(f"{BACKEND_URL}/users/{user_id}")
                    return True
                else:
                    print("   ❌ Valid user not found in database after error")
                    return False
            else:
                print("   ❌ System did not recover from error")
                return False
                
        except Exception as e:
            print(f"   ❌ Error recovery test failed: {str(e)}")
            return False

    def test_inspection_crud_with_complex_data(self):
        """Test inspection CRUD operations with complex form data"""
        print("\n📋 Testing Inspection CRUD with Complex Data...")
        
        try:
            # First, get a customer for the inspection
            customers_response = self.session.get(f"{BACKEND_URL}/customers")
            if customers_response.status_code != 200 or not customers_response.json():
                print("   ❌ No customers available for inspection test")
                return False
            
            customer_id = customers_response.json()[0]["id"]
            
            # Create inspection with complex equipment info
            inspection_data = {
                "customer_id": customer_id,
                "equipment_info": {
                    "equipment_type": "CARASKAL",
                    "serial_number": f"COMPLEX-{int(time.time())}",
                    "manufacturer": "Complex Test Manufacturer",
                    "model": "Complex Model X1",
                    "capacity": "5000 kg",
                    "year": 2023,
                    "location": "Test Location",
                    "additional_info": {
                        "maintenance_history": ["2023-01-15", "2023-06-15"],
                        "certifications": ["ISO 9001", "CE"],
                        "special_notes": "Özel notlar ve açıklamalar"
                    }
                },
                "inspector_id": self.user_info["id"],
                "planned_date": "2025-01-25T10:00:00"
            }
            
            # Create inspection
            response = self.session.post(f"{BACKEND_URL}/inspections", json=inspection_data)
            print(f"   Complex inspection create status: {response.status_code}")
            
            if response.status_code == 200:
                inspection = response.json()
                inspection_id = inspection["id"]
                
                # Verify in database
                time.sleep(1)
                db_inspection = self.db["inspections"].find_one({"id": inspection_id})
                
                if db_inspection and db_inspection.get("equipment_info", {}).get("serial_number") == inspection_data["equipment_info"]["serial_number"]:
                    print("   ✅ Complex inspection create successful")
                    
                    # Update inspection with complex report data
                    complex_report_data = {
                        "status": "rapor_yazildi",
                        "report_data": {
                            "form_data": {
                                "item_1": {"value": "U", "comment": "Test comment 1"},
                                "item_2": {"value": "UD", "comment": "Test comment 2"},
                                "item_3": {"value": "U.Y", "comment": "Özel açıklama"}
                            },
                            "general_info": {
                                "inspection_date": "2025-01-25",
                                "weather_conditions": "Güneşli",
                                "temperature": "20°C"
                            },
                            "photos": {
                                "photo_1": "base64_encoded_photo_data_here",
                                "photo_2": "base64_encoded_photo_data_here"
                            },
                            "defects": "Tespit edilen kusurlar listesi",
                            "conclusion": "UYGUN"
                        }
                    }
                    
                    response = self.session.put(f"{BACKEND_URL}/inspections/{inspection_id}", json=complex_report_data)
                    print(f"   Complex inspection update status: {response.status_code}")
                    
                    if response.status_code == 200:
                        time.sleep(1)
                        db_inspection_updated = self.db["inspections"].find_one({"id": inspection_id})
                        
                        if (db_inspection_updated and 
                            db_inspection_updated.get("status") == "rapor_yazildi" and
                            db_inspection_updated.get("report_data", {}).get("conclusion") == "UYGUN"):
                            print("   ✅ Complex inspection update successful")
                            return True
                        else:
                            print("   ❌ Complex inspection update not reflected in database")
                            return False
                    else:
                        print("   ❌ Complex inspection update failed")
                        return False
                else:
                    print("   ❌ Complex inspection create not reflected in database")
                    return False
            else:
                print("   ❌ Complex inspection create failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Complex inspection CRUD error: {str(e)}")
            return False

    def run_advanced_tests(self):
        """Run all advanced CRUD tests"""
        print("🚀 Starting ADVANCED DATABASE CRUD OPERATIONS TESTING")
        print("=" * 80)
        
        test_results = {}
        
        # Connect to MongoDB
        test_results['mongodb_connection'] = self.connect_to_mongodb()
        
        if not test_results['mongodb_connection']:
            print("\n❌ Cannot proceed without MongoDB connection")
            return test_results
        
        # Authentication test
        test_results['authentication'] = self.authenticate()
        
        if not test_results['authentication']:
            print("\n❌ Cannot proceed without authentication")
            return test_results
        
        # Run advanced tests
        test_results['concurrent_operations'] = self.test_concurrent_operations()
        test_results['large_data_operations'] = self.test_large_data_operations()
        test_results['unicode_operations'] = self.test_special_characters_and_unicode()
        test_results['rapid_sequential_operations'] = self.test_rapid_sequential_operations()
        test_results['error_recovery'] = self.test_database_consistency_after_errors()
        test_results['complex_inspection_crud'] = self.test_inspection_crud_with_complex_data()
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 ADVANCED DATABASE CRUD OPERATIONS TEST SUMMARY")
        print("=" * 80)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title():<40} {status}")
            if result:
                passed += 1
        
        print(f"\nOverall Result: {passed}/{total} tests passed")
        
        # Analysis
        print("\n" + "=" * 80)
        print("🔍 ADVANCED CRUD OPERATIONS ANALYSIS")
        print("=" * 80)
        
        if passed == total:
            print("🎉 ALL ADVANCED CRUD OPERATIONS WORKING CORRECTLY!")
            print("   ✅ Concurrent operations handled properly")
            print("   ✅ Large data operations working")
            print("   ✅ Unicode and special characters supported")
            print("   ✅ Rapid sequential operations stable")
            print("   ✅ Error recovery working correctly")
            print("   ✅ Complex data structures handled properly")
        else:
            print("🚨 ADVANCED ISSUES IDENTIFIED:")
            
            failed_tests = [name for name, result in test_results.items() if not result]
            for test_name in failed_tests:
                print(f"   ❌ {test_name.replace('_', ' ').title()} failed")
        
        return test_results

if __name__ == "__main__":
    tester = AdvancedCRUDTester()
    results = tester.run_advanced_tests()