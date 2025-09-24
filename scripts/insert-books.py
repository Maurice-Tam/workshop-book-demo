#!/usr/bin/env python3
import json
import requests
import hashlib
import hmac
import base64
from urllib.parse import quote
from datetime import datetime
import time

# CosmosDB Configuration
COSMOS_ENDPOINT = "https://book-library-cosmos.documents.azure.com"
COSMOS_KEY = "fuiY1a2uIkWx7ROGCCAiGIwlBKqW1sVT2bM08X7KvDT5VNFzWLi8KTQjdNdOcgJeGrFN9KNDyJdHACDbFo7MIA=="
DATABASE_ID = "BookLibraryDB"
CONTAINER_ID = "Books"

def generate_auth_signature(verb, resource_type, resource_id, date, key):
    """Generate the authorization signature for CosmosDB REST API"""
    # Create the payload
    payload = f"{verb.lower()}\n{resource_type.lower()}\n{resource_id}\n{date.lower()}\n\n"

    # Decode the key
    key_bytes = base64.b64decode(key)

    # Create HMAC
    signature = hmac.new(key_bytes, payload.encode('utf-8'), hashlib.sha256).digest()

    # Encode to base64
    signature_b64 = base64.b64encode(signature).decode('utf-8')

    # Return authorization header
    return f"type=master&ver=1.0&sig={signature_b64}"

def insert_document(document):
    """Insert a document into CosmosDB"""
    # Create the request URL
    url = f"{COSMOS_ENDPOINT}/dbs/{DATABASE_ID}/colls/{CONTAINER_ID}/docs"

    # Create the date header
    date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    # Create resource ID for authorization
    resource_id = f"dbs/{DATABASE_ID}/colls/{CONTAINER_ID}"

    # Generate authorization header
    auth_header = generate_auth_signature("POST", "docs", resource_id, date, COSMOS_KEY)

    # Create headers
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json',
        'x-ms-date': date,
        'x-ms-version': '2020-07-15',
        'x-ms-documentdb-partitionkey': f'["{document["category"]}"]'
    }

    # Make the request
    response = requests.post(url, headers=headers, json=document)

    return response

def main():
    """Insert all book records"""
    books = [
        "../data/book001.json",
        "../data/book002.json",
        "../data/book003.json",
        "../data/book004.json",
        "../data/book005.json"
    ]

    successful_inserts = 0

    for book_file in books:
        try:
            # Read the book data
            with open(book_file, 'r') as f:
                book_data = json.load(f)

            print(f"Inserting {book_data['title']}...")

            # Insert the document
            response = insert_document(book_data)

            if response.status_code == 201:
                print(f"✅ Successfully inserted: {book_data['title']}")
                successful_inserts += 1
            else:
                print(f"❌ Failed to insert {book_data['title']}: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"❌ Error processing {book_file}: {str(e)}")

        # Small delay between requests
        time.sleep(0.5)

    print(f"\n📊 Summary: {successful_inserts}/{len(books)} books inserted successfully")

if __name__ == "__main__":
    main()