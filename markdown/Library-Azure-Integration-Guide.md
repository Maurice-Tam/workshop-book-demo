# Library Azure Integration Guide
**Connecting Static Book Library to Azure Backend with Dynamic Browse Books Feature**

## 📋 Overview

This guide provides step-by-step instructions for integrating the existing static book library (`index.html`) with Azure services to create a dynamic, real-time book browsing experience powered by:
- Azure API Management (APIM) Gateway
- Azure Functions
- Azure CosmosDB

## 🏗️ Architecture Flow

```
User Browser → Static Web App → APIM Gateway → Azure Function → CosmosDB
     ↑                                                              ↓
     └────────────── Dynamic Book Data Response ←─────────────────┘
```

## 🎯 Integration Objectives

1. **Transform static library** into dynamic application
2. **Implement Browse Books** with real-time CosmosDB data
3. **Add search and filter** capabilities
4. **Enable borrowing workflow** integration
5. **Maintain responsive UI** with loading states

## 📦 Prerequisites

### Azure Resources Required
- **APIM Gateway**: `book-system-apim.azure-api.net`
- **Azure Function**: `helloworldfunc09231920.azurewebsites.net`
- **CosmosDB**: 15 books already loaded
- **API Subscription Key**: `6854c6a9b0ff4b449f50b06f3e3b8d5e`

### Endpoints Available
```javascript
const API_CONFIG = {
    gateway: 'https://book-system-apim.azure-api.net/books',
    endpoints: {
        hello: '/hello',      // Test endpoint
        books: '/books'       // List all books
    },
    key: '6854c6a9b0ff4b449f50b06f3e3b8d5e'
};
```

## 🚀 Implementation Guide

### Step 1: Prepare HTML Structure

Update your `index.html` to include dynamic content areas:

```html
<!-- Add to existing index.html -->
<div id="dynamicBooksSection">
    <!-- Loading State -->
    <div id="loadingIndicator" class="loading-state" style="display: none;">
        <div class="spinner"></div>
        <p>Loading books from Azure CosmosDB...</p>
    </div>

    <!-- Error State -->
    <div id="errorMessage" class="error-state" style="display: none;">
        <p class="error-text"></p>
        <button onclick="retryLoading()">Retry</button>
    </div>

    <!-- Books Container -->
    <div id="booksContainer" class="books-grid" style="display: none;">
        <!-- Dynamic books will be inserted here -->
    </div>

    <!-- Statistics Dashboard -->
    <div id="statsPanel" class="stats-panel" style="display: none;">
        <div class="stat-card">
            <span class="stat-value" id="totalBooks">0</span>
            <span class="stat-label">Total Books</span>
        </div>
        <div class="stat-card">
            <span class="stat-value" id="availableBooks">0</span>
            <span class="stat-label">Available</span>
        </div>
        <div class="stat-card">
            <span class="stat-value" id="borrowedBooks">0</span>
            <span class="stat-label">Borrowed</span>
        </div>
    </div>
</div>
```

### Step 2: Add JavaScript Integration

