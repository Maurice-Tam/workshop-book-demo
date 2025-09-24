# 📋 Azure API Management Provisioning Checklist

**Project**: Book Borrowing System
**Azure Function**: helloworldfunc09231920
**Resource Group**: dev-swa-rg
**Date**: ___________
**DevOps Engineer**: ___________

---

## 🚀 Pre-Deployment Prerequisites

### ✅ Environment Validation
- [ ] Azure CLI installed and updated (`az --version`)
- [ ] Logged into correct Azure subscription
  ```bash
  az account show --query "name" -o tsv
  # Should return: "Visual Studio Enterprise Subscription"
  ```
- [ ] Confirm subscription ID: `176a9b8c-ce4f-49c9-adc1-0b464552aa81`
- [ ] Verify permissions: Contributor role on subscription or resource group

### ✅ Resource Provider Registration
- [ ] **CRITICAL**: Register API Management provider
  ```bash
  az provider register --namespace Microsoft.ApiManagement
  az provider show --namespace Microsoft.ApiManagement --query "registrationState"
  # Should return: "Registered" (may take 2-5 minutes)
  ```

### ✅ Existing Resources Validation
- [ ] Verify Function App is running
  ```bash
  az functionapp show --name helloworldfunc09231920 --resource-group dev-swa-rg --query "state"
  # Should return: "Running"
  ```
- [ ] Test Function App endpoint directly
  ```bash
  curl https://helloworldfunc09231920.azurewebsites.net/api/hello
  # Should return: "Hello World!" message
  ```
- [ ] Retrieve Function App key
  ```bash
  FUNCTION_KEY=$(az functionapp keys list --resource-group dev-swa-rg --name helloworldfunc09231920 --query "functionKeys.default" --output tsv)
  echo "Function Key: $FUNCTION_KEY"
  # Should return: Base64 encoded key
  ```

### ✅ Network Prerequisites
- [ ] Confirm Canada Central region availability
  ```bash
  az account list-locations --query "[?name=='canadacentral']" -o table
  ```
- [ ] Verify no existing APIM service with same name
  ```bash
  az apim list --resource-group dev-swa-rg -o table
  # Should return empty or no conflicts with "book-system-apim"
  ```

---

## 🏗️ Deployment Execution

### ✅ Step 1: Set Environment Variables
```bash
# Copy and execute these commands
export RESOURCE_GROUP="dev-swa-rg"
export APIM_NAME="book-system-apim"
export LOCATION="canadacentral"
export FUNCTION_APP="helloworldfunc09231920"
export PUBLISHER_EMAIL="your-email@domain.com"  # UPDATE THIS
export PUBLISHER_NAME="Book System Admin"

# Verify variables are set
echo "Resource Group: $RESOURCE_GROUP"
echo "APIM Name: $APIM_NAME"
echo "Location: $LOCATION"
echo "Function App: $FUNCTION_APP"
```

**Action Required**:
- [ ] Update `PUBLISHER_EMAIL` with your actual email address

### ✅ Step 2: Create APIM Service
- [ ] Execute APIM creation command
  ```bash
  echo "Starting APIM creation at $(date)"
  az apim create \
    --resource-group $RESOURCE_GROUP \
    --name $APIM_NAME \
    --location $LOCATION \
    --publisher-email $PUBLISHER_EMAIL \
    --publisher-name "$PUBLISHER_NAME" \
    --sku-name Developer \
    --sku-capacity 1
  ```
- [ ] **Expected Duration**: 45-60 minutes ⏱️
- [ ] Monitor creation status
  ```bash
  # Check status periodically
  az apim show --resource-group $RESOURCE_GROUP --name $APIM_NAME --query "provisioningState"
  ```

### ✅ Step 3: Retrieve Function App Key
- [ ] Get Function App authentication key
  ```bash
  FUNCTION_KEY=$(az functionapp keys list \
    --resource-group $RESOURCE_GROUP \
    --name $FUNCTION_APP \
    --query "functionKeys.default" \
    --output tsv)
  echo "Retrieved Function Key: ${FUNCTION_KEY:0:10}..." # Show first 10 chars only
  ```

### ✅ Step 4: Create Backend Configuration
- [ ] Create Function App backend
  ```bash
  az apim backend create \
    --resource-group $RESOURCE_GROUP \
    --service-name $APIM_NAME \
    --backend-id "helloworldfunc-backend" \
    --url "https://$FUNCTION_APP.azurewebsites.net/api" \
    --protocol http \
    --credentials-header x-functions-key=$FUNCTION_KEY
  ```
