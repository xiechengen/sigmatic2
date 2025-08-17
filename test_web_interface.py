#!/usr/bin/env python3
"""
Test script to simulate web interface behavior and check session persistence
"""

import requests
import json

def test_web_interface_flow():
    base_url = "http://localhost:5000"
    session = requests.Session()

    print("🧪 Testing Web Interface Flow")
    print("=" * 50)

    # Test 1: Upload adverse events file (simulating web interface)
    print("\n1. Uploading adverse events file...")
    with open('sample_data/ae.csv', 'rb') as f:
        files = {'file': ('ae.csv', f, 'text/csv')}
        response = session.post(f"{base_url}/upload", files=files)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Adverse events file uploaded successfully")
        else:
            print(f"❌ Upload failed: {result['error']}")
            return
    else:
        print(f"❌ Upload request failed: {response.status_code}")
        return

    # Test 2: Check if files are listed (simulating web interface)
    print("\n2. Checking uploaded files...")
    response = session.get(f"{base_url}/files")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Files listed successfully: {len(result['files'])} files")
        for file in result['files']:
            print(f"   - {file['filename']}: {file['rows']} rows, {file['columns']} columns")
    else:
        print(f"❌ Files request failed: {response.status_code}")

    # Test 3: Query for adverse events summary (simulating web interface)
    print("\n3. Testing adverse events summary query...")
    query_data = {"query": "provide the table summary of adverse event"}
    response = session.post(f"{base_url}/query", json=query_data)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Adverse events summary query processed successfully")
            print(f"   - Report: {result['report'][:100]}...")
            if result['result']:
                print(f"   - Result type: {result['result']['type']}")
        else:
            print(f"❌ Query failed: {result['error']}")
    else:
        print(f"❌ Query request failed: {response.status_code}")

    # Test 4: Test without session (simulating new browser tab)
    print("\n4. Testing without session (new browser tab simulation)...")
    new_session = requests.Session()
    query_data = {"query": "provide the table summary of adverse event"}
    response = new_session.post(f"{base_url}/query", json=query_data)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Query succeeded in new session (unexpected)")
        else:
            print(f"❌ Query failed in new session: {result['error']}")
    else:
        print(f"❌ Query request failed: {response.status_code}")

    print("\n" + "=" * 50)
    print("🎉 Web interface flow testing completed!")

if __name__ == "__main__":
    test_web_interface_flow() 