```javascript
// Azure Integration Module
const AzureBookLibrary = {
    // Configuration
    config: {
        apiUrl: 'https://book-system-apim.azure-api.net/books',
        apiKey: '6854c6a9b0ff4b449f50b06f3e3b8d5e',
        retryAttempts: 3,
        cacheTimeout: 300000 // 5 minutes
    },

    // Cache management
    cache: {
        books: null,
        timestamp: null
    },

    // Initialize the library
    init: function() {
        console.log('Initializing Azure Book Library...');
        this.attachEventListeners();
        this.loadBooks();
    },

    // Attach event listeners
    attachEventListeners: function() {
        // Browse Books button
        const browseBtn = document.querySelector('#browseBooks');
        if (browseBtn) {
            browseBtn.addEventListener('click', () => this.loadBooks());
        }

        // Search functionality
        const searchInput = document.querySelector('#searchBooks');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.searchBooks(e.target.value));
        }

        // Category filters
        document.querySelectorAll('.category-filter').forEach(filter => {
            filter.addEventListener('click', (e) => this.filterByCategory(e.target.dataset.category));
        });
    },

    // Load books from Azure
    async loadBooks(forceRefresh = false) {
        try {
            // Check cache
            if (!forceRefresh && this.isCacheValid()) {
                this.displayBooks(this.cache.books);
                return;
            }

            // Show loading state
            this.showLoading();

            // Fetch from APIM Gateway
            const response = await fetch(`${this.config.apiUrl}/books`, {
                method: 'GET',
                headers: {
                    'Ocp-Apim-Subscription-Key': this.config.apiKey,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            // Update cache
            this.cache.books = data.books;
            this.cache.timestamp = Date.now();

            // Display books
            this.displayBooks(data.books);
            this.updateStatistics(data.books);

        } catch (error) {
            console.error('Failed to load books:', error);
            this.showError(error.message);
        }
    },

    // Display books in grid
    displayBooks: function(books) {
        const container = document.getElementById('booksContainer');

        if (!books || books.length === 0) {
            container.innerHTML = '<p class="no-books">No books found</p>';
            this.hideLoading();
            container.style.display = 'block';
            return;
        }

        // Generate HTML for each book
        const booksHTML = books.map(book => this.createBookCard(book)).join('');
        container.innerHTML = booksHTML;

        // Show container and hide loading
        this.hideLoading();
        container.style.display = 'grid';

        // Attach book card event listeners
        this.attachBookCardListeners();
    },

    // Create individual book card
    createBookCard: function(book) {
        const availabilityClass = book.availableCount > 0 ? 'available' : 'unavailable';
        const availabilityText = book.availableCount > 0
            ? `${book.availableCount} available`
            : 'Currently unavailable';

        return `
            <div class="book-card ${availabilityClass}" data-book-id="${book.id}">
                <div class="book-header">
                    <h3 class="book-title">${book.title}</h3>
                    <span class="book-category badge-${book.category.toLowerCase()}">${book.category}</span>
                </div>

                <div class="book-body">
                    <p class="book-author">by ${book.author}</p>
                    <p class="book-description">${book.description}</p>

                    <div class="book-meta">
                        <span class="book-year">Published: ${book.publishedYear}</span>
                        <span class="book-isbn">ISBN: ${book.isbn}</span>
                    </div>

                    <div class="book-availability">
                        <div class="availability-indicator ${availabilityClass}"></div>
                        <span class="availability-text">${availabilityText}</span>
                    </div>

                    <div class="book-stats">
                        <div class="stat">
                            <span class="stat-label">Total:</span>
                            <span class="stat-value">${book.totalCount}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Available:</span>
                            <span class="stat-value">${book.availableCount}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Borrowed:</span>
                            <span class="stat-value">${book.borrowedCount}</span>
                        </div>
                    </div>
                </div>

                <div class="book-actions">
                    <button class="btn-borrow"
                            onclick="AzureBookLibrary.borrowBook('${book.id}')"
                            ${book.availableCount === 0 ? 'disabled' : ''}>
                        ${book.availableCount > 0 ? 'Borrow Book' : 'Join Waitlist'}
                    </button>
                    <button class="btn-details" onclick="AzureBookLibrary.showBookDetails('${book.id}')">
                        View Details
                    </button>
                </div>
            </div>
        `;
    },

    // Search books
    searchBooks: function(query) {
        if (!this.cache.books) {
            this.loadBooks();
            return;
        }

        const filtered = this.cache.books.filter(book =>
            book.title.toLowerCase().includes(query.toLowerCase()) ||
            book.author.toLowerCase().includes(query.toLowerCase()) ||
            book.description.toLowerCase().includes(query.toLowerCase())
        );

        this.displayBooks(filtered);
    },

    // Filter by category
    filterByCategory: function(category) {
        if (!this.cache.books) {
            this.loadBooks();
            return;
        }

        const filtered = category === 'all'
            ? this.cache.books
            : this.cache.books.filter(book => book.category === category);

        this.displayBooks(filtered);

        // Update active filter
        document.querySelectorAll('.category-filter').forEach(filter => {
            filter.classList.toggle('active', filter.dataset.category === category);
        });
    },

    // Update statistics
    updateStatistics: function(books) {
        const stats = {
            total: books.length,
            available: books.reduce((sum, book) => sum + book.availableCount, 0),
            borrowed: books.reduce((sum, book) => sum + book.borrowedCount, 0)
        };

        document.getElementById('totalBooks').textContent = stats.total;
        document.getElementById('availableBooks').textContent = stats.available;
        document.getElementById('borrowedBooks').textContent = stats.borrowed;
        document.getElementById('statsPanel').style.display = 'flex';
    },

    // Utility functions
    showLoading: function() {
        document.getElementById('loadingIndicator').style.display = 'block';
        document.getElementById('booksContainer').style.display = 'none';
        document.getElementById('errorMessage').style.display = 'none';
    },

    hideLoading: function() {
        document.getElementById('loadingIndicator').style.display = 'none';
    },

    showError: function(message) {
        document.getElementById('errorMessage').style.display = 'block';
        document.querySelector('#errorMessage .error-text').textContent = message;
        this.hideLoading();
    },

    isCacheValid: function() {
        return this.cache.books &&
               this.cache.timestamp &&
               (Date.now() - this.cache.timestamp < this.config.cacheTimeout);
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    AzureBookLibrary.init();
});
```

