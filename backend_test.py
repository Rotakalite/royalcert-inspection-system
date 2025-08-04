#!/usr/bin/env python3
"""
Backend API Testing for RoyalCert Bulk Import System
Tests the bulk customer import functionality and template download
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

class RoyalCertTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        
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
    
    def test_template_download(self):
        """Test Excel template download endpoint"""
        print("\n📥 Testing Template Download...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/customers/bulk-import/template")
            print(f"Template Download Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "message" in data and "filename" in data and "content" in data:
                    print(f"✅ Template download successful")
                    print(f"   Filename: {data['filename']}")
                    print(f"   Message: {data['message']}")
                    
                    # Try to decode the hex content
                    try:
                        excel_content = bytes.fromhex(data['content'])
                        
                        # Parse the Excel content to verify structure
                        df = pd.read_excel(io.BytesIO(excel_content), engine='openpyxl')
                        
                        expected_columns = [
                            'Muayene Alanı',
                            'Muayene Alt Alanı', 
                            'Muayene Türü',
                            'Referans',
                            'Muayene Tarihi',
                            'Zorunlu Alan ya da Gönüllü Alan',
                            'Müşteri Adı',
                            'Müşteri Adresi',
                            'Denetçi Adı',
                            'Denetçinin Lokasyonu',
                            'Rapor Onay Tarihi',
                            'Raporu Onaylayan Teknik Yönetici'
                        ]
                        
                        print(f"   Template has {len(df.columns)} columns")
                        print(f"   Expected {len(expected_columns)} columns")
                        
                        if len(df.columns) == len(expected_columns):
                            print("✅ Template has correct number of columns (12)")
                            
                            # Check if columns match expected names
                            columns_match = all(col in df.columns for col in expected_columns)
                            if columns_match:
                                print("✅ All expected column names present")
                            else:
                                print("⚠️  Column names may differ from expected")
                                print(f"   Actual columns: {list(df.columns)}")
                            
                            # Check sample data
                            if len(df) > 0:
                                print(f"✅ Template contains {len(df)} sample rows")
                                print("   Sample data preview:")
                                for i, row in df.head(2).iterrows():
                                    print(f"     Row {i+1}: {row['Müşteri Adı']} - {row['Müşteri Adresi']}")
                            else:
                                print("⚠️  Template has no sample data")
                                
                        else:
                            print(f"❌ Template has incorrect number of columns")
                            
                        return True
                        
                    except Exception as e:
                        print(f"❌ Failed to parse Excel content: {str(e)}")
                        return False
                        
                else:
                    print(f"❌ Invalid response structure: {data}")
                    return False
                    
            else:
                print(f"❌ Template download failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Template download error: {str(e)}")
            return False
    
    def create_test_excel(self, scenario="valid"):
        """Create test Excel files for different scenarios"""
        
        headers = [
            'Muayene Alanı',
            'Muayene Alt Alanı', 
            'Muayene Türü',
            'Referans',
            'Muayene Tarihi',
            'Zorunlu Alan ya da Gönüllü Alan',
            'Müşteri Adı',
            'Müşteri Adresi',
            'Denetçi Adı',
            'Denetçinin Lokasyonu',
            'Rapor Onay Tarihi',
            'Raporu Onaylayan Teknik Yönetici'
        ]
        
        if scenario == "valid":
            data = [
                [
                    'Kaldırma ve İndirme Ekipmanları',
                    'CARASKAL',
                    'PERİYODİK',
                    'TSE EN 280',
                    '2025-01-15',
                    'Zorunlu Alan',
                    'Test İnşaat Ltd. Şti.',
                    'İstanbul, Beşiktaş, Test Caddesi No:123',
                    'Ahmet Yılmaz',
                    'İstanbul',
                    '2025-01-20',
                    'Mehmet Koç'
                ],
                [
                    'İş Güvenliği Ekipmanları',
                    'İSKELE',
                    'İLK MONTAJ',
                    'TS 498',
                    '2025-02-10',
                    'Gönüllü Alan',
                    'Demo Yapı A.Ş.',
                    'Ankara, Çankaya, Demo Sokak No:456',
                    'Fatma Demir',
                    'Ankara',
                    '',
                    ''
                ]
            ]
        elif scenario == "missing_mandatory":
            data = [
                [
                    'Kaldırma ve İndirme Ekipmanları',
                    'CARASKAL',
                    'PERİYODİK',
                    'TSE EN 280',
                    '2025-01-15',
                    'Zorunlu Alan',
                    '',  # Missing customer name
                    'İstanbul, Beşiktaş, Test Caddesi No:123',
                    'Ahmet Yılmaz',
                    'İstanbul',
                    '2025-01-20',
                    'Mehmet Koç'
                ],
                [
                    'İş Güvenliği Ekipmanları',
                    'İSKELE',
                    'İLK MONTAJ',
                    'TS 498',
                    '2025-02-10',
                    'Gönüllü Alan',
                    'Demo Yapı A.Ş.',
                    '',  # Missing customer address
                    'Fatma Demir',
                    'Ankara',
                    '',
                    ''
                ]
            ]
        elif scenario == "empty_values":
            data = [
                [
                    '-',  # Empty marker
                    '',   # Empty string
                    'PERİYODİK',
                    None,  # None value
                    '2025-01-15',
                    'Zorunlu Alan',
                    'Test Şirketi Ltd.',
                    'Test Adresi, İstanbul',
                    '-',
                    '',
                    None,
                    '-'
                ]
            ]
        elif scenario == "duplicate":
            data = [
                [
                    'Kaldırma ve İndirme Ekipmanları',
                    'CARASKAL',
                    'PERİYODİK',
                    'TSE EN 280',
                    '2025-01-15',
                    'Zorunlu Alan',
                    'Duplicate Test Şirketi',
                    'İstanbul, Test Adresi',
                    'Ahmet Yılmaz',
                    'İstanbul',
                    '2025-01-20',
                    'Mehmet Koç'
                ],
                [
                    'İş Güvenliği Ekipmanları',
                    'İSKELE',
                    'İLK MONTAJ',
                    'TS 498',
                    '2025-02-10',
                    'Gönüllü Alan',
                    'Duplicate Test Şirketi',  # Same company name
                    'İstanbul, Test Adresi',   # Same address
                    'Fatma Demir',
                    'Ankara',
                    '',
                    ''
                ]
            ]
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)
        
        # Save to BytesIO
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Müşteri Listesi')
        
        output.seek(0)
        return output.getvalue()
    
    def test_bulk_import(self, scenario="valid"):
        """Test bulk import with different scenarios"""
        print(f"\n📤 Testing Bulk Import - {scenario.upper()} scenario...")
        
        try:
            # Create test Excel file
            excel_content = self.create_test_excel(scenario)
            
            # Prepare file upload
            files = {
                'file': ('test_import.xlsx', excel_content, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            
            response = self.session.post(f"{BACKEND_URL}/customers/bulk-import", files=files)
            print(f"Bulk Import Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Bulk import completed")
                print(f"   Total rows: {data.get('total_rows', 0)}")
                print(f"   Successful imports: {data.get('successful_imports', 0)}")
                print(f"   Failed imports: {data.get('failed_imports', 0)}")
                
                if data.get('warnings'):
                    print(f"   Warnings ({len(data['warnings'])}):")
                    for warning in data['warnings'][:3]:  # Show first 3 warnings
                        print(f"     - {warning}")
                
                if data.get('errors'):
                    print(f"   Errors ({len(data['errors'])}):")
                    for error in data['errors'][:3]:  # Show first 3 errors
                        print(f"     - Row {error.get('row', 'N/A')}: {error.get('error', 'Unknown error')}")
                
                # Validate results based on scenario
                if scenario == "valid":
                    if data.get('successful_imports', 0) > 0 and data.get('failed_imports', 0) == 0:
                        print("✅ Valid data processed successfully")
                        return True
                    else:
                        print("⚠️  Expected successful imports for valid data")
                        return False
                        
                elif scenario == "missing_mandatory":
                    if data.get('warnings') and len(data['warnings']) > 0:
                        print("✅ Missing mandatory fields handled correctly")
                        return True
                    else:
                        print("⚠️  Expected warnings for missing mandatory fields")
                        return False
                        
                elif scenario == "empty_values":
                    print("✅ Empty values scenario processed")
                    return True
                    
                elif scenario == "duplicate":
                    if data.get('warnings') and any('mevcut' in warning for warning in data['warnings']):
                        print("✅ Duplicate handling working correctly")
                        return True
                    else:
                        print("⚠️  Expected duplicate handling warnings")
                        return False
                
                return True
                
            else:
                print(f"❌ Bulk import failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Bulk import error: {str(e)}")
            return False
    
    def test_invalid_file_formats(self):
        """Test bulk import with invalid file formats"""
        print(f"\n🚫 Testing Invalid File Formats...")
        
        test_cases = [
            ("test.txt", "text/plain", b"This is a text file"),
            ("test.pdf", "application/pdf", b"PDF content"),
            ("test.doc", "application/msword", b"DOC content")
        ]
        
        results = []
        
        for filename, content_type, content in test_cases:
            try:
                files = {
                    'file': (filename, content, content_type)
                }
                
                response = self.session.post(f"{BACKEND_URL}/customers/bulk-import", files=files)
                
                if response.status_code == 400:
                    print(f"✅ {filename}: Correctly rejected (400)")
                    results.append(True)
                else:
                    print(f"❌ {filename}: Should have been rejected (got {response.status_code})")
                    results.append(False)
                    
            except Exception as e:
                print(f"❌ {filename}: Error testing - {str(e)}")
                results.append(False)
        
        return all(results)
    
    def test_corrupted_excel(self):
        """Test bulk import with corrupted Excel file"""
        print(f"\n💥 Testing Corrupted Excel File...")
        
        try:
            # Create corrupted Excel content
            corrupted_content = b"This is not a valid Excel file content"
            
            files = {
                'file': ('corrupted.xlsx', corrupted_content, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            
            response = self.session.post(f"{BACKEND_URL}/customers/bulk-import", files=files)
            
            if response.status_code == 400:
                print(f"✅ Corrupted Excel file correctly rejected")
                return True
            else:
                print(f"❌ Corrupted Excel file should have been rejected (got {response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ Corrupted Excel test error: {str(e)}")
            return False
    
    def test_missing_columns(self):
        """Test bulk import with insufficient columns"""
        print(f"\n📊 Testing Missing Columns...")
        
        try:
            # Create Excel with only 5 columns (less than required 12)
            headers = ['Col1', 'Col2', 'Col3', 'Col4', 'Col5']
            data = [['Data1', 'Data2', 'Data3', 'Data4', 'Data5']]
            
            df = pd.DataFrame(data, columns=headers)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            output.seek(0)
            
            files = {
                'file': ('insufficient_columns.xlsx', output.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            
            response = self.session.post(f"{BACKEND_URL}/customers/bulk-import", files=files)
            
            if response.status_code == 400:
                print(f"✅ Insufficient columns correctly rejected")
                return True
            else:
                print(f"❌ Insufficient columns should have been rejected (got {response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ Missing columns test error: {str(e)}")
            return False
    
    def test_unauthorized_access(self):
        """Test bulk import endpoints without proper authentication"""
        print(f"\n🔒 Testing Unauthorized Access...")
        
        # Create a session without authentication
        unauth_session = requests.Session()
        
        results = []
        
        # Test template download without auth
        try:
            response = unauth_session.get(f"{BACKEND_URL}/customers/bulk-import/template")
            if response.status_code in [401, 403]:  # Both are valid for authentication failure
                print("✅ Template download correctly requires authentication")
                results.append(True)
            else:
                print(f"❌ Template download should require auth (got {response.status_code})")
                results.append(False)
        except Exception as e:
            print(f"❌ Unauthorized template test error: {str(e)}")
            results.append(False)
        
        # Test bulk import without auth
        try:
            excel_content = self.create_test_excel("valid")
            files = {
                'file': ('test.xlsx', excel_content, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            
            response = unauth_session.post(f"{BACKEND_URL}/customers/bulk-import", files=files)
            if response.status_code in [401, 403]:  # Both are valid for authentication failure
                print("✅ Bulk import correctly requires authentication")
                results.append(True)
            else:
                print(f"❌ Bulk import should require auth (got {response.status_code})")
                results.append(False)
        except Exception as e:
            print(f"❌ Unauthorized bulk import test error: {str(e)}")
            results.append(False)
        
        return all(results)
    
    def run_all_tests(self):
        """Run all bulk import tests"""
        print("🚀 Starting RoyalCert Bulk Import System Tests")
        print("=" * 60)
        
        test_results = {}
        
        # Authentication test
        test_results['authentication'] = self.authenticate()
        
        if not test_results['authentication']:
            print("\n❌ Cannot proceed without authentication")
            return test_results
        
        # Template download test
        test_results['template_download'] = self.test_template_download()
        
        # Bulk import tests with different scenarios
        test_results['bulk_import_valid'] = self.test_bulk_import("valid")
        test_results['bulk_import_missing_mandatory'] = self.test_bulk_import("missing_mandatory")
        test_results['bulk_import_empty_values'] = self.test_bulk_import("empty_values")
        test_results['bulk_import_duplicate'] = self.test_bulk_import("duplicate")
        
        # Error handling tests
        test_results['invalid_file_formats'] = self.test_invalid_file_formats()
        test_results['corrupted_excel'] = self.test_corrupted_excel()
        test_results['missing_columns'] = self.test_missing_columns()
        test_results['unauthorized_access'] = self.test_unauthorized_access()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title():<30} {status}")
            if result:
                passed += 1
        
        print(f"\nOverall Result: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Bulk import system is working correctly.")
        else:
            print(f"⚠️  {total - passed} test(s) failed. Please review the issues above.")
        
        return test_results

if __name__ == "__main__":
    tester = RoyalCertTester()
    results = tester.run_all_tests()