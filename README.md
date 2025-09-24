# Book Library System - Workshop Demo

A complete serverless book management system built on Azure cloud architecture.

## 🚀 Quick Start

- **Dynamic Browse Books**: [index-dynamic-browse.html](https://jolly-hill-0d883e40f.2.azurestaticapps.net/index-dynamic-browse.html)
- **Real-time Interface**: [index-cosmodb.html](https://jolly-hill-0d883e40f.2.azurestaticapps.net/index-cosmodb.html)

## 📁 Project Structure

```
workshop-book-demo/
├── index*.html                    # Various HTML interfaces
├── staticwebapp.config.json      # Static Web App configuration
├── data/                          # Book JSON data files (15 books)
│   ├── book001.json → book015.json
├── scripts/                       # Python utility scripts
│   ├── insert-books-sdk.py       # CosmosDB insertion (Azure SDK)
│   └── insert-books.py           # CosmosDB insertion (REST API)
└── markdown/                      # Documentation
    ├── README.md                  # Comprehensive project docs
    ├── Library-Azure-Integration-Guide.md
    ├── Azure-CLI-Operations-Guide.md
    └── Other technical documentation
```

## 🎯 Azure Architecture

```
Browser → Static Web App → APIM Gateway → Azure Function → CosmosDB
```

## 📚 Features

- **15 Books** across 9 categories
- **Real-time search** and filtering
- **Azure Integration** (APIM, Functions, CosmosDB)
- **Responsive UI** with modern design
- **Complete documentation** for deployment and operations

For detailed information, see [markdown/README.md](markdown/README.md).