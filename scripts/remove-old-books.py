#!/usr/bin/env python3
import subprocess
from azure.cosmos import CosmosClient

def main():
    """Remove old books (book001-book015) from CosmosDB"""

    print("🧹 Removing old books (book001-book015) from CosmosDB...")

    # Get connection string from Azure CLI
    result = subprocess.run(['az', 'cosmosdb', 'keys', 'list', '--name', 'book-library-cosmos',
                           '--resource-group', 'dev-swa-rg', '--type', 'connection-strings',
                           '--query', 'connectionStrings[0].connectionString', '--output', 'tsv'],
                          capture_output=True, text=True)
    connection_string = result.stdout.strip()

    # Initialize the Cosmos client
    client = CosmosClient.from_connection_string(connection_string)
    database = client.get_database_client("BookLibraryDB")
    container = database.get_container_client("Books")

    # Books to delete (book001 through book015)
    books_to_delete = [f"book{i:03d}" for i in range(1, 16)]

    deleted_count = 0
    for book_id in books_to_delete:
        try:
            # First, get the book to find its category (partition key)
            query = f"SELECT c.id, c.category FROM c WHERE c.id = '{book_id}'"
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))

            if items:
                book = items[0]
                category = book.get('category', '')

                # Delete the book using its category as partition key
                container.delete_item(item=book_id, partition_key=category)
                print(f"✅ Deleted {book_id} (category: {category})")
                deleted_count += 1
            else:
                print(f"⚠️  Book {book_id} not found")

        except Exception as e:
            print(f"❌ Error deleting {book_id}: {str(e)}")

    print(f"\n🎯 Successfully deleted {deleted_count}/{len(books_to_delete)} old books")

if __name__ == "__main__":
    main()