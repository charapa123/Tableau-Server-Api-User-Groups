import requests
import pandas as pd

class Credentials:

    token = None
    site_id = None
    headers_get = None
    api = 'api/3.11/'

    def __init__(self,PATName,PATSecret,site,base_url,endpoint):
        self.PATName = PATName
        self.PATSecret = PATSecret
        self.site = site
        self.base_url = base_url
        self.endpoint = endpoint


        # Run setup if the session hasn't been initialized yet
        if not Credentials.token or not Credentials.site_id:
            self.setup()

    def setup(self):
        global token
        global site_id
        global headers_get
        global api
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

        headers_get = {
    'Accept': 'application/json',
    'X-Tableau-Auth' : token
}
        return
    
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
        data = []
        for sublist in all_data:
            data.append(pd.json_normalize(sublist[f'{self.endpoint}'][f"{self.endpoint.rstrip('s')}"]))

        df_endpoint = pd.concat(data,ignore_index=True)

        df_endpoint['permissions'] = df_endpoint['id'].apply(lambda x: f'{new_base_get}/{self.endpoint}/{x}/permissions')

        projects_permission_url = df_endpoint['permissions'].to_list()

        for download in projects_permission_url:
            stuff = pd.DataFrame(requests.get(download, headers=headers_get).json())

        return stuff
    
    def permissions_group(self):

            # data1 = stuff['permissions']
            # endpoint_id = data1[f"{self.endpoint.rstrip('s')}"]['id']

            if 'permissions' in stuff:
                data1 = stuff['permissions']
                endpoint_id = data1.get(f"{self.endpoint.rstrip('s')}", {}).get('id', None)

            project_permissions_download = []


            # Check if 'granteeCapabilities' exists and is a list with at least one item
            #.get('group') used as some group id's are empty this handles such occasions.
            if 'granteeCapabilities' in data1 and data1['granteeCapabilities']:
                group_id = data1['granteeCapabilities'][0].get('group')
            else:
                group_id = None

            # Only append if project_id is not None
            if endpoint_id:
                ids = {
                    'id': endpoint_id,
                    'group_id': group_id['id'] if group_id is not None else 'N/A'  # Use 'N/A' if group_id is None
                }
                project_permissions_download.append(ids)

            permissions_df = pd.DataFrame(project_permissions_download)

            # endpoint_df = pd.DataFrame(stuff)

            # endpoint_df_with_permissions = pd.merge(endpoint_df,permissions_df,'outer', right_on='id',left_on='id')

            return permissions_df
    #endpoint_df_with_permissions



    

stuff = Credentials('','','','','workbooks')

print(stuff.setup())
stuff.chosen_endpoint()
stuff.permissions()
print(stuff.permissions_group())