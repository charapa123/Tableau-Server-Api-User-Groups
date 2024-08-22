import requests

class credentials:

    def __init__(self,PATName,PATSecret,site,base_url,endpoint):
        self.PATName = PATName
        self.PATSecret = PATSecret
        self.site = site
        self.base_url = base_url
        self.endpoint = endpoint

    def user(self):
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
    
    

         


    

credentials('PATName', 'PATSecret', 'site', 'base_url','endpoint')


print(stuff.user())






# class anime:

#     def __init__(self,genre,title,year,rating):
#         self.g = genre
#         self.t = title
#         self.y = year
#         self.r = rating

#     def good(self):
#         print(f'{self.t} is good')

#     def bad(self):
#         print(f'{self.g} is bad')


# anime_1 = anime('romance','Fruits Basket',2023,10)

# anime_1.good()

# print(anime_1.t)