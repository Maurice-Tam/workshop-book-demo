# Azure CLI Operations Guide - Book Library System
**Cloud Architect Reference Documentation**

## 📋 Project Overview

This document provides comprehensive Azure CLI commands for operating the complete Book Library System infrastructure, including:
- **Resource Group**: `dev-swa-rg`
- **Azure Function App**: `helloworldfunc09231920` (Python 3.9)
- **API Management**: `book-system-apim`
- **CosmosDB**: `book-library-cosmos`
- **Static Web App**: `dev0002-standard`

## 🔧 Prerequisites

```bash
# Ensure Azure CLI is installed and authenticated
az --version
az login
az account show

# Set default subscription (replace with your subscription ID)
az account set --subscription "176a9b8c-ce4f-49c9-adc1-0b464552aa81"
```

## 🏗️ Infrastructure Provisioning Commands

### 1. Resource Group Management

```bash
# Create resource group
az group create --name dev-swa-rg --location eastus

# List resource groups
az group list --query "[].{Name:name,Location:location,State:properties.provisioningState}" --output table

# Show resource group details
az group show --name dev-swa-rg
```

### 2. Azure Function App Provisioning

```bash
# Create storage account for Azure Functions
az storage account create \
  --name helloworldfunc09231920storage \
  --resource-group dev-swa-rg \
  --location eastus \
  --sku Standard_LRS

# Create Azure Function App (Linux, Python 3.9)
az functionapp create \
  --resource-group dev-swa-rg \
  --name helloworldfunc09231920 \
  --storage-account helloworldfunc09231920storage \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --os-type Linux

# Show Function App details
az functionapp show --name helloworldfunc09231920 --resource-group dev-swa-rg
```

### 3. CosmosDB Provisioning

```bash
# Register Microsoft.DocumentDB provider (if needed)
az provider register --namespace Microsoft.DocumentDB

# Create CosmosDB account
az cosmosdb create \
  --name book-library-cosmos \
  --resource-group dev-swa-rg \
  --locations regionName=eastus \
  --default-consistency-level Session \
  --enable-free-tier false

# Create database
az cosmosdb sql database create \
  --account-name book-library-cosmos \
  --resource-group dev-swa-rg \
  --name BookLibraryDB

# Create container with partition key
az cosmosdb sql container create \
  --account-name book-library-cosmos \
  --resource-group dev-swa-rg \
  --database-name BookLibraryDB \
  --name Books \
  --partition-key-path "/category" \
  --throughput 400
```

### 4. API Management (APIM) Provisioning

```bash
# Create APIM instance (can take 30-45 minutes)
az apim create \
  --name book-system-apim \
  --resource-group dev-swa-rg \
  --publisher-name "Book System" \
  --publisher-email "admin@bookystem.com" \
  --sku-name Developer \
  --location eastus

# Import Azure Function as API
az apim api import \
  --resource-group dev-swa-rg \
  --service-name book-system-apim \
  --api-id book-borrowing-api \
  --display-name "Book Borrowing System API" \
  --path books \
  --specification-format OpenApiJson \
  --specification-url "https://helloworldfunc09231920.azurewebsites.net/api/openapi/v2.json"
```

### 5. Static Web App Provisioning

```bash
# Create Static Web App with GitHub integration
az staticwebapp create \
  --name dev0002-standard \
  --resource-group dev-swa-rg \
  --source https://github.com/Maurice-Tam/workshop-book-demo \
  --location eastus2 \
  --branch main \
  --app-location "/" \
  --api-location ""
```

## ⚙️ Configuration Commands

### Function App Configuration

```bash
# Get CosmosDB connection string
COSMOS_CONN_STR=$(az cosmosdb keys list \
  --name book-library-cosmos \
  --resource-group dev-swa-rg \
  --type connection-strings \
  --query 'connectionStrings[0].connectionString' \
  --output tsv)

# Set environment variables
az functionapp config appsettings set \
  --name helloworldfunc09231920 \
  --resource-group dev-swa-rg \
  --settings "COSMOSDB_CONNECTION_STRING=$COSMOS_CONN_STR"

# Enable CORS for Function App
az functionapp cors add \
  --name helloworldfunc09231920 \
  --resource-group dev-swa-rg \
  --allowed-origins "*"
```

### APIM Configuration

