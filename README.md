# AI Demo Generator

The AI Demo Generator is a Streamlit-based tool that helps you quickly generate and iterate on code based on your use case descriptions. It leverages OpenAI to create detailed descriptions and corresponding code, allowing for easy editing and management of demos.

## Features

- **Use Case Description**: Describe your desired functionality in natural language.
- **AI-powered Code Generation**: Automatically generate detailed descriptions and corresponding code.
- **Code Execution**: Run the generated code and see results immediately.
- **Interactive Editing**: Make changes to the generated code through natural language requests.
- **Demo Management**: Save, view, load, and delete demos for future reference.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/kmavrodis/demo-generator-with-openai.git
   cd ai-demo-generator
   ```

2. Create an Azure Cosmos DB Account, Database, and Container:

   The AI Demo Generator uses Azure Cosmos DB to store and manage demos. Follow these steps to set up your Cosmos DB resources:

   #### Create a Cosmos DB Account:

   Use the Azure Portal or Azure CLI to create a new Cosmos DB account with SQL API:
   ```
   az cosmosdb create \
   --name $accountName \
   --resource-group $resourceGroupName \
   --kind GlobalDocumentDB
   ```

   #### Create a Database and Container:
   ```
   az cosmosdb sql database create \
   --account-name $accountName \
   --resource-group $resourceGroupName \
   --name $databaseName

   az cosmosdb sql container create \
   --account-name $accountName \
   --resource-group $resourceGroupName \
   --database-name $databaseName \
   --name $containerName \
   --partition-key-path "/id"
   ```
   #### Assign Role to Principal ID:

   To grant your application access to the Cosmos DB account, assign the "Cosmos DB Built-in Data Contributor" role to your Azure Active Directory (AD) principal.

   First, get the scope of your Cosmos DB account:
   ```
   scope=$(
      az cosmosdb show \
         --resource-group $resourceGroupName \
         --name $accountName \
         --query id \
         --output tsv
   )
   ```
   Then, create a role assignment:

   ```
   az cosmosdb sql role assignment create \
      --resource-group $resourceGroupName \
      --account-name $accountName \
      --role-definition-name "Cosmos DB Built-in Data Contributor" \
      --principal-id $principalId \
      --scope $scope
   ```
   The principalId is the unique identifier (object ID) of the Azure AD entity (user, group, or service principal) that you want to assign the role to. It specifies who will receive the permissions defined by the role.

   To get the principal ID of the currently signed-in user:
   ```
   principalId=$(az ad signed-in-user show --query objectId -o tsv)
   ```
   To get the principal ID of a service principal:
   ```
   principalId=$(az ad sp show --id "http://your-service-principal-app-id" --query objectId -o tsv)
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables in a `.env` file:
   ```
   AZURE_WHISPER_KEY=your_azure_whisper_key
   AZURE_WHISPER_DEPLOYMENT=your_azure_whisper_deployment
   AZURE_WHISPER_ENDPOINT=your_azure_whisper_endpoint
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_DEPLOYMENT_NAME=your_openai_deployment_name
   OPENAI_ENDPOINT=your_openai_endpoint
   DOCUMENT_INTELLIGENCE_ENDPOINT=your_document_intelligence_endpoint
   DOCUMENT_INTELLIGENCE_KEY=your_document_intelligence_key
   COSMOS_DB_ENDPOINT=your_cosmos_db_endpoint
   COSMOS_DB_DATABASE_NAME=your_database_name
   COSMOS_DB_CONTAINER_NAME=your_container_name
   ```

## Usage

Run the Streamlit app:
```
streamlit run app.py
```

Follow the instructions in the app to:
1. Describe your use case
2. Generate a demo
3. Run the generated code
4. Edit the code as needed
5. Manage your demos

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
