// infra/modules/openai.bicep
@description('Project name')
param projectName string

@description('Environment name')
param environment string

@description('Azure region')
param location string

var uniqueSuffix = take(uniqueString(resourceGroup().id), 6)

resource openai 'Microsoft.CognitiveServices/accounts@2024-04-01-preview' = {
  name: 'oai-${projectName}-${environment}-${uniqueSuffix}'
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: 'oai-${projectName}-${environment}-${uniqueSuffix}'
    publicNetworkAccess: 'Enabled'
  }
  tags: {
    project: projectName
    environment: environment
    managedBy: 'bicep'
  }
}

output endpoint string = openai.properties.endpoint
output openAiName string = openai.name
output openAiId string = openai.id