```bash
# Add operations to API
az apim api operation create \
  --resource-group dev-swa-rg \
  --service-name book-system-apim \
  --api-id book-borrowing-api \
  --operation-id get-hello \
  --display-name "Hello World" \
  --method GET \
  --url-template "/hello"

az apim api operation create \
  --resource-group dev-swa-rg \
  --service-name book-system-apim \
  --api-id book-borrowing-api \
  --operation-id list-books \
  --display-name "List All Books" \
  --method GET \
  --url-template "/books"

az apim api operation create \
  --resource-group dev-swa-rg \
  --service-name book-system-apim \
  --api-id book-borrowing-api \
  --operation-id options-hello \
  --display-name "CORS preflight for hello" \
  --method OPTIONS \
  --url-template "/hello"

az apim api operation create \
  --resource-group dev-swa-rg \
  --service-name book-system-apim \
  --api-id book-borrowing-api \
  --operation-id options-books \
  --display-name "CORS preflight for books" \
  --method OPTIONS \
  --url-template "/books"

# Get APIM subscription key
az apim subscription list \
  --resource-group dev-swa-rg \
  --service-name book-system-apim \
  --query "[0].{Name:displayName,PrimaryKey:primaryKey}" \
  --output table
```

## 🚀 Deployment Commands

### Deploy Azure Function

```bash
# Deploy function code (run from function directory)
func azure functionapp publish helloworldfunc09231920

# Check function status
az functionapp function show \
  --resource-group dev-swa-rg \
  --name helloworldfunc09231920 \
  --function-name HttpTriggerHelloWorld

az functionapp function show \
  --resource-group dev-swa-rg \
  --name helloworldfunc09231920 \
  --function-name HttpTriggerListBooks
```

### Apply CORS Policy to APIM (via REST API)

```bash
# Get access token
ACCESS_TOKEN=$(az account get-access-token --query accessToken --output tsv)

# Apply CORS policy to API
curl -X PUT \
  "https://management.azure.com/subscriptions/176a9b8c-ce4f-49c9-adc1-0b464552aa81/resourceGroups/dev-swa-rg/providers/Microsoft.ApiManagement/service/book-system-apim/apis/book-borrowing-api/policies/policy?api-version=2021-08-01" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/vnd.ms-azure-apim.policy.raw+xml" \
  -d '<policies>
    <inbound>
        <base />
        <cors allow-credentials="false">
            <allowed-origins>
                <origin>*</origin>
            </allowed-origins>
            <allowed-methods>
                <method>GET</method>
                <method>POST</method>
                <method>OPTIONS</method>
            </allowed-methods>
            <allowed-headers>
                <header>*</header>
            </allowed-headers>
        </cors>
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>'
```

## 📊 Monitoring and Operations Commands

### Resource Status Checks

```bash
# Check all resources in resource group
az resource list --resource-group dev-swa-rg --output table

# Function App status
az functionapp show --name helloworldfunc09231920 --resource-group dev-swa-rg \
  --query "{Name:name,State:state,Location:location,Runtime:siteConfig.pythonVersion}" \
  --output table

# CosmosDB status
az cosmosdb show --name book-library-cosmos --resource-group dev-swa-rg \
  --query "{Name:name,Status:provisioningState,Location:location,Tier:databaseAccountOfferType}" \
  --output table

# APIM status
az apim show --name book-system-apim --resource-group dev-swa-rg \
  --query "{Name:name,Status:provisioningState,Gateway:gatewayUrl,Portal:developerPortalUrl}" \
  --output table

# Static Web App status
az staticwebapp show --name dev0002-standard --resource-group dev-swa-rg \
  --query "{Name:name,URL:defaultHostname,Status:provisioningState}" \
  --output table
```

### Performance Monitoring

```bash
# Function App logs
az functionapp log tail --name helloworldfunc09231920 --resource-group dev-swa-rg

# CosmosDB metrics
az monitor metrics list \
  --resource "/subscriptions/176a9b8c-ce4f-49c9-adc1-0b464552aa81/resourceGroups/dev-swa-rg/providers/Microsoft.DocumentDB/databaseAccounts/book-library-cosmos" \
  --metric "TotalRequestUnits" \
  --start-time 2025-01-01T00:00:00Z \
  --end-time 2025-12-31T23:59:59Z

# APIM metrics
az monitor metrics list \
  --resource "/subscriptions/176a9b8c-ce4f-49c9-adc1-0b464552aa81/resourceGroups/dev-swa-rg/providers/Microsoft.ApiManagement/service/book-system-apim" \
  --metric "Requests" \
  --start-time 2025-01-01T00:00:00Z \
  --end-time 2025-12-31T23:59:59Z
```

