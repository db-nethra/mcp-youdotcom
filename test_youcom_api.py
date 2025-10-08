import httpx
import asyncio

# Read API key directly from .env file
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('YOU_API_KEY='):
            API_KEY = line.split('=', 1)[1].strip()
            break

YOU_API_BASE = "https://api.ydc-index.io"

async def test_search():
    print(f"Testing with API key: {API_KEY[:30]}...")
    print(f"Key length: {len(API_KEY)}")
    
    # Test v2/search
    print("\n1. Testing /v2/search...")
    async with httpx.AsyncClient() as client:
        try:
            headers = {"X-API-Key": API_KEY}
            params = {"query": "Python programming"}
            
            response = await client.get(
                f"{YOU_API_BASE}/v2/search",
                headers=headers,
                params=params,
                timeout=30.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✓ Success! Got results")
                data = response.json()
                print(f"   Keys in response: {list(data.keys())[:5]}")
            else:
                print(f"   ✗ Error: {response.text[:200]}")
        except Exception as e:
            print(f"   ✗ Exception: {e}")
    
    # Test v1/search
    print("\n2. Testing /v1/search...")
    async with httpx.AsyncClient() as client:
        try:
            headers = {"X-API-Key": API_KEY}
            params = {"query": "Python programming"}
            
            response = await client.get(
                f"{YOU_API_BASE}/v1/search",
                headers=headers,
                params=params,
                timeout=30.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✓ Success! Got results")
                data = response.json()
                print(f"   Keys in response: {list(data.keys())[:5]}")
            else:
                print(f"   ✗ Error: {response.text[:200]}")
        except Exception as e:
            print(f"   ✗ Exception: {e}")
    
    # Test /search without version
    print("\n3. Testing /search...")
    async with httpx.AsyncClient() as client:
        try:
            headers = {"X-API-Key": API_KEY}
            params = {"query": "Python programming"}
            
            response = await client.get(
                f"{YOU_API_BASE}/search",
                headers=headers,
                params=params,
                timeout=30.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✓ Success! Got results")
                data = response.json()
                print(f"   Keys in response: {list(data.keys())[:5]}")
            else:
                print(f"   ✗ Error: {response.text[:200]}")
        except Exception as e:
            print(f"   ✗ Exception: {e}")

asyncio.run(test_search())
