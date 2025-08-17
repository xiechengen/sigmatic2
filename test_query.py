#!/usr/bin/env python3
"""
Test script for natural language query functionality
"""

import requests
import json
import os

def test_query_functionality():
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print("🧪 Testing Sigmatic Natural Language Query Functionality")
    print("=" * 60)
    
    # Test 1: Upload demographics file
    print("\n1. Uploading demographics file...")
    with open('sample_data/dm.csv', 'rb') as f:
        files = {'file': ('dm.csv', f, 'text/csv')}
        response = session.post(f"{base_url}/upload", files=files)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Demographics file uploaded successfully")
            print(f"   - Rows: {result['file_info']['rows']}")
            print(f"   - Columns: {result['file_info']['columns']}")
        else:
            print(f"❌ Upload failed: {result['error']}")
            return
    else:
        print(f"❌ Upload request failed: {response.status_code}")
        return
    
    # Test 2: Upload adverse events file
    print("\n2. Uploading adverse events file...")
    with open('sample_data/ae.csv', 'rb') as f:
        files = {'file': ('ae.csv', f, 'text/csv')}
        response = session.post(f"{base_url}/upload", files=files)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Adverse events file uploaded successfully")
            print(f"   - Rows: {result['file_info']['rows']}")
            print(f"   - Columns: {result['file_info']['columns']}")
        else:
            print(f"❌ Upload failed: {result['error']}")
    else:
        print(f"❌ Upload request failed: {response.status_code}")
    
    # Test 3: Simple count query
    print("\n3. Testing simple count query...")
    query_data = {"query": "How many patients are there?"}
    response = session.post(f"{base_url}/query", json=query_data)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Query processed successfully")
            print(f"   - Report: {result['report'][:100]}...")
            if result['result']:
                print(f"   - Result type: {result['result']['type']}")
                if result['result']['type'] == 'scalar':
                    print(f"   - Count: {result['result']['value']}")
        else:
            print(f"❌ Query failed: {result['error']}")
    else:
        print(f"❌ Query request failed: {response.status_code}")
    
    # Test 4: Age-based query
    print("\n4. Testing age-based query...")
    query_data = {"query": "Show me patients over 70 years old"}
    response = session.post(f"{base_url}/query", json=query_data)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Age query processed successfully")
            print(f"   - Report: {result['report'][:100]}...")
            if result['result'] and result['result']['type'] == 'dataframe':
                print(f"   - Found {result['result']['total_rows']} patients over 70")
        else:
            print(f"❌ Query failed: {result['error']}")
    else:
        print(f"❌ Query request failed: {response.status_code}")
    
    # Test 5: Death analysis query
    print("\n5. Testing death analysis query...")
    query_data = {"query": "How many patients died during the study?"}
    response = session.post(f"{base_url}/query", json=query_data)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Death analysis query processed successfully")
            print(f"   - Report: {result['report'][:100]}...")
        else:
            print(f"❌ Query failed: {result['error']}")
    else:
        print(f"❌ Query request failed: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎉 Testing completed!")

if __name__ == "__main__":
    test_query_functionality() 