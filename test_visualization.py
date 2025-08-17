#!/usr/bin/env python3
"""
Test script for visualization functionality
"""

import requests
import json
import os

def test_visualization_functionality():
    base_url = "http://localhost:5000"
    session = requests.Session()

    print("🧪 Testing Sigmatic Visualization Functionality")
    print("=" * 60)

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

    # Test 2: Test scatter plot visualization
    print("\n2. Testing scatter plot visualization...")
    query_data = {"query": "Create a scatter plot of age vs weight"}
    response = session.post(f"{base_url}/visualize", json=query_data)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Scatter plot visualization created successfully")
            print(f"   - Chart type: {result['chart_type']}")
            print(f"   - Chart data keys: {list(result['chart'].keys())}")
        else:
            print(f"❌ Visualization failed: {result['error']}")
    else:
        print(f"❌ Visualization request failed: {response.status_code}")

    # Test 3: Test bar chart visualization
    print("\n3. Testing bar chart visualization...")
    query_data = {"query": "Create a bar chart showing gender distribution"}
    response = session.post(f"{base_url}/visualize", json=query_data)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ Bar chart visualization created successfully")
            print(f"   - Chart type: {result['chart_type']}")
        else:
            print(f"❌ Visualization failed: {result['error']}")
    else:
        print(f"❌ Visualization request failed: {response.status_code}")

    # Test 4: Test dashboard functionality
    print("\n4. Testing dashboard functionality...")
    
    # Get current dashboard
    response = session.get(f"{base_url}/dashboard")
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print(f"✅ Dashboard retrieved successfully")
            print(f"   - Current charts: {len(result['charts'])}")
        else:
            print(f"❌ Dashboard retrieval failed: {result['error']}")
    else:
        print(f"❌ Dashboard request failed: {response.status_code}")

    print("\n" + "=" * 60)
    print("🎉 Visualization testing completed!")

if __name__ == "__main__":
    test_visualization_functionality() 