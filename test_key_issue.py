# Read API key from .env
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('YOU_API_KEY='):
            raw_key = line.split('=', 1)[1].strip()
            # Remove quotes if present
            clean_key = raw_key.strip("'\"")
            print(f"Raw key: {raw_key[:40]}")
            print(f"Clean key: {clean_key[:40]}")
            print(f"First char raw: {repr(raw_key[0])}")
            print(f"First char clean: {repr(clean_key[0])}")
            break
