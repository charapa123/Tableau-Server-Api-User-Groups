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
        global df_endpoint
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

        while total_available >= page_size*len(all_data):
            get = requests.get(new_base_get+'/'+self.endpoint+'?includeUsageStatistics=true&fields=_all_&pageNumber='+str(current_page),headers=headers_get).json()
            all_data.append(get)
            print(new_base_get+'/'+self.endpoint+'?includeUsageStatistics=true&fields=_all_&pageNumber='+str(current_page))
            current_page +=1 

            data = []
            for sublist in all_data:
                data.append(pd.json_normalize(sublist[f'{self.endpoint}'][f"{self.endpoint.rstrip('s')}"]))

        df_endpoint = pd.concat(data, ignore_index=True)

        return df_endpoint
    
    def permissions(self):
        global stuff

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



workbooks = Credentials('','','','','workbooks')
projects = Credentials('','','','','projects')
views = Credentials('','','','','views')
groups = Credentials('','','','','groups')
workbooks.setup()
workbooks.chosen_endpoint()
workbooks.permissions()

df_workbook = workbooks.permissions_group()

df_workbook = df_workbook[['id','name','project.id','group_id']].rename(columns = {'id' :'Workbook_id','name':'Workbook_name','group_id':'Workbook_group_id'})

df_workbook = df_workbook[df_workbook['Workbook_group_id'] != 'N/A']

projects.setup()
projects.chosen_endpoint()
projects.permissions()
df_projects = projects.permissions_group()



df_projects = df_projects[['id','name','group_id']].rename(columns = {'id' :'project_id','name':'project_name','group_id':'projects_group_id'})

df_projects = df_projects[df_projects['projects_group_id'] != 'N/A']


views.setup()
views.chosen_endpoint()
views.permissions()
df_views = views.permissions_group()


df_views = df_views[['name','group_id','workbook.id','project.id']].rename(columns = {'name':'view_name','group_id':'view_group_id'})

df_views = df_views[df_views['view_group_id'] != 'N/A']

groups.setup()
df_groups = groups.chosen_endpoint()



df_part_1 = pd.merge(df_views,df_workbook,'inner',right_on=['Workbook_id','project.id'],left_on=['workbook.id','project.id'])

df_part_2 = pd.merge(df_part_1,df_projects,'outer',left_on='project.id',right_on='project_id')

df_part_3 = pd.melt(df_part_2,id_vars=['view_name','project_name','Workbook_name','project_id'])

df_Final = pd.merge(df_groups,df_part_3,'outer',left_on='id',right_on='value')







