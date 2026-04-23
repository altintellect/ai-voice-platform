// infra/main.bicep
targetScope = 'subscription'

@description('Environment name')
param environment string = 'dev'

@description('Azure region')
param location string = 'eastus'

@description('Project name')
param projectName string = 'aivoice'

// Resource Group
resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${projectName}-${environment}'
  location: location
  tags: {
    project: projectName
    environment: environment
    managedBy: 'bicep'
  }
}

// Deploy all modules into the resource group
module acs 'modules/acs.bicep' = {
  name: 'acs-deployment'
  scope: rg
  params: {
    projectName: projectName
    environment: environment
    location: location
  }
}

module openai 'modules/openai.bicep' = {
  name: 'openai-deployment'
  scope: rg
  params: {
    projectName: projectName
    environment: environment
    location: location
  }
}

module storage 'modules/storage.bicep' = {
  name: 'storage-deployment'
  scope: rg
  params: {
    projectName: projectName
    environment: environment
    location: location
  }
}

module containerapp 'modules/containerapp.bicep' = {
  name: 'containerapp-deployment'
  scope: rg
  params: {
    projectName: projectName
    environment: environment
    location: location
  }
}

// Outputs
output resourceGroupName string = rg.name
output acsEndpoint string = acs.outputs.endpoint
output openAiEndpoint string = openai.outputs.endpoint
output containerAppUrl string = containerapp.outputs.url
