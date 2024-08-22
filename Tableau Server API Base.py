import pandas as pd
import requests

base_url = 'url'
auth = 'auth/signin'
site = '<>'
api = 'api/3.11/'

PATName = 'Token'
PATSecret = '<>'

url = base_url+api+auth

#print(url)


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

url_for_get_request = f'{base_url}{api}sites/{site_id}/groups?includeUsageStatistics=true&fields=_all_'

headers_get = {
    'Accept': 'application/json',
    'X-Tableau-Auth' : token
}

r_get = requests.get(url_for_get_request,headers=headers_get).json()

print(r_get)

page_number = r_get['pagination']['pageNumber']
page_size = r_get['pagination']['pageSize']
total_available = r_get['pagination']['totalAvailable']

print(page_number)
print(page_size)
print(total_available)

print(pd.json_normalize(r_get['pagination'])) 