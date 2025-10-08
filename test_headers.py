import httpx
import asyncio

# Read API key from .env
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('YOU_API_KEY='):
            API_KEY = line.split('=', 1)[1].strip()
            break

async def test_headers():
    async with httpx.AsyncClient() as client:
        # Test what headers httpx sends
        request = client.build_request(
            "GET",
            "https://api.ydc-index.io/v2/search",
            headers={"X-API-Key": API_KEY},
            params={"query": "test"}
        )
        
        print("Headers being sent:")
        for key, value in request.headers.items():
            if key.lower() == 'x-api-key':
                print(f"  {key}: {value[:30]}...")
            else:
                print(f"  {key}: {value}")
        
        # Actually send the request
        print("\nSending request...")
        response = await client.send(request)
        print(f"Status: {response.status_code}")

asyncio.run(test_headers())
