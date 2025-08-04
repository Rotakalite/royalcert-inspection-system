#!/usr/bin/env python3
"""
PDF Upload Debug Test - Manual Endpoint Test

PDF upload neden çalışmıyor debug et:
1. POST /api/equipment-templates/upload endpoint'ine manuel bir PDF dosyası upload et
2. Backend logs'unda "DEBUG: Upload filename" mesajının çıkıp çıkmadığını kontrol et  
3. PDF parser'ın çalışıp çalışmadığını kontrol et
4. Eğer PDF upload başarısız ise nedeni nedir?

Admin: admin/admin123

Logs'da şu mesajları arıyorum:
- "DEBUG: Upload filename: [filename]"
- "DEBUG: Using PDF parser"
- "DEBUG: Starting DYNAMIC PDF parsing"
"""

import requests
import json
import io
import os
from datetime import datetime

# Configuration - Use environment variable for backend URL
BACKEND_URL = os.getenv('REACT_APP_ROYALCERT_API_URL', 'https://royalcert-inspection-system-production.up.railway.app/api')
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class PDFUploadDebugTester:
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

    def create_sample_pdf(self):
        """Create a simple PDF file for testing"""
        print("\n📄 Creating Sample PDF for Testing...")
        
        try:
            # Create a simple PDF content (minimal PDF structure)
            pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(FORKLIFT MUAYENE FORMU) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF"""
            
            print("✅ Sample PDF created successfully")
            return pdf_content
            
        except Exception as e:
            print(f"❌ Failed to create sample PDF: {str(e)}")
            return None

    def test_pdf_upload(self, pdf_content, filename="FORKLIFT_MUAYENE_FORMU.pdf"):
        """Test PDF upload to the endpoint"""
        print(f"\n📤 Testing PDF Upload: {filename}")
        
        try:
            # Prepare file for upload
            files = {
                'file': (filename, pdf_content, 'application/pdf')
            }
            
            print(f"   Uploading file: {filename}")
            print(f"   File size: {len(pdf_content)} bytes")
            print(f"   Content type: application/pdf")
            
            # Upload the PDF
            response = self.session.post(f"{BACKEND_URL}/equipment-templates/upload", files=files)
            
            print(f"\n📊 Upload Response:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    print("✅ PDF upload successful!")
                    print(f"   Response data keys: {list(response_data.keys())}")
                    
                    if 'template' in response_data:
                        template = response_data['template']
                        print(f"   Template created:")
                        print(f"     - Name: {template.get('name', 'N/A')}")
                        print(f"     - Equipment Type: {template.get('equipment_type', 'N/A')}")
                        print(f"     - Template Type: {template.get('template_type', 'N/A')}")
                        print(f"     - Categories: {len(template.get('categories', []))}")
                        
                        # Count control items
                        total_items = 0
                        for category in template.get('categories', []):
                            total_items += len(category.get('items', []))
                        print(f"     - Total Control Items: {total_items}")
                    
                    return True, response_data
                    
                except json.JSONDecodeError:
                    print("✅ PDF upload successful (non-JSON response)")
                    print(f"   Response text: {response.text[:200]}...")
                    return True, response.text
                    
            elif response.status_code == 400:
                print("❌ PDF upload failed with 400 Bad Request")
                print(f"   Error message: {response.text}")
                return False, response.text
                
            elif response.status_code == 401:
                print("❌ PDF upload failed with 401 Unauthorized")
                print(f"   Error message: {response.text}")
                return False, response.text
                
            elif response.status_code == 403:
                print("❌ PDF upload failed with 403 Forbidden")
                print(f"   Error message: {response.text}")
                return False, response.text
                
            elif response.status_code == 500:
                print("❌ PDF upload failed with 500 Internal Server Error")
                print(f"   Error message: {response.text}")
                return False, response.text
                
            else:
                print(f"❌ PDF upload failed with status {response.status_code}")
                print(f"   Error message: {response.text}")
                return False, response.text
                
        except Exception as e:
            print(f"❌ PDF upload error: {str(e)}")
            return False, str(e)

    def test_different_pdf_filenames(self, pdf_content):
        """Test PDF upload with different filenames to check equipment type detection"""
        print("\n🔄 Testing Different PDF Filenames...")
        
        test_filenames = [
            "FORKLIFT_MUAYENE_FORMU.pdf",
            "CARASKAL_MUAYENE_RAPORU.pdf", 
            "VINC_MUAYENE_FORMU.pdf",
            "ISKELE_MUAYENE_RAPORU.pdf",
            "UNKNOWN_EQUIPMENT.pdf"
        ]
        
        results = {}
        
        for filename in test_filenames:
            print(f"\n   Testing filename: {filename}")
            success, response_data = self.test_pdf_upload(pdf_content, filename)
            results[filename] = {
                'success': success,
                'response': response_data
            }
            
            # Small delay between uploads
            import time
            time.sleep(1)
        
        return results

    def check_backend_logs_instructions(self):
        """Provide instructions for checking backend logs"""
        print("\n📋 Backend Logs Check Instructions:")
        print("=" * 60)
        print("To check if the debug messages are appearing in backend logs:")
        print("")
        print("1. SSH into the server or access the container")
        print("2. Check supervisor logs:")
        print("   tail -f /var/log/supervisor/backend.*.log")
        print("")
        print("3. Look for these specific debug messages:")
        print("   - 'DEBUG: Upload filename: [filename]'")
        print("   - 'DEBUG: Using PDF parser'") 
        print("   - 'DEBUG: Starting DYNAMIC PDF parsing'")
        print("")
        print("4. If messages don't appear, check:")
        print("   - Is the upload endpoint being reached?")
        print("   - Are there any errors before the debug messages?")
        print("   - Is the PDF file being processed correctly?")

    def run_pdf_upload_debug_test(self):
        """Run complete PDF upload debug test"""
        print("🚀 Starting PDF Upload Debug Test")
        print("=" * 80)
        
        test_results = {}
        
        # Step 1: Authentication
        test_results['authentication'] = self.authenticate()
        if not test_results['authentication']:
            print("\n❌ Cannot proceed without authentication")
            return test_results
        
        # Step 2: Create sample PDF
        pdf_content = self.create_sample_pdf()
        if not pdf_content:
            print("\n❌ Cannot proceed without sample PDF")
            test_results['pdf_creation'] = False
            return test_results
        
        test_results['pdf_creation'] = True
        
        # Step 3: Test single PDF upload
        print("\n" + "="*50)
        print("PHASE 1: SINGLE PDF UPLOAD TEST")
        print("="*50)
        
        success, response_data = self.test_pdf_upload(pdf_content)
        test_results['single_upload'] = success
        
        # Step 4: Test multiple filenames
        print("\n" + "="*50)
        print("PHASE 2: MULTIPLE FILENAME TEST")
        print("="*50)
        
        filename_results = self.test_different_pdf_filenames(pdf_content)
        test_results['multiple_filenames'] = filename_results
        
        # Step 5: Backend logs instructions
        print("\n" + "="*50)
        print("PHASE 3: BACKEND LOGS CHECK")
        print("="*50)
        
        self.check_backend_logs_instructions()
        
        # Final Summary
        print("\n" + "=" * 80)
        print("📋 PDF UPLOAD DEBUG TEST SUMMARY")
        print("=" * 80)
        
        print(f"Authentication: {'✅ PASS' if test_results['authentication'] else '❌ FAIL'}")
        print(f"PDF Creation: {'✅ PASS' if test_results['pdf_creation'] else '❌ FAIL'}")
        print(f"Single Upload: {'✅ PASS' if test_results['single_upload'] else '❌ FAIL'}")
        
        # Multiple filename results
        successful_uploads = sum(1 for result in filename_results.values() if result['success'])
        total_uploads = len(filename_results)
        print(f"Multiple Filenames: {successful_uploads}/{total_uploads} successful")
        
        # Detailed filename results
        print(f"\n📊 Detailed Filename Results:")
        for filename, result in filename_results.items():
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            print(f"   {filename:<30} {status}")
            if not result['success']:
                error_msg = str(result['response'])[:100]
                print(f"      Error: {error_msg}...")
        
        # Key findings
        print(f"\n🔍 Key Findings:")
        
        if test_results['single_upload']:
            print("   ✅ PDF upload endpoint is reachable and functional")
            print("   ✅ Authentication is working correctly")
            print("   ✅ PDF files are being accepted by the server")
        else:
            print("   ❌ PDF upload is failing - check error messages above")
            print("   ❌ This indicates a problem with the upload endpoint or PDF processing")
        
        # Next steps
        print(f"\n🎯 Next Steps:")
        if test_results['single_upload']:
            print("   1. Check backend logs for the debug messages mentioned above")
            print("   2. Verify that PDF parsing is working correctly")
            print("   3. Check if control items are being extracted properly")
        else:
            print("   1. Fix the upload endpoint issues first")
            print("   2. Check server logs for detailed error messages")
            print("   3. Verify PDF file format and content requirements")
        
        print(f"\n📋 Debug Messages to Look For:")
        print("   - 'DEBUG: Upload filename: [filename]'")
        print("   - 'DEBUG: Using PDF parser'")
        print("   - 'DEBUG: Starting DYNAMIC PDF parsing'")
        
        return test_results

if __name__ == "__main__":
    tester = PDFUploadDebugTester()
    results = tester.run_pdf_upload_debug_test()