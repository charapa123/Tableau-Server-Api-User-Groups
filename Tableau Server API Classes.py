import requests
import pandas as pd
from datetime import datetime, timedelta

class Credentials:
    """
    Input Tableau Server Credentails:
    (Token Name,Token Secret,Site,Base URL,Endpoint e.g. workbooks,projects)"""
    def __init__(self,PATName,PATSecret,site,base_url,endpoint):
        self.PATName = PATName
        self.PATSecret = PATSecret
        self.site = site
        self.base_url = base_url
        self.endpoint = endpoint
        

    def setup(self):
        global token
        global site_id
        global headers_get
        global api
        global estimatedTimeToExpiration
        global future_time
        body = f'''<tsRequest>
    <credentials
        personalAccessTokenName="{self.PATName}" personalAccessTokenSecret="{self.PATSecret}">
        <site contentUrl="{self.site}" />
    </credentials>
</tsRequest>'''

        headers = {
    'Accept': 'application/json'
}
        api = 'api/3.11/'
        auth = 'auth/signin'
        url = self.base_url+api+auth

#.text shows the result in text
#r = requests.post(url,body,headers=headers).text
        r = requests.post(url,body,headers=headers).json()

        token = r['credentials']['token']
        site_id = r['credentials']['site']['id']
        estimatedTimeToExpiration = r['credentials']['estimatedTimeToExpiration']
        future_time = datetime.now() + timedelta(hours=int(estimatedTimeToExpiration.split(":")[0]), minutes=int(estimatedTimeToExpiration.split(":")[1]), seconds=int(estimatedTimeToExpiration.split(":")[2]))

        headers_get = {
    'Accept': 'application/json',
    'X-Tableau-Auth' : token
}
        return estimatedTimeToExpiration
    
    def chosen_endpoint(self):
        global all_data
        global new_base_get
        # endpoints = ['workbooks','projects','groups','views']
        
        # endpoint_url = []
        # for item in endpoints:
        #     url = f'{self.base_url}{api}sites/{site_id}/{item}?includeUsageStatistics=true&fields=_all_'
        #     endpoint_url.append(url)

        endpoint_url = f'{self.base_url}{api}sites/{site_id}/{self.endpoint}?includeUsageStatistics=true&fields=_all_'


        r = requests.get(endpoint_url,headers=headers_get).json()
        page_number = int(r['pagination']['pageNumber'])
        page_size = int(r['pagination']['pageSize'])
        total_available = int(r['pagination']['totalAvailable'])

        new_base_get = f'{self.base_url}{api}sites/{site_id}'


        all_data = []
        #this allows you to initialize the variables returned by the function to use seperately.
        current_page = page_number

        while total_available >= page_size*current_page:
            get = requests.get(new_base_get+'/'+self.endpoint+'?includeUsageStatistics=true&fields=_all_&pageNumber='+str(current_page),headers=headers_get).json()
            all_data.append(get)
            print(new_base_get+'/'+self.endpoint+'?includeUsageStatistics=true&fields=_all_&pageNumber='+str(current_page))
            current_page +=1  

        return all_data
    
    def permissions(self):
        global stuff
        global df_endpoint
        data = []
        for sublist in all_data:
            data.append(pd.json_normalize(sublist[f'{self.endpoint}'][f"{self.endpoint.rstrip('s')}"]))

        df_endpoint = pd.concat(data, ignore_index=True)

        df_endpoint['permissions'] = df_endpoint['id'].apply(lambda x: f'{new_base_get}/{self.endpoint}/{x}/permissions')

        projects_permission_url = df_endpoint['permissions'].to_list()

        # Initialize stuff as a list to store multiple permissions data
        stuff = []
        for download in projects_permission_url:
            permissions_data = requests.get(download, headers=headers_get).json()
            stuff.append(permissions_data)

        return stuff

    def permissions_group(self):
        project_permissions_download = []

        for permission_set in stuff:
            if 'permissions' in permission_set:
                data1 = permission_set['permissions']

                endpoint_id = data1.get(f"{self.endpoint.rstrip('s')}", {}).get('id', None)
                group_id = None

                if 'granteeCapabilities' in data1 and data1['granteeCapabilities']:
                    group_id = data1['granteeCapabilities'][0].get('group')

                if endpoint_id:
                    ids = {
                        'id': endpoint_id,
                        'group_id': group_id['id'] if group_id is not None else 'N/A'
                    }
                    project_permissions_download.append(ids)

        permissions_df = pd.DataFrame(project_permissions_download)

        endpoint_df_with_permissions = pd.merge(df_endpoint,permissions_df,'outer', right_on='id',left_on='id')

        return endpoint_df_with_permissions

    #endpoint_df_with_permissions



what = Credentials('','','','','workbooks')
print(what.setup())
# print(what.setup())
what.chosen_endpoint()
what.permissions()
print(what.permissions_group())