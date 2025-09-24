# Borrow & Return System Design
**Data Structure and API Design for Book Borrowing Workflow**

## 📋 Overview

This document outlines the data structure and API design for implementing a complete book borrowing and return system integrated with the existing Azure architecture.

## 🗄️ Data Structure Design

### 1. Borrow Records Collection

**CosmosDB Container**: `BorrowRecords`
**Partition Key**: `/userId` (for efficient user-based queries)

```json
{
  "id": "borrow_20250924_001",
  "borrowId": "BRW-2025092412345",
  "userId": "user001",
  "userName": "John Doe",
  "userEmail": "john.doe@example.com",
  "bookId": "book001",
  "bookTitle": "Clean Code: A Handbook of Agile Software Craftsmanship",
  "bookIsbn": "9780132350884",
  "bookCategory": "Technology",
  "borrowDate": "2025-09-24T10:30:00Z",
  "dueDate": "2025-10-08T10:30:00Z",
  "returnDate": null,
  "status": "ACTIVE",
  "renewalCount": 0,
  "maxRenewals": 2,
  "fineAmount": 0.00,
  "notes": "Standard 2-week borrowing period",
  "libraryLocation": "Main Branch",
  "createdAt": "2025-09-24T10:30:00Z",
  "updatedAt": "2025-09-24T10:30:00Z",
  "metadata": {
    "borrowedVia": "WEB_APP",
    "ipAddress": "192.168.1.100",
    "deviceType": "Desktop",
    "librarian": null
  }
}
```

### 2. Updated Books Collection Structure

**Enhancement to existing Books container**:

```json
{
  "id": "book001",
  "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
  "author": "Robert C. Martin",
  "category": "Technology",
  "isbn": "9780132350884",
  "totalCount": 3,
  "availableCount": 2,
  "borrowedCount": 1,
  "reservedCount": 0,
  "description": "A guide to writing clean, readable, and maintainable code...",
  "publishedYear": 2008,
  "addedDate": "2025-09-24T02:50:00Z",
  "lastModified": "2025-09-24T10:30:00Z",
  "borrowingRules": {
    "borrowPeriodDays": 14,
    "maxRenewals": 2,
    "renewalPeriodDays": 7,
    "finePerDay": 0.50,
    "maxFineAmount": 10.00,
    "allowReservations": true
  },
  "currentBorrowers": [
    {
      "userId": "user001",
      "borrowId": "BRW-2025092412345",
      "dueDate": "2025-10-08T10:30:00Z"
    }
  ]
}
```

### 3. User Profiles Collection (Optional Enhancement)

**CosmosDB Container**: `Users`
**Partition Key**: `/userType`

```json
{
  "id": "user001",
  "userId": "user001",
  "userType": "MEMBER",
  "profile": {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "address": {
      "street": "123 Main St",
      "city": "Seattle",
      "state": "WA",
      "zipCode": "98101"
    }
  },
  "membershipInfo": {
    "membershipId": "MEM-001",
    "membershipType": "STANDARD",
    "joinDate": "2025-01-15T00:00:00Z",
    "expiryDate": "2026-01-15T00:00:00Z",
    "status": "ACTIVE",
    "borrowingLimit": 5
  },
  "borrowingHistory": {
    "totalBorrowed": 25,
    "currentlyBorrowed": 2,
    "overdueCount": 0,
    "totalFines": 0.00,
    "lastBorrowDate": "2025-09-24T10:30:00Z"
  },
  "preferences": {
    "emailNotifications": true,
    "smsNotifications": false,
    "favoriteCategories": ["Technology", "Science"],
    "language": "en-US"
  },
  "createdAt": "2025-01-15T00:00:00Z",
  "updatedAt": "2025-09-24T10:30:00Z"
}
```

## 🔌 API Design

### 1. Borrow Book API

**Endpoint**: `POST /api/books/borrow`
**Method**: HTTP POST
**Authentication**: Required (User token)

#### Request Body:
```json
{
  "bookId": "book001",
  "userId": "user001",
  "borrowPeriodDays": 14,
  "notes": "Standard borrowing"
}
```

#### Response (Success - 201 Created):
```json
{
  "success": true,
  "message": "Book borrowed successfully",
  "data": {
    "borrowId": "BRW-2025092412345",
    "bookTitle": "Clean Code: A Handbook of Agile Software Craftsmanship",
    "borrowDate": "2025-09-24T10:30:00Z",
    "dueDate": "2025-10-08T10:30:00Z",
    "renewalsAvailable": 2,
    "bookLocation": "Main Branch - Section A, Shelf 3"
  },
  "links": {
    "renewBook": "/api/books/renew/BRW-2025092412345",
    "viewBorrowHistory": "/api/user/user001/borrows"
  }
}
```

