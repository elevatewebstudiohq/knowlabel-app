#!/usr/bin/env python3
"""Printify API wrapper for ThePetParentStore."""
import json
import urllib.request
import urllib.error

SECRETS_FILE = '/home/node/.openclaw/workspace/automation/secrets.json'
BASE_URL = 'https://api.printify.com/v1'

def get_api_key():
    with open(SECRETS_FILE) as f:
        return json.load(f)['printify_api_key']

def api_request(method, endpoint, data=None):
    key = get_api_key()
    url = BASE_URL + endpoint
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f'HTTP {e.code}: {error_body}')
        return None
    except Exception as e:
        print(f'Error: {e}')
        return None

if __name__ == '__main__':
    print('Testing Printify API connection...')
    result = api_request('GET', '/shops.json')
    if result:
        print(f'Connected! Found {len(result)} shop(s):')
        for shop in result:
            print(f'  - {shop["title"]} (ID: {shop["id"]})')
    else:
        print('Connection failed.')
