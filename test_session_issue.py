#!/usr/bin/env python3
"""
Test script to demonstrate session issue and provide solution
"""

import requests
import json

def test_session_issue():
    base_url = "http://localhost:5000"
    session = requests.Session()

    print("🧪 Testing Session Issue")
    print("=" * 50)

    # Test 1: Upload file with session
    print("\n1. Uploading file with session...")
    with open('sample_data/dm.csv', 'rb') as f:
        files = {'file': ('dm.csv', f, 'text/csv')}
        response = session.post(f"{base_url}/upload", files=files)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ File uploaded successfully with session")
        else:
            print(f"❌ Upload failed: {result['error']}")
            return
    else:
        print(f"❌ Upload request failed: {response.status_code}")
        return

    # Test 2: Check files with same session
    print("\n2. Checking files with same session...")
    response = session.get(f"{base_url}/files")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Files found: {len(result['files'])} files")
        for file in result['files']:
            print(f"   - {file['filename']}: {file['rows']} rows")
    else:
        print(f"❌ Files request failed: {response.status_code}")

    # Test 3: Query with same session
    print("\n3. Querying with same session...")
    query_data = {"query": "how many patients are there"}
    response = session.post(f"{base_url}/query", json=query_data)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Query successful with session")
        else:
            print(f"❌ Query failed: {result['error']}")
    else:
        print(f"❌ Query request failed: {response.status_code}")

    # Test 4: Query with NEW session (simulating new browser tab)
    print("\n4. Querying with NEW session (simulating new browser tab)...")
    new_session = requests.Session()
    query_data = {"query": "how many patients are there"}
    response = new_session.post(f"{base_url}/query", json=query_data)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Query successful with new session (unexpected)")
        else:
            print(f"❌ Query failed with new session: {result['error']}")
    else:
        print(f"❌ Query request failed: {response.status_code}")

    print("\n" + "=" * 50)
    print("🎯 SOLUTION:")
    print("The issue is that each browser tab/request needs to maintain the same session.")
    print("In the web interface:")
    print("1. Upload your files")
    print("2. Don't refresh the page")
    print("3. Don't open new tabs")
    print("4. Make sure you see the green '1 file loaded' indicator")
    print("5. Then ask your questions")

if __name__ == "__main__":
    test_session_issue() 