#### Response (Error - 400 Bad Request):
```json
{
  "success": false,
  "error": {
    "code": "BOOK_NOT_AVAILABLE",
    "message": "Book is not available for borrowing",
    "details": {
      "bookId": "book001",
      "availableCount": 0,
      "nextAvailableDate": "2025-10-01T00:00:00Z"
    },
    "suggestions": [
      "Reserve the book for when it becomes available",
      "Browse similar books in the Technology category"
    ]
  }
}
```

### 2. Return Book API

**Endpoint**: `POST /api/books/return`
**Method**: HTTP POST
**Authentication**: Required (User token or Staff token)

#### Request Body:
```json
{
  "borrowId": "BRW-2025092412345",
  "returnDate": "2025-10-05T14:30:00Z",
  "condition": "GOOD",
  "notes": "Returned in excellent condition",
  "returnedBy": "user001",
  "libraryLocation": "Main Branch"
}
```

#### Response (Success - 200 OK):
```json
{
  "success": true,
  "message": "Book returned successfully",
  "data": {
    "borrowId": "BRW-2025092412345",
    "bookTitle": "Clean Code: A Handbook of Agile Software Craftsmanship",
    "borrowDate": "2025-09-24T10:30:00Z",
    "returnDate": "2025-10-05T14:30:00Z",
    "dueDate": "2025-10-08T10:30:00Z",
    "isLate": false,
    "fineAmount": 0.00,
    "borrowPeriodDays": 11
  },
  "bookAvailability": {
    "availableCount": 3,
    "waitingList": 0,
    "nextReserver": null
  }
}
```

### 3. Renew Book API

**Endpoint**: `POST /api/books/renew`
**Method**: HTTP POST
**Authentication**: Required (User token)

#### Request Body:
```json
{
  "borrowId": "BRW-2025092412345",
  "renewalPeriodDays": 7
}
```

#### Response (Success - 200 OK):
```json
{
  "success": true,
  "message": "Book renewed successfully",
  "data": {
    "borrowId": "BRW-2025092412345",
    "originalDueDate": "2025-10-08T10:30:00Z",
    "newDueDate": "2025-10-15T10:30:00Z",
    "renewalCount": 1,
    "remainingRenewals": 1
  }
}
```

### 4. Get User Borrows API

**Endpoint**: `GET /api/user/{userId}/borrows`
**Method**: HTTP GET
**Authentication**: Required (User token)

#### Query Parameters:
- `status`: Filter by status (ACTIVE, RETURNED, OVERDUE)
- `limit`: Number of records to return (default: 10)
- `offset`: Pagination offset (default: 0)

#### Response (Success - 200 OK):
```json
{
  "success": true,
  "data": {
    "userId": "user001",
    "summary": {
      "activeBorrows": 2,
      "overdueBorrows": 0,
      "totalFines": 0.00,
      "borrowingLimit": 5,
      "remainingLimit": 3
    },
    "borrows": [
      {
        "borrowId": "BRW-2025092412345",
        "bookId": "book001",
        "bookTitle": "Clean Code",
        "borrowDate": "2025-09-24T10:30:00Z",
        "dueDate": "2025-10-08T10:30:00Z",
        "status": "ACTIVE",
        "renewalCount": 0,
        "canRenew": true,
        "daysUntilDue": 14
      }
    ],
    "pagination": {
      "total": 25,
      "limit": 10,
      "offset": 0,
      "hasMore": true
    }
  }
}
```

### 5. Get Book Availability API

**Endpoint**: `GET /api/books/{bookId}/availability`
**Method**: HTTP GET
**Authentication**: Optional

#### Response (Success - 200 OK):
```json
{
  "success": true,
  "data": {
    "bookId": "book001",
    "bookTitle": "Clean Code: A Handbook of Agile Software Craftsmanship",
    "availability": {
      "totalCount": 3,
      "availableCount": 2,
      "borrowedCount": 1,
      "reservedCount": 0,
      "isAvailable": true
    },
    "currentBorrows": [
      {
        "dueDate": "2025-10-08T10:30:00Z",
        "isOverdue": false
      }
    ],
    "nextAvailable": null,
    "estimatedWaitTime": "0 days"
  }
}
```

## 🏗️ Azure Function Implementation

### Function Structure

