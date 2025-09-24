# 📚 CosmosDB Book Management API Feature

## Overview
This feature adds a CosmosDB database to store book information and implements a new Azure Function API to list all books, replacing the current in-memory data structure.

**Current Architecture**: `Static Web App → APIM Gateway → Azure Function (in-memory data)`
**New Architecture**: `Static Web App → APIM Gateway → Azure Function → CosmosDB`

---

## 🏗️ Feature Specifications

### Database Design

#### CosmosDB Configuration
```yaml
Database Name: BookLibraryDB
Container Name: Books
Partition Key: /category
Consistency Level: Session
Initial Throughput: 400 RU/s (Manual)
```

#### Book Document Schema
```json
{
  "id": "string",                    // Unique book identifier
  "title": "string",                 // Book title
  "author": "string",                // Author name
  "category": "string",              // Partition key (Technology, Business, Science, Fiction)
  "isbn": "string",                  // ISBN number
  "totalCount": number,              // Total copies available
  "availableCount": number,          // Current available copies
  "borrowedCount": number,           // Currently borrowed copies
  "description": "string",           // Book description
  "publishedYear": number,           // Year published
  "addedDate": "string",            // ISO date when added to library
  "lastModified": "string"          // ISO date of last update
}
```

### API Specifications

#### New API Endpoint: List All Books
```yaml
Method: GET
Path: /api/books/list
Authentication: Function Key (handled by APIM)
Response Format: JSON Array
CORS: Enabled via APIM
```

**Response Structure**:
```json
{
  "success": true,
  "data": [
    {
      "id": "book001",
      "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
      "author": "Robert C. Martin",
      "category": "Technology",
      "isbn": "9780132350884",
      "totalCount": 3,
      "availableCount": 2,
      "borrowedCount": 1,
      "description": "A guide to writing clean, readable, and maintainable code.",
      "publishedYear": 2008,
      "addedDate": "2025-09-24T00:00:00Z",
      "lastModified": "2025-09-24T00:00:00Z"
    }
  ],
  "count": 5,
  "timestamp": "2025-09-24T02:45:00Z"
}
```

---

## 📊 Sample Data (5 Books)

### Book Collection for Initial Seeding
```json
[
  {
    "id": "book001",
    "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
    "author": "Robert C. Martin",
    "category": "Technology",
    "isbn": "9780132350884",
    "totalCount": 3,
    "availableCount": 2,
    "borrowedCount": 1,
    "description": "A guide to writing clean, readable, and maintainable code. Learn how to write code that's easy to understand, maintain, and extend.",
    "publishedYear": 2008,
    "addedDate": "2025-09-24T00:00:00Z",
    "lastModified": "2025-09-24T00:00:00Z"
  },
  {
    "id": "book002",
    "title": "The Lean Startup",
    "author": "Eric Ries",
    "category": "Business",
    "isbn": "9780307887894",
    "totalCount": 2,
    "availableCount": 0,
    "borrowedCount": 2,
    "description": "How today's entrepreneurs use continuous innovation to create radically successful businesses. Build-Measure-Learn methodology for startups.",
    "publishedYear": 2011,
    "addedDate": "2025-09-24T00:00:00Z",
    "lastModified": "2025-09-24T00:00:00Z"
  },
  {
    "id": "book003",
    "title": "Atomic Habits",
    "author": "James Clear",
    "category": "Business",
    "isbn": "9780735211292",
    "totalCount": 4,
    "availableCount": 3,
    "borrowedCount": 1,
    "description": "Proven strategies for building good habits and breaking bad ones. Small changes that make a big difference over time.",
    "publishedYear": 2018,
    "addedDate": "2025-09-24T00:00:00Z",
    "lastModified": "2025-09-24T00:00:00Z"
  },
  {
    "id": "book004",
    "title": "Sapiens: A Brief History of Humankind",
    "author": "Yuval Noah Harari",
    "category": "Science",
    "isbn": "9780062316097",
    "totalCount": 2,
    "availableCount": 1,
    "borrowedCount": 1,
    "description": "From the birth of humankind to the present day. How Homo Sapiens came to dominate the Earth through cognitive, agricultural, and scientific revolutions.",
    "publishedYear": 2014,
    "addedDate": "2025-09-24T00:00:00Z",
    "lastModified": "2025-09-24T00:00:00Z"
  },
  {
    "id": "book005",
    "title": "Dune",
    "author": "Frank Herbert",
    "category": "Fiction",
    "isbn": "9780441172719",
    "totalCount": 3,
    "availableCount": 2,
    "borrowedCount": 1,
    "description": "A science fiction masterpiece about power, politics, and survival on the desert planet Arrakis. Epic tale of Paul Atreides and the spice melange.",
    "publishedYear": 1965,
    "addedDate": "2025-09-24T00:00:00Z",
    "lastModified": "2025-09-24T00:00:00Z"
  }
]
```