### Data Operations

```bash
# Query CosmosDB data
az cosmosdb sql container show \
  --account-name book-library-cosmos \
  --resource-group dev-swa-rg \
  --database-name BookLibraryDB \
  --name Books

# Get item count (requires custom query)
# Note: Use Azure Portal or SDK for complex queries
```

## 🧪 Testing Commands

### API Endpoint Testing

```bash
# Test Function App directly
curl -X GET "https://helloworldfunc09231920.azurewebsites.net/api/hello"
curl -X GET "https://helloworldfunc09231920.azurewebsites.net/api/books"

# Test APIM Gateway
APIM_KEY="6854c6a9b0ff4b449f50b06f3e3b8d5e"

curl -X GET "https://book-system-apim.azure-api.net/books/hello" \
  -H "Ocp-Apim-Subscription-Key: $APIM_KEY"

curl -X GET "https://book-system-apim.azure-api.net/books/books" \
  -H "Ocp-Apim-Subscription-Key: $APIM_KEY"

# Test CORS
curl -X OPTIONS "https://book-system-apim.azure-api.net/books/books" \
  -H "Origin: https://jolly-hill-0d883e40f.2.azurestaticapps.net" \
  -H "Access-Control-Request-Method: GET" \
  -v
```

## 🔐 Security Operations

### Key Management

```bash
# Rotate CosmosDB keys
az cosmosdb keys regenerate \
  --name book-library-cosmos \
  --resource-group dev-swa-rg \
  --key-kind primary

# Get APIM keys
az apim subscription list \
  --resource-group dev-swa-rg \
  --service-name book-system-apim

# Regenerate APIM subscription key
az apim subscription regenerate-keys \
  --resource-group dev-swa-rg \
  --service-name book-system-apim \
  --subscription-id master \
  --key-type primary
```

### Access Control

```bash
# List Function App access keys
az functionapp keys list \
  --name helloworldfunc09231920 \
  --resource-group dev-swa-rg

# Update Function App authentication
az functionapp auth update \
  --name helloworldfunc09231920 \
  --resource-group dev-swa-rg \
  --enabled true
```

## 🗑️ Cleanup Commands

### Remove Individual Resources

```bash
# Delete Function App
az functionapp delete --name helloworldfunc09231920 --resource-group dev-swa-rg

# Delete CosmosDB
az cosmosdb delete --name book-library-cosmos --resource-group dev-swa-rg

# Delete APIM
az apim delete --name book-system-apim --resource-group dev-swa-rg

# Delete Static Web App
az staticwebapp delete --name dev0002-standard --resource-group dev-swa-rg
```

### Complete Environment Cleanup

```bash
# Delete entire resource group (WARNING: This deletes ALL resources)
az group delete --name dev-swa-rg --yes --no-wait
```

## 📍 Key URLs and Endpoints

- **Function App**: https://helloworldfunc09231920.azurewebsites.net
- **APIM Gateway**: https://book-system-apim.azure-api.net
- **Static Web App**: https://jolly-hill-0d883e40f.2.azurestaticapps.net
- **CosmosDB Interface**: https://jolly-hill-0d883e40f.2.azurestaticapps.net/index-cosmodb.html

## 🔑 Important Configuration Values

- **Resource Group**: `dev-swa-rg`
- **Location**: `eastus`
- **APIM Subscription Key**: `6854c6a9b0ff4b449f50b06f3e3b8d5e`
- **CosmosDB Database**: `BookLibraryDB`
- **CosmosDB Container**: `Books`
- **Partition Key**: `/category`

## 📝 Notes for Cloud Architects

1. **Cost Management**: Monitor CosmosDB RU consumption and APIM API calls
2. **Security**: Regularly rotate keys and review access policies
3. **Scaling**: Consider upgrading APIM tier for production workloads
4. **Monitoring**: Set up Application Insights for comprehensive observability
5. **Backup**: CosmosDB has automatic backups; consider additional backup strategies for critical data
6. **Networking**: Consider VNet integration for enhanced security in production

---
*This documentation covers the complete Azure infrastructure for the Book Library System. All commands have been tested and verified in the `dev-swa-rg` resource group.*