```python
# function_app.py additions

@app.function_name(name="BorrowBook")
@app.route(route="books/borrow", auth_level=func.AuthLevel.FUNCTION, methods=["POST", "OPTIONS"])
def borrow_book(req: func.HttpRequest) -> func.HttpResponse:
    # Implementation for borrowing books
    pass

@app.function_name(name="ReturnBook")
@app.route(route="books/return", auth_level=func.AuthLevel.FUNCTION, methods=["POST", "OPTIONS"])
def return_book(req: func.HttpRequest) -> func.HttpResponse:
    # Implementation for returning books
    pass

@app.function_name(name="RenewBook")
@app.route(route="books/renew", auth_level=func.AuthLevel.FUNCTION, methods=["POST", "OPTIONS"])
def renew_book(req: func.HttpRequest) -> func.HttpResponse:
    # Implementation for renewing books
    pass

@app.function_name(name="GetUserBorrows")
@app.route(route="user/{userId}/borrows", auth_level=func.AuthLevel.FUNCTION, methods=["GET", "OPTIONS"])
def get_user_borrows(req: func.HttpRequest) -> func.HttpResponse:
    # Implementation for getting user borrow history
    pass
```

## 🔧 CosmosDB Setup Commands

```bash
# Create BorrowRecords container
az cosmosdb sql container create \
  --account-name book-library-cosmos \
  --resource-group dev-swa-rg \
  --database-name BookLibraryDB \
  --name BorrowRecords \
  --partition-key-path "/userId" \
  --throughput 400

# Create Users container (optional)
az cosmosdb sql container create \
  --account-name book-library-cosmos \
  --resource-group dev-swa-rg \
  --database-name BookLibraryDB \
  --name Users \
  --partition-key-path "/userType" \
  --throughput 400

# Create indexes for efficient queries
az cosmosdb sql container update \
  --account-name book-library-cosmos \
  --resource-group dev-swa-rg \
  --database-name BookLibraryDB \
  --name BorrowRecords \
  --idx @borrow-indexes.json
```

### Index Configuration (borrow-indexes.json):
```json
{
  "indexingPolicy": {
    "indexingMode": "consistent",
    "includedPaths": [
      {"path": "/userId/*"},
      {"path": "/bookId/*"},
      {"path": "/status/*"},
      {"path": "/borrowDate/*"},
      {"path": "/dueDate/*"}
    ],
    "excludedPaths": [
      {"path": "/metadata/*"},
      {"path": "/notes/*"}
    ]
  }
}
```

## 🔄 Business Logic Flow

### Borrowing Flow:
1. **Validate User**: Check user exists and has borrowing privileges
2. **Check Availability**: Verify book is available for borrowing
3. **Check Limits**: Ensure user hasn't exceeded borrowing limit
4. **Create Borrow Record**: Insert into BorrowRecords container
5. **Update Book Counts**: Decrease availableCount, increase borrowedCount
6. **Send Notification**: Email/SMS confirmation to user
7. **Return Response**: Success with borrow details

### Return Flow:
1. **Validate Borrow Record**: Check borrow record exists and is active
2. **Calculate Fines**: Check if return is late, calculate fine amount
3. **Update Borrow Record**: Set returnDate, status = "RETURNED"
4. **Update Book Counts**: Increase availableCount, decrease borrowedCount
5. **Process Reservations**: Check if book is reserved, notify next user
6. **Send Notification**: Confirmation and fine notice (if applicable)
7. **Return Response**: Success with return details and fine info

## 🔒 Security Considerations

1. **Authentication**: All APIs require valid user tokens
2. **Authorization**: Users can only access their own borrow records
3. **Rate Limiting**: Prevent abuse of borrowing APIs
4. **Input Validation**: Sanitize all input parameters
5. **Audit Logging**: Log all borrow/return activities
6. **Data Privacy**: Mask sensitive user information in logs

## 📊 Performance Optimizations

1. **Partition Strategy**: Partition by userId for user-centric queries
2. **Indexing**: Strategic indexes on frequently queried fields
3. **Caching**: Cache book availability data
4. **Pagination**: Limit result sets for large queries
5. **Batch Operations**: Bulk updates for efficiency
6. **TTL**: Automatic cleanup of old records

## 🎯 Future Enhancements

1. **Reservations System**: Queue system for popular books
2. **Digital Receipts**: PDF generation for borrow/return receipts
3. **Mobile App Integration**: Push notifications for due dates
4. **Analytics Dashboard**: Borrowing patterns and popular books
5. **Multi-Library Support**: Cross-branch borrowing
6. **Integration APIs**: Third-party library system integration

---

**This design provides a robust foundation for implementing a complete book borrowing and return system integrated with your existing Azure architecture.** 📚✨