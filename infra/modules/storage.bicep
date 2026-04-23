// infra/modules/storage.bicep
@description('Project name')
param projectName string

@description('Environment name')
param environment string

@description('Azure region')
param location string

// Storage account name must be lowercase, max 24 chars, no hyphens
var storageAccountName = 'st${projectName}${environment}'

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
  tags: {
    project: projectName
    environment: environment
    managedBy: 'bicep'
  }
}

// Blob container for call recordings
resource recordingsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${storage.name}/default/recordings'
  properties: {
    publicAccess: 'None'
  }
}

output storageAccountName string = storage.name
output storageAccountId string = storage.id
output blobEndpoint string = storage.properties.primaryEndpoints.blob