---

## 🚀 Implementation Plan

### Phase 1: CosmosDB Provisioning

#### Step 1: Create CosmosDB Account
```bash
# Variables
RESOURCE_GROUP="dev-swa-rg"
COSMOS_ACCOUNT="book-library-cosmos"
DATABASE_NAME="BookLibraryDB"
CONTAINER_NAME="Books"
LOCATION="canadacentral"

# Create CosmosDB Account
az cosmosdb create \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --default-consistency-level Session \
  --enable-multiple-write-locations false \
  --enable-automatic-failover false

# Create Database
az cosmosdb sql database create \
  --account-name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --name $DATABASE_NAME

# Create Container with partition key
az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT \
  --database-name $DATABASE_NAME \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_NAME \
  --partition-key-path "/category" \
  --throughput 400
```

#### Step 2: Configure Access Keys
```bash
# Get connection string
COSMOS_CONNECTION_STRING=$(az cosmosdb keys list \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --type connection-strings \
  --query "connectionStrings[0].connectionString" \
  --output tsv)

# Configure Function App setting
az functionapp config appsettings set \
  --name helloworldfunc09231920 \
  --resource-group $RESOURCE_GROUP \
  --settings "CosmosDB_ConnectionString=$COSMOS_CONNECTION_STRING"
```

### Phase 2: Azure Function Development

#### Step 1: Update Function Requirements
Add to `requirements.txt`:
```txt
azure-cosmos>=4.5.0
```

#### Step 2: Create Books API Function
```python
import azure.functions as func
from azure.cosmos import CosmosClient
import json
import logging
import os
from datetime import datetime

app = func.FunctionApp()

# CosmosDB Configuration
COSMOS_CONNECTION_STRING = os.environ.get('CosmosDB_ConnectionString')
DATABASE_NAME = 'BookLibraryDB'
CONTAINER_NAME = 'Books'

def get_cosmos_client():
    return CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING)

@app.function_name(name="ListBooks")
@app.route(route="books/list", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "OPTIONS"])
def list_books(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing list books request')

    # CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept"
    }

    # Handle preflight OPTIONS request
    if req.method == "OPTIONS":
        return func.HttpResponse("", headers=headers, status_code=200)

    try:
        # Initialize Cosmos client
        client = get_cosmos_client()
        database = client.get_database_client(DATABASE_NAME)
        container = database.get_container_client(CONTAINER_NAME)

        # Query all books
        query = "SELECT * FROM c ORDER BY c.title"
        books = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        # Prepare response
        response_data = {
            "success": True,
            "data": books,
            "count": len(books),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        return func.HttpResponse(
            json.dumps(response_data),
            mimetype="application/json",
            headers=headers,
            status_code=200
        )

    except Exception as e:
        logging.error(f'Error retrieving books: {str(e)}')
        error_response = {
            "success": False,
            "error": "Failed to retrieve books",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        return func.HttpResponse(
            json.dumps(error_response),
            mimetype="application/json",
            headers=headers,
            status_code=500
        )

@app.function_name(name="SeedBooksData")
@app.route(route="books/seed", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
def seed_books_data(req: func.HttpRequest) -> func.HttpResponse:
    """Administrative function to seed initial book data"""
    logging.info('Seeding books data')

    headers = {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json"
    }

    try:
        # Sample books data
        sample_books = [
            # ... (sample books data from above)
        ]

        # Initialize Cosmos client
        client = get_cosmos_client()
        database = client.get_database_client(DATABASE_NAME)
        container = database.get_container_client(CONTAINER_NAME)

        # Insert each book
        inserted_count = 0
        for book in sample_books:
            try:
                container.create_item(book)
                inserted_count += 1
                logging.info(f'Inserted book: {book["title"]}')
            except Exception as book_error:
                logging.warning(f'Book already exists or error: {book_error}')

        response_data = {
            "success": True,
            "message": f"Seeded {inserted_count} books successfully",
            "total_books": len(sample_books),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        return func.HttpResponse(
            json.dumps(response_data),
            mimetype="application/json",
            headers=headers,
            status_code=200
        )

    except Exception as e:
        logging.error(f'Error seeding books: {str(e)}')
        error_response = {
            "success": False,
            "error": "Failed to seed books",
            "message": str(e)
        }

        return func.HttpResponse(
            json.dumps(error_response),
            mimetype="application/json",
            headers=headers,
            status_code=500
        )
```

