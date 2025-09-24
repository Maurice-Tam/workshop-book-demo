#!/usr/bin/env python3
import json
import os
from azure.cosmos import CosmosClient

def main():
    """Insert all book records using Azure Cosmos SDK"""

    # Get connection string from Azure CLI
    import subprocess
    result = subprocess.run(['az', 'cosmosdb', 'keys', 'list', '--name', 'book-library-cosmos',
                           '--resource-group', 'dev-swa-rg', '--type', 'connection-strings',
                           '--query', 'connectionStrings[0].connectionString', '--output', 'tsv'],
                          capture_output=True, text=True)
    connection_string = result.stdout.strip()

    # Initialize the Cosmos client
    client = CosmosClient.from_connection_string(connection_string)

    # Get database and container
    database = client.get_database_client("BookLibraryDB")
    container = database.get_container_client("Books")

    # List of book files
    books = [
        "book001.json",
        "book002.json",
        "book003.json",
        "book004.json",
        "book005.json"
    ]

    successful_inserts = 0

    for book_file in books:
        try:
            # Read the book data
            with open(book_file, 'r') as f:
                book_data = json.load(f)

            print(f"Inserting: {book_data['title']}")

            # Insert the document
            response = container.create_item(body=book_data)

            print(f"✅ Successfully inserted: {book_data['title']} (ID: {response['id']})")
            successful_inserts += 1

        except Exception as e:
            print(f"❌ Error inserting {book_file}: {str(e)}")

    print(f"\n📊 Summary: {successful_inserts}/{len(books)} books inserted successfully")

    # Query to verify insertion
    print("\n📚 Verifying inserted books:")
    try:
        query = "SELECT c.id, c.title, c.category FROM c ORDER BY c.title"
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        for item in items:
            print(f"  - {item['title']} (ID: {item['id']}, Category: {item['category']})")

    except Exception as e:
        print(f"❌ Error querying books: {str(e)}")

if __name__ == "__main__":
    main()