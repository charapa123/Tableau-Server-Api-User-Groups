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
page_text = '&pageNumber='

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
#this allows you to initialize the variables returned by the function to use seperately.
page_number, page_size, total_available = get_page_diff_endpoint(url_for_projects)

print(page_number)

# endpoint_workbooks = '/workbooks?includeUsageStatistics=true&fields=_all_&pageNumber='
# endpoint_projects = '/groups?includeUsageStatistics=true&fields=_all_&pageNumber='


# URL = requests.get(f'{base_url}/api/3.11/sites/9f1ee58e-b27c-4144-acb8-492c0c74cbab/workbooks?includeUsageStatistics=true&fields=_all_&pageNumber=2',headers=headers_get).json()


# # def get_rest(url_for_get_request,page_text,current_page):

# new_base_get = f'{base_url}{api}sites/{site_id}'


# def get_rest(new_base_get,endpoint,current_page):
#     all_data = []
#     current_page = page_number

#     while total_available >= page_size*current_page:
#         get = requests.get(new_base_get+endpoint+str(current_page),headers=headers_get).json()
#         all_data.append(get)
#         print(new_base_get+endpoint+str(current_page))
#         current_page +=1
#     return all_data

# print(get_rest(new_base_get,endpoint_projects,page_number))