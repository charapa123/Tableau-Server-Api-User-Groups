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
        <site contentUrl={site} />
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

url_for_get_request = f'{base_url}{api}sites/{site_id}/workbooks?includeUsageStatistics=true&fields=_all_'
page_text = '&pageNumber='

headers_get = {
    'Accept': 'application/json',
    'X-Tableau-Auth' : token
}

r_get = requests.get(url_for_get_request,headers=headers_get).json()

# print(r_get)

page_number = int(r_get['pagination']['pageNumber'])
page_size = int(r_get['pagination']['pageSize'])
total_available = int(r_get['pagination']['totalAvailable'])

endpoint = '/workbooks?includeUsageStatistics=true&fields=_all_&pageNumber='
#url check
URL = requests.get(f'{base_url}/api/3.11/sites/9f1ee58e-b27c-4144-acb8-492c0c74cbab/workbooks?includeUsageStatistics=true&fields=_all_&pageNumber=2',headers=headers_get).json()


# def get_rest(url_for_get_request,page_text,current_page):

new_base_get = f'{base_url}{api}sites/{site_id}'

all_data = []
current_page = page_number

while total_available >= page_size*current_page:
    get = requests.get(new_base_get+endpoint+str(current_page),headers=headers_get).json()
    all_data.append(get)
    print(new_base_get+endpoint+str(current_page))
    current_page +=1
print(all_data)

print(total_available)
print(current_page)

# print(get_rest(url_for_get_request,page_text,page_number))

# all = []
# while page_number < 10:
#     all.append(page_number)
#     page_number +=1

# print(all)