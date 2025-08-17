#!/usr/bin/env python3
"""
Test script to specifically test date handling issues
"""

import requests
import json

def test_date_handling():
    base_url = "http://localhost:5000"
    session = requests.Session()

    print("🧪 Testing Date Handling")
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

    # Test 2: Query involving date operations
    print("\n2. Testing date-based query...")
    query_data = {"query": "Show me patients with birth dates"}
    response = session.post(f"{base_url}/query", json=query_data)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Date query processed successfully")
            print(f"   - Report: {result['report'][:100]}...")
            if result['result']:
                print(f"   - Result type: {result['result']['type']}")
        else:
            print(f"❌ Query failed: {result['error']}")
    else:
        print(f"❌ Query request failed: {response.status_code}")

    # Test 3: Query with date filtering
    print("\n3. Testing date filtering query...")
    query_data = {"query": "Show me patients born after 1950"}
    response = session.post(f"{base_url}/query", json=query_data)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Date filtering query processed successfully")
            print(f"   - Report: {result['report'][:100]}...")
        else:
            print(f"❌ Query failed: {result['error']}")
    else:
        print(f"❌ Query request failed: {response.status_code}")

    # Test 4: Query with age calculation
    print("\n4. Testing age calculation query...")
    query_data = {"query": "Calculate patient ages based on birth dates"}
    response = session.post(f"{base_url}/query", json=query_data)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Age calculation query processed successfully")
            print(f"   - Report: {result['report'][:100]}...")
        else:
            print(f"❌ Query failed: {result['error']}")
    else:
        print(f"❌ Query request failed: {response.status_code}")

    print("\n" + "=" * 50)
    print("🎉 Date handling testing completed!")

if __name__ == "__main__":
    test_date_handling() 