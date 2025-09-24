#!/usr/bin/env python3
import subprocess
from azure.cosmos import CosmosClient

def main():
    """Clean up all data from CosmosDB collections"""

    print("🧹 Starting cleanup of all CosmosDB data...")

    # Get connection string from Azure CLI
    result = subprocess.run(['az', 'cosmosdb', 'keys', 'list', '--name', 'book-library-cosmos',
                           '--resource-group', 'dev-swa-rg', '--type', 'connection-strings',
                           '--query', 'connectionStrings[0].connectionString', '--output', 'tsv'],
                          capture_output=True, text=True)
    connection_string = result.stdout.strip()

    # Initialize the Cosmos client
    client = CosmosClient.from_connection_string(connection_string)
    database = client.get_database_client("BookLibraryDB")

    # Collections to clean
    collections = ["Books", "BorrowRecords", "Users"]

    for collection_name in collections:
        try:
            print(f"\n📋 Cleaning {collection_name} collection...")
            container = database.get_container_client(collection_name)

            # Query all documents
            query = "SELECT c.id, c._self FROM c"
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))

            print(f"Found {len(items)} items to delete")

            # Delete all documents
            deleted_count = 0
            for item in items:
                try:
                    container.delete_item(item=item['id'], partition_key=item.get('category', item.get('userId', item.get('userType', ''))))
                    deleted_count += 1
                    if deleted_count % 5 == 0:
                        print(f"  Deleted {deleted_count}/{len(items)} items...")
                except Exception as e:
                    print(f"  ❌ Error deleting item {item['id']}: {str(e)}")

            print(f"✅ Successfully deleted {deleted_count} items from {collection_name}")

        except Exception as e:
            print(f"❌ Error cleaning {collection_name}: {str(e)}")

    print(f"\n🎯 Cleanup completed!")

if __name__ == "__main__":
    main()