import pandas as pd
import requests

base_url = 'url'
auth = 'auth/signin'
site = '<>'
api = 'api/3.11/'

PATName = 'Token'
PATSecret = '<>'

url = base_url+api+auth
#triple quotes used to indent multiple lines
body = f'''<tsRequest>
    <credentials
        personalAccessTokenName="{PATName}" personalAccessTokenSecret="{PATSecret}">
        <site contentUrl="{site}" />
    </credentials>
</tsRequest>'''

headers = {
    'Accept': 'application/json'
}

#.text shows the result in text
#r = requests.post(url,body,headers=headers).text
r = requests.post(url,body,headers=headers).json()

print(r)
#getting token to authorise API request
token = r['credentials']['token']
site_id = r['credentials']['site']['id']

url_for_workbooks = f'{base_url}{api}sites/{site_id}/workbooks?includeUsageStatistics=true&fields=_all_'
url_for_projects = f'{base_url}{api}sites/{site_id}/projects?includeUsageStatistics=true&fields=_all_'
url_for_groups = f'{base_url}{api}sites/{site_id}/groups?includeUsageStatistics=true&fields=_all_'
url_for_views = f'{base_url}{api}sites/{site_id}/views?includeUsageStatistics=true&fields=_all_'


headers_get = {
    'Accept': 'application/json',
    'X-Tableau-Auth' : token
}

# r_get = requests.get(url_for_get_request,headers=headers_get).json()

def get_page_diff_endpoint(url):
    r = requests.get(url,headers=headers_get).json()
    page_number = int(r['pagination']['pageNumber'])
    page_size = int(r['pagination']['pageSize'])
    total_available = int(r['pagination']['totalAvailable'])
    return page_number,page_size,total_available

endpoint_workbooks = '/workbooks?includeUsageStatistics=true&fields=_all_&pageNumber='
endpoint_projects = '/projects?includeUsageStatistics=true&fields=_all_&pageNumber='
endpoint_groups = '/groups?includeUsageStatistics=true&fields=_all_&pageNumber='
endpoint_views = '/views?includeUsageStatistics=true&fields=_all_&pageNumber='



new_base_get = f'{base_url}{api}sites/{site_id}'


def get_rest(new_base_get,endpoint,current_page,pagination_url):
    all_data = []
    #this allows you to initialize the variables returned by the function to use seperately.
    page_number, page_size, total_available = get_page_diff_endpoint(pagination_url)
    current_page = page_number

    while total_available >= page_size*current_page:
        get = requests.get(new_base_get+endpoint+str(current_page),headers=headers_get).json()
        all_data.append(get)
        print(new_base_get+endpoint+str(current_page))
        current_page +=1
    return all_data

r1 = get_rest(new_base_get,endpoint_groups,1,url_for_groups)
r2 = get_rest(new_base_get,endpoint_projects,1,url_for_projects)
r3 = get_rest(new_base_get,endpoint_workbooks,1,url_for_workbooks)
r4 = get_rest(new_base_get,endpoint_views,1,url_for_views)

# All data for groups endpoint

data_groups = []
for sublist in r1:
    data_groups.append(pd.json_normalize(sublist['groups']['group']))

df_groups = pd.concat(data_groups,ignore_index=True)

print(df_groups)

# All data for projects endpoint

data_projects = []
for sublist in r2:
    data_projects.append(pd.json_normalize(sublist['projects']['project']))

df_projects = pd.concat(data_projects,ignore_index=True)

print(df_projects)

# All data for workbooks endpoint

data_workbooks = []
for sublist in r3:
    data_workbooks.append(pd.json_normalize(sublist['workbooks']['workbook']))

df_workbook = pd.concat(data_workbooks,ignore_index=True)

print(df_workbook)

# All data for views endpoint

data_views = []
for sublist in r4:
    data_views.append(pd.json_normalize(sublist['views']['view']))

df_views = pd.concat(data_views,ignore_index=True)

df_projects['permissions'] = df_projects['id'].apply(lambda x: f'{new_base_get}/projects/{x}/permissions')

projects_permission_url = df_projects['permissions'].to_list()


project_permissions_download = []
for download in projects_permission_url:
    stuff = requests.get(download, headers=headers_get).json()

    data = stuff['permissions']
    project_id = data['project']['id']

    # Check if 'granteeCapabilities' exists and is a list with at least one item
    #.get('group') used as some group id's are empty this handles such occasions.
    if 'granteeCapabilities' in data and data['granteeCapabilities']:
        group_id = data['granteeCapabilities'][0].get('group')
    else:
        group_id = None

    # Only append if project_id is not None
    if project_id:
        ids = {
            'id': project_id,
            'group_id': group_id if group_id is not None else 'N/A'  # Use 'N/A' if group_id is None
        }
        project_permissions_download.append(ids)

print(project_permissions_download)