import httpx
import asyncio
import json

# Read API key directly from .env file
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('YOU_API_KEY='):
            API_KEY = line.split('=', 1)[1].strip()
            break

YOU_API_BASE = "https://api.ydc-index.io"

async def test_nvidia_search():
    print("Searching for latest NVIDIA news...\n")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {"X-API-Key": API_KEY}
            params = {"query": "latest NVIDIA news"}
            
            response = await client.get(
                f"{YOU_API_BASE}/v2/search",
                headers=headers,
                params=params,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Search successful!")
                print(f"\nFull response:")
                print(json.dumps(data, indent=2))
            else:
                print(f"✗ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"✗ Exception: {e}")

asyncio.run(test_nvidia_search())
