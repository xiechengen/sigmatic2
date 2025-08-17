#!/usr/bin/env python3
"""
Test script to specifically test adverse events queries
"""

import requests
import json

def test_adverse_events():
    base_url = "http://localhost:5000"
    session = requests.Session()

    print("🧪 Testing Adverse Events Queries")
    print("=" * 50)

    # Test 1: Upload adverse events file
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

    # Test 2: Query for adverse events summary
    print("\n2. Testing adverse events summary query...")
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

    # Test 3: Query for adverse events count
    print("\n3. Testing adverse events count query...")
    query_data = {"query": "how many adverse events are there"}
    response = session.post(f"{base_url}/query", json=query_data)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Adverse events count query processed successfully")
            print(f"   - Report: {result['report'][:100]}...")
        else:
            print(f"❌ Query failed: {result['error']}")
    else:
        print(f"❌ Query request failed: {response.status_code}")

    # Test 4: Query for adverse events by severity
    print("\n4. Testing adverse events by severity query...")
    query_data = {"query": "show me adverse events by severity"}
    response = session.post(f"{base_url}/query", json=query_data)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Adverse events by severity query processed successfully")
            print(f"   - Report: {result['report'][:100]}...")
        else:
            print(f"❌ Query failed: {result['error']}")
    else:
        print(f"❌ Query request failed: {response.status_code}")

    print("\n" + "=" * 50)
    print("🎉 Adverse events testing completed!")

if __name__ == "__main__":
    test_adverse_events() 