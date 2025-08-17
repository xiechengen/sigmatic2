#!/usr/bin/env python3
"""
Test script to demonstrate debugging features
"""

import requests
import json

def test_debugging_features():
    base_url = "http://localhost:5000"
    session = requests.Session()

    print("🧪 Testing Debugging Features")
    print("=" * 50)

    # Test 1: Upload sample data
    print("\n1. Uploading sample data...")
    with open('sample_data/dm.csv', 'rb') as f:
        files = {'file': ('dm.csv', f, 'text/csv')}
        response = session.post(f"{base_url}/upload", files=files)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Sample data uploaded successfully")
        else:
            print(f"❌ Upload failed: {result['error']}")
            return
    else:
        print(f"❌ Upload request failed: {response.status_code}")
        return

    # Test 2: Query that might fail (to see debugging output)
    print("\n2. Testing query that might fail...")
    query_data = {"query": "show me patients with age greater than 100"}
    response = session.post(f"{base_url}/query", json=query_data)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Query processed successfully")
            print(f"   - Report: {result['report'][:100]}...")
            if result['pandas_code']:
                print(f"   - Generated pandas code: {result['pandas_code'][:100]}...")
        else:
            print(f"❌ Query failed: {result['error']}")
            # Check if it contains debugging info
            if 'Generated code:' in result['error']:
                print("   - Debugging info included in error message")
    else:
        print(f"❌ Query request failed: {response.status_code}")

    print("\n" + "=" * 50)
    print("🎉 Debugging features testing completed!")

if __name__ == "__main__":
    test_debugging_features() 