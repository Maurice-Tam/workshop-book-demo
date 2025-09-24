#!/usr/bin/env python3
import json
import os
from datetime import datetime

def main():
    """Create 10 blank books with IDs book020 through book029"""

    print("📚 Creating 10 blank books (book020-book029)...")

    # Create data directory if it doesn't exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    print(f"Data directory: {data_dir}")

    # Template for blank books
    blank_book_template = {
        "title": "",
        "author": "",
        "category": "",
        "isbn": "",
        "totalCount": 0,
        "availableCount": 0,
        "borrowedCount": 0,
        "description": "",
        "publishedYear": 0,
        "addedDate": datetime.utcnow().isoformat() + "Z",
        "lastModified": datetime.utcnow().isoformat() + "Z"
    }

    created_count = 0

    # Create books book020 through book029
    for i in range(20, 30):
        book_id = f"book{i:03d}"
        filename = os.path.join(data_dir, f"{book_id}.json")

        # Create book data with unique ID
        book_data = blank_book_template.copy()
        book_data["id"] = book_id

        try:
            # Write to JSON file
            with open(filename, 'w') as f:
                json.dump(book_data, f, indent=2)

            print(f"✅ Created {filename}")
            created_count += 1

        except Exception as e:
            print(f"❌ Error creating {filename}: {str(e)}")

    print(f"\n🎯 Successfully created {created_count}/10 blank books")

if __name__ == "__main__":
    main()