- [ ] Verify backend creation
  ```bash
  az apim backend show --resource-group $RESOURCE_GROUP --service-name $APIM_NAME --backend-id "helloworldfunc-backend"
  ```

### ✅ Step 5: Create API Definition
- [ ] Create main API
  ```bash
  az apim api create \
    --resource-group $RESOURCE_GROUP \
    --service-name $APIM_NAME \
    --api-id "book-borrowing-api" \
    --path "/books" \
    --display-name "Book Borrowing System API" \
    --protocols https
  ```

### ✅ Step 6: Create Hello World Operations
- [ ] Add GET /hello operation
  ```bash
  az apim api operation create \
    --resource-group $RESOURCE_GROUP \
    --service-name $APIM_NAME \
    --api-id "book-borrowing-api" \
    --operation-id "hello-world" \
    --method GET \
    --url-template "/hello" \
    --display-name "Hello World"
  ```
- [ ] Add OPTIONS /hello operation for CORS preflight
  ```bash
  az apim api operation create \
    --resource-group $RESOURCE_GROUP \
    --service-name $APIM_NAME \
    --api-id "book-borrowing-api" \
    --operation-id "hello-world-options" \
    --method OPTIONS \
    --url-template "/hello" \
    --display-name "Hello World Options"
  ```

### ✅ Step 7: Configure CORS Policy
- [ ] Apply CORS policy via REST API (Azure CLI policy commands may not work)
  ```bash
  # Get access token
  ACCESS_TOKEN=$(az account get-access-token --query "accessToken" --output tsv)

  # Apply CORS policy via REST API
  curl -X PUT "https://management.azure.com/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ApiManagement/service/$APIM_NAME/apis/book-borrowing-api/policies/policy?api-version=2021-08-01" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/vnd.ms-azure-apim.policy.raw+xml" \
    -d '<policies>
    <inbound>
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
          <header>Content-Type</header>
          <header>Authorization</header>
          <header>Accept</header>
        </allowed-headers>
      </cors>
      <set-backend-service base-url="https://$FUNCTION_APP.azurewebsites.net/api" />
      <set-header name="x-functions-key" exists-action="override">
        <value>$FUNCTION_KEY</value>
      </set-header>
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
- [ ] **IMPORTANT**: Cannot mix wildcard origin (`*`) with specific origins
- [ ] Verify CORS policy was applied successfully

---

## 🔍 Post-Deployment Verification

### ✅ Service Health Checks
- [ ] Verify APIM service is running
  ```bash
  az apim show --resource-group $RESOURCE_GROUP --name $APIM_NAME --query "{name:name, state:state, gatewayUrl:gatewayUrl}"
  ```
- [ ] Check API Management gateway URL
  ```bash
  GATEWAY_URL=$(az apim show --resource-group $RESOURCE_GROUP --name $APIM_NAME --query "gatewayUrl" -o tsv)
  echo "Gateway URL: $GATEWAY_URL"
  ```

### ✅ API Endpoint Testing
- [ ] Test Hello World endpoint without parameters
  ```bash
  curl -X GET "$GATEWAY_URL/books/hello"
  # Expected: "Hello World! This HTTP triggered function executed successfully..."
  ```
- [ ] Test Hello World endpoint with name parameter
  ```bash
  curl -X GET "$GATEWAY_URL/books/hello?name=DevOpsEngineer"
  # Expected: "Hello, DevOpsEngineer! This HTTP triggered function executed successfully."
  ```

### ✅ CORS Validation
- [ ] Test CORS preflight request (should return 200, not 404)
  ```bash
  curl -X OPTIONS "$GATEWAY_URL/books/hello" \
    -H "Origin: https://jolly-hill-0d883e40f.2.azurestaticapps.net" \
    -H "Access-Control-Request-Method: GET" \
    -v
  # Expected: HTTP/1.1 200 OK with Access-Control-Allow-* headers
  # If 404: OPTIONS operation missing, go back to Step 6
  ```
- [ ] Test actual GET request with Origin header
  ```bash
  curl -X GET "$GATEWAY_URL/books/hello?name=TestUser" \
    -H "Origin: https://jolly-hill-0d883e40f.2.azurestaticapps.net" \
    -v
  # Expected: Access-Control-Allow-Origin: * header present
  ```

### ✅ Rate Limiting Test
- [ ] Verify rate limiting is active
  ```bash
  # Make multiple rapid requests
  for i in {1..5}; do
    curl -X GET "$GATEWAY_URL/books/hello" -w "Response: %{http_code}\n" -o /dev/null -s
    sleep 1
  done
  # Should show 200 responses with rate limiting headers
  ```

### ✅ Management Portal Access
- [ ] Access Developer Portal
  ```bash
  DEVELOPER_PORTAL=$(az apim show --resource-group $RESOURCE_GROUP --name $APIM_NAME --query "developerPortalUrl" -o tsv)
  echo "Developer Portal: $DEVELOPER_PORTAL"
  # Manually verify portal is accessible in browser
  ```

---

## 📊 Monitoring Setup

### ✅ Application Insights Configuration
- [ ] Verify Application Insights is connected
  ```bash
  az apim show --resource-group $RESOURCE_GROUP --name $APIM_NAME --query "additionalProperties.Microsoft.ApiManagement/service/gateways/configurations/ingestion"
  ```
- [ ] Test logging functionality
  ```bash
  # Make a few API calls and check if they appear in Application Insights
  curl -X GET "$GATEWAY_URL/books/hello?name=TestUser"
  ```

### ✅ Health Monitoring
- [ ] Set up health check endpoint
  ```bash
  # The /hello endpoint serves as a health check
  curl -X GET "$GATEWAY_URL/books/hello" --max-time 5
  # Should respond within 5 seconds
  ```

---

## 🎯 Final Validation Checklist

### ✅ Complete System Test
- [ ] **Static Web App Integration**: Test from actual Static Web App
  - Visit: `https://jolly-hill-0d883e40f.2.azurestaticapps.net/index-with-api.html`
  - Enter a test name and click "Call Azure Function"
  - Should receive personalized greeting through APIM

