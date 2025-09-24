# Book Library System - Workshop Demo

A complete serverless book management system built on Azure cloud architecture, demonstrating modern web development practices with real-time database integration.

## 🌟 Live Demo

- **Main Application**: https://jolly-hill-0d883e40f.2.azurestaticapps.net/index-cosmodb.html
- **APIM Gateway**: https://book-system-apim.azure-api.net/books
- **Function API**: https://helloworldfunc09231920.azurewebsites.net/api

## 🏗️ Architecture

```
Browser → Static Web App → APIM Gateway → Azure Function → CosmosDB
```

### Components
- **Frontend**: Modern HTML5 interface with real-time book browsing
- **API Gateway**: Azure API Management with CORS and subscription key authentication
- **Backend**: Python Azure Functions with CosmosDB integration
- **Database**: Azure CosmosDB (SQL API) with category-based partitioning
- **Hosting**: Azure Static Web Apps with GitHub Actions CI/CD

## 📱 Features

### Book Management
- **Browse Books**: View all books with detailed information
- **Category Filtering**: Filter by Technology, Business, Science, Fiction
- **Real-time Statistics**: Total books, available, borrowed counts
- **Availability Indicators**: Color-coded availability status

### User Interface
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Glass-morphism effects with gradient backgrounds
- **Interactive Controls**: Load, refresh, and filter operations
- **Error Handling**: User-friendly error messages and loading states

### Technical Features
- **Real-time Data**: Direct CosmosDB integration via Azure Functions
- **CORS Support**: Proper cross-origin request handling
- **API Testing**: Built-in hello world endpoint testing
- **Auto-deployment**: GitHub Actions for continuous deployment

## 🚀 Quick Start

### View the Application
1. Visit: https://jolly-hill-0d883e40f.2.azurestaticapps.net/index-cosmodb.html
2. Click "Load Books" to fetch data from CosmosDB
3. Use category filters to browse books by type
4. View real-time statistics and book details

### Test API Endpoints
```bash
# Test Hello World endpoint
curl "https://book-system-apim.azure-api.net/books/hello" \
  -H "Ocp-Apim-Subscription-Key: 6854c6a9b0ff4b449f50b06f3e3b8d5e"

# Test Books API
curl "https://book-system-apim.azure-api.net/books/books" \
  -H "Ocp-Apim-Subscription-Key: 6854c6a9b0ff4b449f50b06f3e3b8d5e"
```

## 📊 Sample Data

The system includes 5 sample books across different categories:

- **Technology**: Clean Code: A Handbook of Agile Software Craftsmanship
- **Business**: The Lean Startup, Atomic Habits
- **Science**: Sapiens: A Brief History of Humankind
- **Fiction**: Dune

Each book includes:
- Title, author, ISBN, publication year
- Category-based organization
- Inventory tracking (total, available, borrowed counts)
- Detailed descriptions

## 🔧 Development

### Local Development
```bash
# Run Azure Functions locally
cd ../
func start

# Deploy to Azure
func azure functionapp publish helloworldfunc09231920
```

### Add New Books
```bash
# Using Azure Cosmos SDK
python insert-books-sdk.py

# Using REST API
python insert-books.py
```

## 📁 Project Structure

```
workshop-book-demo/
├── index-cosmodb.html          # Main application interface
├── index-with-apim.html        # APIM integration demo
├── index-with-api.html         # Direct API integration
├── index.html                  # Original static demo
├── book001-005.json           # Sample book data
├── insert-books-sdk.py        # CosmosDB data insertion (SDK)
├── insert-books.py            # CosmosDB data insertion (REST)
├── staticwebapp.config.json   # Static Web App configuration
├── Azure-CLI-Operations-Guide.md      # Infrastructure operations
├── CosmosDB-Book-API-Feature.md       # Database schema & API spec
├── APIM-Provisioning-Guide.md         # APIM setup guide
└── .github/workflows/         # GitHub Actions deployment
```

## 🔑 Configuration

### Azure Resources (Resource Group: `dev-swa-rg`)
- **Function App**: `helloworldfunc09231920`
- **API Management**: `book-system-apim`
- **CosmosDB**: `book-library-cosmos`
- **Static Web App**: `dev0002-standard`

### Environment Variables
- `COSMOSDB_CONNECTION_STRING`: Required for database access
- `FUNCTIONS_WORKER_RUNTIME`: Set to `python`

### API Configuration
- **APIM Subscription Key**: `6854c6a9b0ff4b449f50b06f3e3b8d5e`
- **CosmosDB Database**: `BookLibraryDB`
- **CosmosDB Container**: `Books` (Partition Key: `/category`)

## 📚 Documentation

- **[Azure CLI Operations Guide](Azure-CLI-Operations-Guide.md)**: Complete infrastructure management
- **[CosmosDB Feature Specification](CosmosDB-Book-API-Feature.md)**: Database design and API documentation
- **[APIM Provisioning Guide](APIM-Provisioning-Guide.md)**: API Management setup and CORS configuration

## 🔒 Security

- **API Authentication**: Subscription key-based access
- **CORS Configuration**: Proper cross-origin request handling
- **Environment Variables**: Secure connection string management
- **Anonymous Access**: Configured for demo purposes (production should implement proper auth)

## 🚦 Deployment

### Automatic Deployment
- **Trigger**: Push to `main` branch
- **Pipeline**: GitHub Actions workflow
- **Target**: Azure Static Web Apps
- **Status**: Auto-deploys HTML, CSS, JS files

### Manual Deployment
```bash
# Deploy static content
git add .
git commit -m "Update static content"
git push origin main

# Deploy Azure Functions
func azure functionapp publish helloworldfunc09231920
```

## 🎯 Use Cases

### Educational
- Learn Azure serverless architecture
- Understand API Management concepts
- Practice modern web development
- Explore CosmosDB capabilities

### Business
- Book library management system
- Inventory tracking demonstration
- API-first architecture example
- Cloud-native application showcase

## 🛠️ Technologies Used

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python 3.9, Azure Functions
- **Database**: Azure CosmosDB (SQL API)
- **API Management**: Azure APIM with CORS
- **Hosting**: Azure Static Web Apps
- **CI/CD**: GitHub Actions
- **Authentication**: API key-based

## 📈 Monitoring

- **Application Insights**: Telemetry and performance monitoring
- **Function Logs**: Real-time debugging via Azure CLI
- **APIM Analytics**: API usage and performance metrics
- **CosmosDB Metrics**: Request units and query performance

## 🤝 Contributing

This is a demonstration project showcasing Azure cloud architecture. For educational modifications:

1. Fork the repository
2. Create feature branches
3. Test changes locally with Azure Functions Core Tools
4. Submit pull requests with clear descriptions

## 📄 License

This project is created for educational and demonstration purposes. Feel free to use and modify for learning Azure cloud development.

---

**Built with Azure Cloud Services** | **Powered by CosmosDB & API Management** | **Deployed via GitHub Actions**