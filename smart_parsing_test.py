#!/usr/bin/env python3
"""
SMART Word Parsing Algorithm Test - FORKLIFT Templates
Tests the improved Word document parsing algorithm for FORKLIFT documents
"""

import requests
import json

# Configuration
BACKEND_URL = "https://405a5b7a-3c02-4793-9fcc-5203d2944620.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# FORKLIFT Document URLs for testing
FORKLIFT_DOCUMENTS = {
    "FORKLIFT_MUAYENE_FORMU": "https://customer-assets.emergentagent.com/job_periodic-check/artifacts/y9b9lejo_RC-M-%C4%B0E-FR24_5%20FORKL%C4%B0FT%20MUAYENE%20FORMU.docx",
    "FORKLIFT_MUAYENE_RAPORU": "https://customer-assets.emergentagent.com/job_periodic-check/artifacts/00vmxy69_RC-M-%C4%B0E-FR25_6%20FORKL%C4%B0FT%20MUAYENE%20RAPORU.docx"
}

def authenticate():
    """Authenticate with admin credentials"""
    print("🔐 Testing Authentication...")
    
    session = requests.Session()
    login_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    print(f"Login Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        user_info = data["user"]
        
        # Set authorization header for future requests
        session.headers.update({
            "Authorization": f"Bearer {token}"
        })
        
        print(f"✅ Authentication successful")
        print(f"   User: {user_info['full_name']} ({user_info['role']})")
        return session, True
    else:
        print(f"❌ Authentication failed: {response.text}")
        return session, False

def check_existing_forklift_templates(session):
    """Check for existing FORKLIFT templates"""
    print("\n🔍 Checking for Existing FORKLIFT Templates...")
    
    response = session.get(f"{BACKEND_URL}/equipment-templates")
    print(f"Equipment Templates Status: {response.status_code}")
    
    if response.status_code == 200:
        templates_data = response.json()
        
        # Find FORKLIFT templates
        forklift_templates = [t for t in templates_data if t.get('equipment_type') == 'FORKLIFT']
        
        print(f"✅ Found {len(forklift_templates)} existing FORKLIFT templates")
        
        for template in forklift_templates:
            template_type = template.get('template_type', 'UNKNOWN')
            template_name = template.get('name', 'UNNAMED')
            total_items = sum(len(cat.get('items', [])) for cat in template.get('categories', []))
            print(f"   - {template_name} ({template_type}): {total_items} control items")
        
        return forklift_templates
    else:
        print(f"❌ Failed to get templates: {response.text}")
        return []

def clean_existing_forklift_templates(session, existing_templates):
    """Delete existing FORKLIFT templates to test fresh parsing"""
    print("\n🧹 Cleaning Existing FORKLIFT Templates...")
    
    if not existing_templates:
        print("✅ No existing FORKLIFT templates to clean")
        return True
    
    deleted_count = 0
    
    for template in existing_templates:
        template_id = template.get('id')
        template_name = template.get('name', 'UNNAMED')
        
        response = session.delete(f"{BACKEND_URL}/equipment-templates/{template_id}")
        
        if response.status_code == 200:
            print(f"✅ Deleted template: {template_name}")
            deleted_count += 1
        else:
            print(f"❌ Failed to delete template {template_name}: {response.text}")
    
    print(f"✅ Cleaned {deleted_count}/{len(existing_templates)} FORKLIFT templates")
    return deleted_count == len(existing_templates)

def test_forklift_document_upload(session, doc_name, doc_url):
    """Download and upload a FORKLIFT document for parsing"""
    print(f"\n📥 Testing {doc_name} Upload and Parsing...")
    
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
    upload_response = session.post(f"{BACKEND_URL}/equipment-templates/upload", files=files)
    
    print(f"Upload Response Status: {upload_response.status_code}")
    
    if upload_response.status_code == 200:
        upload_data = upload_response.json()
        print("✅ Document uploaded and parsed successfully")
        
        # Extract parsing results from the simplified response
        template_data = upload_data.get('template', {})
        equipment_type = template_data.get('equipment_type', 'UNKNOWN')
        template_type = template_data.get('template_type', 'UNKNOWN')
        template_name = template_data.get('name', 'UNNAMED')
        total_items = template_data.get('total_items', 0)
        categories_count = template_data.get('categories', 0)
        
        print(f"   Equipment Type: {equipment_type}")
        print(f"   Template Type: {template_type}")
        print(f"   Template Name: {template_name}")
        print(f"   Categories: {categories_count}")
        print(f"   Total Control Items: {total_items}")
        
        # Verify reasonable control item count (50-60 max as per requirement)
        if total_items <= 60:
            print(f"✅ Control item count is reasonable: {total_items} ≤ 60")
        else:
            print(f"❌ Control item count too high: {total_items} > 60")
        
        # Check if it's in the expected range (50-53)
        if 50 <= total_items <= 53:
            print(f"✅ PERFECT: Control item count in expected range: {total_items}")
        elif total_items <= 60:
            print(f"✅ ACCEPTABLE: Control item count within limit: {total_items}")
        else:
            print(f"❌ TOO HIGH: Control item count exceeds limit: {total_items}")
        
        result_data = {
            'equipment_type': equipment_type,
            'template_type': template_type,
            'template_name': template_name,
            'total_items': total_items,
            'categories_count': categories_count,
            'template_id': template_data.get('id')
        }
        
        return True, result_data
    else:
        print(f"❌ Document upload failed: {upload_response.text}")
        return False, None

def test_duplicate_prevention(session, doc_name, doc_url):
    """Test that duplicate templates are prevented"""
    print(f"\n🚫 Testing Duplicate Prevention for {doc_name}...")
    
    # Try to upload the same document again
    doc_response = requests.get(doc_url)
    if doc_response.status_code != 200:
        print(f"❌ Failed to download document for duplicate test")
        return False
    
    filename = doc_name.replace('_', ' ') + '.docx'
    files = {
        'file': (filename, doc_response.content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    }
    
    upload_response = session.post(f"{BACKEND_URL}/equipment-templates/upload", files=files)
    
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

def verify_final_template_state(session):
    """Verify final state of FORKLIFT templates"""
    print("\n📊 Verifying Final Template State...")
    
    response = session.get(f"{BACKEND_URL}/equipment-templates")
    
    if response.status_code == 200:
        templates_data = response.json()
        forklift_templates = [t for t in templates_data if t.get('equipment_type') == 'FORKLIFT']
        
        print(f"✅ Final FORKLIFT templates count: {len(forklift_templates)}")
        
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
        
        return True, has_both_types
    else:
        print(f"❌ Failed to get final templates: {response.text}")
        return False, False

def main():
    """Run SMART Word parsing algorithm tests"""
    print("🚀 Starting SMART Word Parsing Algorithm Tests")
    print("=" * 80)
    
    # Step 1: Authentication
    session, auth_success = authenticate()
    if not auth_success:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Step 2: Check existing FORKLIFT templates
    existing_templates = check_existing_forklift_templates(session)
    
    # Step 3: Clean existing FORKLIFT templates
    clean_success = clean_existing_forklift_templates(session, existing_templates)
    
    # Step 4: Test improved Word document parsing
    parsing_results = {}
    duplicate_results = {}
    template_results = {}
    
    for doc_name, doc_url in FORKLIFT_DOCUMENTS.items():
        # Upload and parse document
        success, template_data = test_forklift_document_upload(session, doc_name, doc_url)
        parsing_results[doc_name] = success
        
        if success and template_data:
            template_results[doc_name] = template_data
            
            # Test duplicate prevention
            duplicate_results[doc_name] = test_duplicate_prevention(session, doc_name, doc_url)
    
    # Step 5: Verify final template state
    final_success, has_both_types = verify_final_template_state(session)
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 SMART WORD PARSING ALGORITHM TEST SUMMARY")
    print("=" * 80)
    
    # Overall results
    all_parsing_passed = all(parsing_results.values())
    all_duplicates_prevented = all(duplicate_results.values())
    
    print(f"Authentication: {'✅ PASS' if auth_success else '❌ FAIL'}")
    print(f"Clean Existing Templates: {'✅ PASS' if clean_success else '❌ FAIL'}")
    print(f"Document Parsing: {'✅ PASS' if all_parsing_passed else '❌ FAIL'}")
    print(f"Duplicate Prevention: {'✅ PASS' if all_duplicates_prevented else '❌ FAIL'}")
    print(f"Final Verification: {'✅ PASS' if final_success else '❌ FAIL'}")
    print(f"Has Both Template Types: {'✅ PASS' if has_both_types else '❌ FAIL'}")
    
    # Key findings
    print(f"\n🔍 KEY FINDINGS:")
    
    # Check control item counts from stored results
    for doc_name, template_data in template_results.items():
        total_items = template_data.get('total_items', 0)
        if 50 <= total_items <= 53:
            print(f"   {doc_name}: ✅ PERFECT count ({total_items} items)")
        elif total_items <= 60:
            print(f"   {doc_name}: ✅ ACCEPTABLE count ({total_items} items)")
        else:
            print(f"   {doc_name}: ❌ TOO HIGH count ({total_items} items)")
    
    # Expected outcome verification
    print(f"\n🎯 EXPECTED OUTCOME VERIFICATION:")
    print("   Expected: FORKLIFT templates with ~50-53 control items (max 60)")
    
    # Check if we achieved the expected outcome
    reasonable_counts = []
    for doc_name, template_data in template_results.items():
        total_items = template_data.get('total_items', 0)
        reasonable_counts.append(total_items <= 60)
        expected_range = 50 <= total_items <= 53
        print(f"   {doc_name}: {total_items} items ({'✅ PERFECT' if expected_range else '✅ ACCEPTABLE' if total_items <= 60 else '❌ TOO HIGH'})")
    
    overall_success = (auth_success and 
                      clean_success and
                      all_parsing_passed and
                      all_duplicates_prevented and
                      final_success and
                      has_both_types and
                      all(reasonable_counts))
    
    if overall_success:
        print(f"\n🎉 SMART WORD PARSING ALGORITHM TEST COMPLETED SUCCESSFULLY!")
        print("   ✅ Control item counts are reasonable (≤60 items)")
        print("   ✅ Both FORM and REPORT templates created")
        print("   ✅ Duplicate prevention is working")
        print("   ✅ Smart filtering algorithm is working correctly")
    else:
        print(f"\n⚠️  SOME TESTS FAILED - ALGORITHM NEEDS IMPROVEMENT")
    
    return overall_success

if __name__ == "__main__":
    main()