### Step 3: Add CSS Styles

```css
/* Dynamic Books Grid */
.books-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 24px;
    padding: 20px;
    animation: fadeIn 0.5s ease-in;
}

/* Book Card Styles */
.book-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    border-left: 4px solid #4CAF50;
}

.book-card.unavailable {
    border-left-color: #f44336;
    opacity: 0.8;
}

.book-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

/* Category Badges */
.badge-technology { background: linear-gradient(135deg, #667eea, #764ba2); }
.badge-business { background: linear-gradient(135deg, #f093fb, #f5576c); }
.badge-fiction { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.badge-science { background: linear-gradient(135deg, #43e97b, #38f9d7); }
.badge-history { background: linear-gradient(135deg, #fa709a, #fee140); }
.badge-psychology { background: linear-gradient(135deg, #30cfd0, #330867); }
.badge-economics { background: linear-gradient(135deg, #a8edea, #fed6e3); }
.badge-philosophy { background: linear-gradient(135deg, #ff9a9e, #fecfef); }
.badge-spirituality { background: linear-gradient(135deg, #ffecd2, #fcb69f); }

.book-category {
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
}

/* Loading State */
.loading-state {
    text-align: center;
    padding: 60px;
}

.spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Statistics Panel */
.stats-panel {
    display: flex;
    justify-content: space-around;
    padding: 20px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 12px;
    margin: 20px;
    color: white;
}

.stat-card {
    text-align: center;
}

.stat-value {
    display: block;
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 8px;
}

.stat-label {
    font-size: 0.9rem;
    text-transform: uppercase;
    opacity: 0.9;
}

/* Availability Indicator */
.availability-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}

.availability-indicator.available {
    background: #4CAF50;
    animation: pulse 2s infinite;
}

.availability-indicator.unavailable {
    background: #f44336;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }
    100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
}

/* Responsive Design */
@media (max-width: 768px) {
    .books-grid {
        grid-template-columns: 1fr;
    }

    .stats-panel {
        flex-direction: column;
        gap: 20px;
    }
}
```

## 🔍 Advanced Features

### 1. Real-time Search
```javascript
// Debounced search for better performance
let searchTimeout;
function searchBooksDebounced(query) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        AzureBookLibrary.searchBooks(query);
    }, 300);
}
```

### 2. Category Filters
```html
<div class="filter-bar">
    <button class="category-filter active" data-category="all">All</button>
    <button class="category-filter" data-category="Technology">Technology</button>
    <button class="category-filter" data-category="Business">Business</button>
    <button class="category-filter" data-category="Fiction">Fiction</button>
    <button class="category-filter" data-category="Science">Science</button>
    <button class="category-filter" data-category="History">History</button>
    <button class="category-filter" data-category="Psychology">Psychology</button>
    <button class="category-filter" data-category="Economics">Economics</button>
    <button class="category-filter" data-category="Philosophy">Philosophy</button>
    <button class="category-filter" data-category="Spirituality">Spirituality</button>
</div>
```

### 3. Borrowing Integration (Future Enhancement)
```javascript
async borrowBook(bookId) {
    try {
        const response = await fetch(`${this.config.apiUrl}/borrow`, {
            method: 'POST',
            headers: {
                'Ocp-Apim-Subscription-Key': this.config.apiKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                bookId: bookId,
                userId: this.getUserId() // Implement user authentication
            })
        });

        if (response.ok) {
            // Refresh books to show updated availability
            this.loadBooks(true);
            this.showSuccess('Book borrowed successfully!');
        }
    } catch (error) {
        this.showError('Failed to borrow book');
    }
}
```

## 🧪 Testing the Integration

### 1. Test APIM Connection
```javascript
// Test connection function
async function testAPIConnection() {
    try {
        const response = await fetch('https://book-system-apim.azure-api.net/books/hello', {
            headers: {
                'Ocp-Apim-Subscription-Key': '6854c6a9b0ff4b449f50b06f3e3b8d5e'
            }
        });
        const result = await response.text();
        console.log('API Test:', result);
        return response.ok;
    } catch (error) {
        console.error('API Test Failed:', error);
        return false;
    }
}
```

