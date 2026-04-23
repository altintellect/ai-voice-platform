// infra/modules/acs.bicep
@description('Project name')
param projectName string

@description('Environment name')
param environment string

resource acs 'Microsoft.Communication/communicationServices@2023-04-01' = {
  name: 'acs-${projectName}-${environment}'
  location: 'global'
  properties: {
    dataLocation: 'United States'
  }
  tags: {
    project: projectName
    environment: environment
    managedBy: 'bicep'
  }
}

output endpoint string = 'https://${acs.name}.communication.azure.com'
output acsName string = acs.name
output acsId string = acs.id
