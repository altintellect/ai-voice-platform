// infra/modules/openai.bicep
@description('Project name')
param projectName string

@description('Environment name')
param environment string

@description('Azure region')
param location string

resource openai 'Microsoft.CognitiveServices/accounts@2024-04-01-preview' = {
  name: 'oai-${projectName}-${environment}'
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: 'oai-${projectName}-${environment}'
    publicNetworkAccess: 'Enabled'
  }
  tags: {
    project: projectName
    environment: environment
    managedBy: 'bicep'
  }
}

// GPT-4o deployment
resource gpt4o 'Microsoft.CognitiveServices/accounts/deployments@2024-04-01-preview' = {
  parent: openai
  name: 'gpt-4o'
  sku: {
    name: 'Standard'
    capacity: 10
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-11-20'
    }
  }
}

// Whisper deployment for STT
resource whisper 'Microsoft.CognitiveServices/accounts/deployments@2024-04-01-preview' = {
  parent: openai
  name: 'whisper'
  sku: {
    name: 'Standard'
    capacity: 1
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'whisper'
      version: '001'
    }
  }
  dependsOn: [gpt4o]
}

output endpoint string = openai.properties.endpoint
output openAiName string = openai.name
output openAiId string = openai.id