### 2. Verify Data Loading
```javascript
// Debug function to check data
function debugBookData() {
    if (AzureBookLibrary.cache.books) {
        console.table(AzureBookLibrary.cache.books);
        console.log('Total books:', AzureBookLibrary.cache.books.length);
        console.log('Categories:', [...new Set(AzureBookLibrary.cache.books.map(b => b.category))]);
    } else {
        console.log('No books loaded yet');
    }
}
```

## 🚨 Troubleshooting

### Common Issues and Solutions

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| **CORS Error** | APIM CORS not configured | Verify CORS policy in APIM includes your domain |
| **401 Unauthorized** | Invalid API key | Check subscription key is correct |
| **Empty Results** | No data in CosmosDB | Verify books exist using Azure Portal |
| **Slow Loading** | Cold start or network | Implement caching and loading states |
| **404 Not Found** | Wrong endpoint URL | Verify APIM gateway URL and path |

### Debug Mode
```javascript
// Enable debug mode
AzureBookLibrary.debug = true;

// Add debug logging
if (this.debug) {
    console.log('API Request:', url, options);
    console.log('API Response:', response.status, data);
}
```

## 📊 Performance Optimization

### 1. Implement Caching
- Cache book data for 5 minutes
- Use localStorage for persistent cache
- Implement cache invalidation strategy

### 2. Lazy Loading
```javascript
// Load images only when visible
const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            imageObserver.unobserve(img);
        }
    });
});
```

### 3. Pagination (Future Enhancement)
```javascript
// Implement pagination for large datasets
async loadBooksPage(page = 1, pageSize = 20) {
    const skip = (page - 1) * pageSize;
    const url = `${this.config.apiUrl}/books?skip=${skip}&limit=${pageSize}`;
    // Fetch paginated results
}
```

## 🔐 Security Best Practices

1. **Never expose sensitive keys in frontend code**
   - Use environment variables in production
   - Implement backend proxy for API calls

2. **Validate all user inputs**
   - Sanitize search queries
   - Validate category filters

3. **Implement rate limiting**
   - Throttle API requests
   - Use debouncing for search

4. **Add authentication** (Future)
   - Implement Azure AD B2C
   - Add user sessions
   - Secure borrowing endpoints

## 📈 Monitoring and Analytics

### Track Key Metrics
```javascript
// Analytics integration
function trackEvent(category, action, label) {
    // Google Analytics or Application Insights
    if (window.gtag) {
        gtag('event', action, {
            'event_category': category,
            'event_label': label
        });
    }
}

// Track book views
trackEvent('Books', 'View', bookId);

// Track searches
trackEvent('Books', 'Search', query);

// Track filters
trackEvent('Books', 'Filter', category);
```

## 🎯 Next Steps

1. **Implement user authentication**
2. **Add book borrowing workflow**
3. **Create admin panel for book management**
4. **Add book reviews and ratings**
5. **Implement recommendation engine**
6. **Add offline support with Service Workers**
7. **Create mobile app with same backend**

## 📚 Resources

