#!/usr/bin/env python3
"""
Test script to specifically test string concatenation issues
"""

import requests
import json

def test_string_concat_issue():
    base_url = "http://localhost:5000"
    session = requests.Session()

    print("🧪 Testing String Concatenation Issue")
    print("=" * 50)

    # Test 1: Upload demographics file
    print("\n1. Uploading demographics file...")
    with open('sample_data/dm.csv', 'rb') as f:
        files = {'file': ('dm.csv', f, 'text/csv')}
        response = session.post(f"{base_url}/upload", files=files)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Demographics file uploaded successfully")
        else:
            print(f"❌ Upload failed: {result['error']}")
            return
    else:
        print(f"❌ Upload request failed: {response.status_code}")
        return

    # Test 2: Query that might trigger string concatenation
    print("\n2. Testing query that might trigger string concatenation...")
    query_data = {"query": "Show me patients with age and weight information combined"}
    response = session.post(f"{base_url}/query", json=query_data)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Query processed successfully")
            print(f"   - Report: {result['report'][:100]}...")
            if result['result']:
                print(f"   - Result type: {result['result']['type']}")
        else:
            print(f"❌ Query failed: {result['error']}")
    else:
        print(f"❌ Query request failed: {response.status_code}")

    # Test 3: Another potentially problematic query
    print("\n3. Testing another potentially problematic query...")
    query_data = {"query": "Create a summary combining patient ID and age"}
    response = session.post(f"{base_url}/query", json=query_data)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Query processed successfully")
            print(f"   - Report: {result['report'][:100]}...")
        else:
            print(f"❌ Query failed: {result['error']}")
    else:
        print(f"❌ Query request failed: {response.status_code}")

    print("\n" + "=" * 50)
    print("🎉 String concatenation testing completed!")

if __name__ == "__main__":
    test_string_concat_issue() 