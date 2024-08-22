import requests

class credentials:

    def __init__(self,PATName,PATSecret,site,base_url):
        self.PATName = PATName
        self.PATSecret = PATSecret
        self.site = site
        self.base_url = base_url

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

        return r
    

stuff = credentials('PATName','PATSecret','site','base_url')

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