### Phase 3: APIM Integration

#### Step 1: Add New API Operation
```bash
# Add list books operation to APIM
az apim api operation create \
  --resource-group "dev-swa-rg" \
  --service-name "book-system-apim" \
  --api-id "book-borrowing-api" \
  --operation-id "list-books" \
  --method GET \
  --url-template "/list" \
  --display-name "List All Books"

# Add OPTIONS for CORS
az apim api operation create \
  --resource-group "dev-swa-rg" \
  --service-name "book-system-apim" \
  --api-id "book-borrowing-api" \
  --operation-id "list-books-options" \
  --method OPTIONS \
  --url-template "/list" \
  --display-name "List Books Options"
```

---

## 🧪 Testing Procedures

### Unit Testing

#### Test CosmosDB Connection
```bash
# Test connection string (replace with actual connection string)
python -c "
from azure.cosmos import CosmosClient
client = CosmosClient.from_connection_string('$COSMOS_CONNECTION_STRING')
print('CosmosDB connection successful')
"
```

#### Test Book Data Seeding
```bash
# Call seed function (requires function key)
curl -X POST "https://helloworldfunc09231920.azurewebsites.net/api/books/seed" \
  -H "x-functions-key: YOUR_FUNCTION_KEY"
```

#### Test List Books API
```bash
# Test direct function call
curl -X GET "https://helloworldfunc09231920.azurewebsites.net/api/books/list"

# Test via APIM Gateway
curl -X GET "https://book-system-apim.azure-api.net/books/list"
```

### Integration Testing

#### Frontend Integration Test
```javascript
// Update Static Web App to call new endpoint
const APIM_GATEWAY_URL = 'https://book-system-apim.azure-api.net';

async function loadBooks() {
    try {
        const response = await fetch(`${APIM_GATEWAY_URL}/books/list`);
        const data = await response.json();

        if (data.success) {
            console.log(`Loaded ${data.count} books from CosmosDB`);
            return data.data;
        } else {
            throw new Error(data.error || 'Failed to load books');
        }
    } catch (error) {
        console.error('Error loading books:', error);
        throw error;
    }
}
```

---

## 📈 Performance Considerations

### CosmosDB Optimization

#### Partition Strategy
- **Partition Key**: `/category` provides good distribution
- **Expected Categories**: Technology, Business, Science, Fiction
- **Benefits**: Enables efficient queries within categories