- [Azure Static Web Apps Documentation](https://docs.microsoft.com/en-us/azure/static-web-apps/)
- [Azure API Management](https://docs.microsoft.com/en-us/azure/api-management/)
- [Azure Functions JavaScript Guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-node)
- [CosmosDB SQL API](https://docs.microsoft.com/en-us/azure/cosmos-db/sql-query-getting-started)

## 🤝 Support

For issues or questions:
- Check APIM Analytics for API errors
- Review Function App logs in Azure Portal
- Monitor CosmosDB metrics for performance
- Use browser DevTools for debugging

## ✅ DevOps Validation Checklist

### Pre-Deployment Validation

#### 1️⃣ **Azure Resources Verification**
- [ ] Resource Group `dev-swa-rg` exists and accessible
- [ ] APIM instance `book-system-apim` is running
- [ ] Azure Function `helloworldfunc09231920` is deployed
- [ ] CosmosDB `book-library-cosmos` is provisioned
- [ ] Static Web App `dev0002-standard` is active

#### 2️⃣ **API Management Configuration**
- [ ] APIM Gateway URL accessible: `https://book-system-apim.azure-api.net`
- [ ] Subscription key validated: `6854c6a9b0ff4b449f50b06f3e3b8d5e`
- [ ] CORS policy configured for all domains
- [ ] Operations created: GET /books, OPTIONS /books, GET /hello, OPTIONS /hello
- [ ] Backend URL points to Azure Function

#### 3️⃣ **Azure Function Validation**
- [ ] Function App is running (Status: Running)
- [ ] Environment variable `COSMOSDB_CONNECTION_STRING` is set
- [ ] Python runtime version 3.9 installed
- [ ] Required packages installed: `azure-functions`, `azure-cosmos`
- [ ] Endpoints accessible: `/api/hello`, `/api/books`

#### 4️⃣ **CosmosDB Verification**
- [ ] Database `BookLibraryDB` exists
- [ ] Container `Books` created with partition key `/category`
- [ ] 15 books successfully loaded
- [ ] Throughput configured: 400 RU/s minimum
- [ ] Connection string valid and accessible

#### 5️⃣ **Network & Security**
- [ ] CORS headers properly configured
- [ ] API subscription key active
- [ ] Network connectivity between services verified
- [ ] SSL/TLS certificates valid
- [ ] Firewall rules allow required traffic

#### 6️⃣ **Integration Testing**
- [ ] Test endpoint returns "Hello World"
- [ ] Books API returns 15 records
- [ ] Response time < 2 seconds
- [ ] Error handling returns proper status codes
- [ ] Cache headers configured correctly

### Deployment Validation Script

```bash
#!/bin/bash
# DevOps Validation Script for Library Azure Integration

echo "🔍 Starting DevOps Validation..."

# 1. Check Resource Group
echo "Checking Resource Group..."
az group show --name dev-swa-rg --output table

# 2. Validate APIM
echo "Validating API Management..."
az apim show --name book-system-apim --resource-group dev-swa-rg \
  --query "{Name:name,Status:provisioningState,Gateway:gatewayUrl}" --output table

# 3. Test APIM Endpoints
echo "Testing APIM Gateway..."
curl -s -o /dev/null -w "Hello Endpoint: %{http_code}\n" \
  "https://book-system-apim.azure-api.net/books/hello" \
  -H "Ocp-Apim-Subscription-Key: 6854c6a9b0ff4b449f50b06f3e3b8d5e"

curl -s -o /dev/null -w "Books Endpoint: %{http_code}\n" \
  "https://book-system-apim.azure-api.net/books/books" \
  -H "Ocp-Apim-Subscription-Key: 6854c6a9b0ff4b449f50b06f3e3b8d5e"

# 4. Check Azure Function
echo "Checking Azure Function..."
az functionapp show --name helloworldfunc09231920 --resource-group dev-swa-rg \
  --query "{Name:name,State:state,Runtime:siteConfig.pythonVersion}" --output table

# 5. Verify CosmosDB
echo "Verifying CosmosDB..."
az cosmosdb show --name book-library-cosmos --resource-group dev-swa-rg \
  --query "{Name:name,Status:provisioningState}" --output table

# 6. Count Books in Database
echo "Counting books in database..."
BOOK_COUNT=$(curl -s "https://book-system-apim.azure-api.net/books/books" \
  -H "Ocp-Apim-Subscription-Key: 6854c6a9b0ff4b449f50b06f3e3b8d5e" \
  | jq '.books | length')
echo "Total books in database: $BOOK_COUNT"

# 7. Check Static Web App
echo "Checking Static Web App..."
az staticwebapp show --name dev0002-standard --resource-group dev-swa-rg \
  --query "{Name:name,URL:defaultHostname,Status:provisioningState}" --output table

# 8. Performance Test
echo "Running performance test..."
time curl -s "https://book-system-apim.azure-api.net/books/books" \
  -H "Ocp-Apim-Subscription-Key: 6854c6a9b0ff4b449f50b06f3e3b8d5e" \
  -o /dev/null

echo "✅ Validation Complete!"
```

### Post-Deployment Monitoring

#### Performance Metrics to Track
- [ ] API response time < 500ms (p95)
- [ ] Error rate < 1%
- [ ] Availability > 99.9%
- [ ] RU consumption < 400 RU/s
- [ ] Cache hit ratio > 80%

#### Alerts to Configure
- [ ] Function App failures
- [ ] APIM 5xx errors
- [ ] CosmosDB throttling (429 errors)
- [ ] High latency (> 2s)
- [ ] SSL certificate expiry

### Rollback Plan

If integration fails:
1. **Revert Static Web App** to previous version
2. **Disable APIM operations** temporarily
3. **Check Function App logs** for errors
4. **Verify CosmosDB connectivity**
5. **Restore from backup** if data corruption

### Sign-off Criteria

- [ ] All checklist items validated ✅
- [ ] Performance tests passed
- [ ] Security scan completed
- [ ] Documentation updated
- [ ] Stakeholders notified

**DevOps Engineer**: ___________________ **Date**: _______________

**Project Manager**: ___________________ **Date**: _______________

---

**Ready to transform your static library into a dynamic Azure-powered application!** 🚀