- [ ] **Direct API Access**: Test API directly
  ```bash
  # Test both endpoints work
  curl -X GET "$GATEWAY_URL/books/hello"
  curl -X GET "$GATEWAY_URL/books/hello?name=FinalTest"
  ```

- [ ] **Error Handling**: Test invalid requests
  ```bash
  curl -X GET "$GATEWAY_URL/books/nonexistent"
  # Should return appropriate error response
  ```

### ✅ Documentation Updates
- [ ] Record actual Gateway URL in documentation
- [ ] Update any hardcoded URLs in Static Web App if needed
- [ ] Document any deviations from original plan

---

## 📈 Success Criteria

✅ **All items below must be checked for successful deployment:**

- [ ] APIM service created and running
- [ ] Backend connection to Function App established
- [ ] API operations created and functional
- [ ] CORS policy applied and working
- [ ] Rate limiting active
- [ ] Static Web App can call API through APIM
- [ ] Monitoring and logging operational
- [ ] All test endpoints return expected responses

---

## 🚨 Troubleshooting Common Issues

### ✅ CORS Issues (NetworkError when attempting to fetch resource)
**If browser shows "TypeError: NetworkError when attempting to fetch resource":**

- [ ] Check if OPTIONS operation exists
  ```bash
  az apim api operation list --resource-group dev-swa-rg --service-name book-system-apim --api-id "book-borrowing-api" --output table
  # Should show both GET and OPTIONS operations
  ```
- [ ] Test CORS preflight manually
  ```bash
  curl -X OPTIONS "https://book-system-apim.azure-api.net/books/hello" -v
  # Should return 200, not 404
  ```
- [ ] If CORS policy not working, reapply via REST API (see Step 7)
- [ ] Verify wildcard origin (*) is used alone, not mixed with specific origins

### ✅ Emergency Rollback Steps
**If deployment fails or issues occur:**

- [ ] Remove APIM service
  ```bash
  az apim delete --resource-group $RESOURCE_GROUP --name $APIM_NAME --yes --no-wait
  ```
- [ ] Verify Static Web App still works with direct Function App calls
- [ ] Document issues encountered
- [ ] Review logs and error messages

---

## 📝 Deployment Log

**Start Time**: ___________
**End Time**: ___________
**Total Duration**: ___________
**Issues Encountered**: ___________
**Resolution Notes**: ___________

**Final Gateway URL**: ___________
**Status**: ✅ Success / ❌ Failed / ⚠️ Partial

**DevOps Engineer Signature**: ___________
**Date Completed**: ___________

---

## 📞 Support Contacts

- **Azure Support**: Standard Support Plan
- **Technical Documentation**: [APIM-Provisioning-Guide.md](./APIM-Provisioning-Guide.md)
- **Function App URL**: https://helloworldfunc09231920.azurewebsites.net
- **Static Web App URL**: https://jolly-hill-0d883e40f.2.azurestaticapps.net

---

*This checklist ensures systematic deployment and validation of Azure API Management for the Book Borrowing System.*