#### Request Unit (RU) Planning
```yaml
Initial Provision: 400 RU/s (Manual scaling)
Expected Operations:
  - Read single book: 1-2 RUs
  - List all books: 10-20 RUs
  - Insert new book: 5-10 RUs
  - Update book: 5-10 RUs

Monthly Cost Estimate: ~$23.36 CAD (400 RU/s)
```

#### Query Optimization
```sql
-- Efficient queries with partition key
SELECT * FROM c WHERE c.category = "Technology"

-- Cross-partition queries (higher RU cost)
SELECT * FROM c ORDER BY c.title
```

---

## 🔒 Security Configuration

### Access Control

#### Function App Security
```yaml
Authentication Level: Function Key
Environment Variables:
  - CosmosDB_ConnectionString (encrypted)
Network Security:
  - HTTPS only
  - CORS via APIM
```

#### CosmosDB Security
```yaml
Access Control:
  - Connection string authentication
  - Private endpoints (future enhancement)
  - Network access restrictions (future)
Firewall Rules:
  - Allow Azure services
  - Specific IP ranges (production)
```

### Data Privacy
```yaml
Sensitive Data: None in book catalog
Logging: No connection strings in logs
Monitoring: Application Insights integration
Backup: Automatic continuous backup enabled
```

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] CosmosDB account created
- [ ] Database and container configured
- [ ] Connection string retrieved
- [ ] Function App settings updated
- [ ] Code deployed and tested locally

### Deployment
- [ ] Deploy Azure Function with new code
- [ ] Update APIM operations
- [ ] Seed initial book data
- [ ] Test all endpoints

### Post-Deployment
- [ ] Verify CosmosDB data insertion
- [ ] Test list books API via APIM
- [ ] Update Static Web App to use new endpoint
- [ ] Monitor performance and RU consumption
- [ ] Validate error handling

---

## 📊 Monitoring and Observability

### Key Metrics to Monitor

#### CosmosDB Metrics
```yaml
Request Units: Total consumed per minute
Throttling: 429 status codes
Latency: P99 response times
Availability: Uptime percentage
Storage: Document count and size
```

#### Function App Metrics
```yaml
Execution Count: API calls per minute
Execution Duration: Response time
Error Rate: Failed requests percentage
Memory Usage: Function memory consumption
```

### Alerting Rules
```yaml
High RU Consumption: >300 RU/s sustained
API Errors: >5% error rate
High Latency: >1000ms P95
CosmosDB Throttling: Any 429 responses
```

---

## 🔄 Future Enhancements

### Phase 2 Features
- [ ] Add book filtering by category
- [ ] Implement pagination for large datasets
- [ ] Add full-text search capabilities
- [ ] Book borrowing/return API endpoints

### Phase 3 Features
- [ ] Book reservation system
- [ ] User management and authentication
- [ ] Book recommendations engine
- [ ] Analytics and reporting dashboard

### Infrastructure Improvements
- [ ] CosmosDB private endpoints
- [ ] Auto-scaling based on demand
- [ ] Multi-region deployment
- [ ] Disaster recovery planning

---

## 💰 Cost Analysis

### Monthly Cost Estimation (CAD)

```yaml
CosmosDB (400 RU/s):     $23.36
Function App:            $0.00 (consumption plan)
APIM Developer Tier:     $65.00
Total Monthly:           ~$88.36

Annual Cost:             ~$1,060.32
```

### Cost Optimization
- Start with 400 RU/s and monitor usage
- Consider serverless CosmosDB for low usage
- Scale up only when needed based on metrics

---

## 📚 Documentation Links

- [Azure CosmosDB Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/)
- [Azure Functions Python Developer Guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [CosmosDB Python SDK](https://docs.microsoft.com/en-us/python/api/overview/azure/cosmos-readme)

---

**Feature Status**: Ready for Implementation
**Estimated Development Time**: 2-3 days
**Priority**: High
**Dependencies**: Existing APIM Gateway, Azure Function App

---

*This feature document provides a complete implementation guide for adding CosmosDB-backed book management to the Book Borrowing System.*