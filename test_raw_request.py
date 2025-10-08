import httpx
import asyncio

# Read API key from .env
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('YOU_API_KEY='):
            API_KEY = line.split('=', 1)[1].strip()
            break

print(f"API Key: {API_KEY}")
print(f"API Key length: {len(API_KEY)}")
print(f"First 30 chars: {API_KEY[:30]}")
print(f"Last 30 chars: {API_KEY[-30:]}")

async def test():
    async with httpx.AsyncClient() as client:
        # Try the exact request format from You.com docs
        response = await client.get(
            "https://api.ydc-index.io/search",
            headers={"X-API-Key": API_KEY},
            params={"query": "test"}
        )
        print(f"\nResponse status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response body: {response.text[:500]}")

asyncio.run(test())
