import requests
import pandas as pd

#We first need to log in to our tableau server using the '/auth/signin' endpoint of the API
#* Note
#Token expires after 6 months download workflow and replace Token with one you have created

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
        #We make the relevant xml in a formula tool as a field and send it as the payload with the download tool
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
        r = requests.post(url,body,headers=headers,verify=r'C:\Users\PavlouC\Downloads\prod-uk-a.online.tableau.crt').json()

        token = r['credentials']['token']
        site_id = r['credentials']['site']['id']
        estimatedTimeToExpiration = r['credentials']['estimatedTimeToExpiration']
        #If we've signed in, we get a connection token to use with future calls along with a site-id from the reponses (more xml). We rename the token 'X-Tableau-Auth'

        headers_get = {
    'Accept': 'application/json',
    'X-Tableau-Auth' : token
}
        return estimatedTimeToExpiration
    
    def chosen_endpoint(self):
        global chosen_endpoint_data
        global new_base_get
        global df_endpoint
        #We can attach this token as a header (along with Accept: application/json) and go to a different endpoint to get information about views,Workbooks,Groups,Projects on our Tableau Server
        #this is the endpoint to get pagination details
        endpoint_url = f'{self.base_url}{api}sites/{site_id}/{self.endpoint}?includeUsageStatistics=true&fields=_all_'


        r = requests.get(endpoint_url,headers=headers_get,verify=r'C:\Users\PavlouC\Downloads\prod-uk-a.online.tableau.crt').json()
        page_number = int(r['pagination']['pageNumber'])
        page_size = int(r['pagination']['pageSize'])
        total_available = int(r['pagination']['totalAvailable'])

        new_base_get = f'{self.base_url}{api}sites/{site_id}'


        chosen_endpoint_data = []
        current_page = page_number
        #downloading all data available 
        while total_available >= page_size*len(chosen_endpoint_data):
            get = requests.get(new_base_get+'/'+self.endpoint+'?includeUsageStatistics=true&fields=_all_&pageNumber='+str(current_page),headers=headers_get,verify=r'C:\Users\PavlouC\Downloads\prod-uk-a.online.tableau.crt').json()
            chosen_endpoint_data.append(get)
            print(new_base_get+'/'+self.endpoint+'?includeUsageStatistics=true&fields=_all_&pageNumber='+str(current_page))
            current_page +=1 
            #parsing out as we are only interested in our endpoint response
            chosen_endpoint_clean_data = []
            for sublist in chosen_endpoint_data:
                chosen_endpoint_clean_data.append(pd.json_normalize(sublist[f'{self.endpoint}'][f"{self.endpoint.rstrip('s')}"]))

        df_endpoint = pd.concat(chosen_endpoint_clean_data, ignore_index=True)

        return df_endpoint
    
    def permissions(self):
        global permissions_json
        #chosen_endpoint function downloads the initial data which provides us with an Id which can then be used in a second download to query permissions
        #Second download for permissions, need to get original fields to create permission URL and use id field from initial download. header Accept: application/json as XML is more inconsistent.
        df_endpoint['permissions'] = df_endpoint['id'].apply(lambda x: f'{new_base_get}/{self.endpoint}/{x}/permissions')

        endpoint_permission_url = df_endpoint['permissions'].to_list()

        # Initialize stuff as a list to store multiple permissions data
        permissions_json = []
        for download in endpoint_permission_url:
            permissions_data = requests.get(download, headers=headers_get,verify=r'C:\Users\PavlouC\Downloads\prod-uk-a.online.tableau.crt').json()
            permissions_json.append(permissions_data)



        return permissions_json

    def permissions_group(self):
        # Parse out Json keeping the chosen endpoint id for each row so it can be joined back onto chosen endpoint function output and getting all permissions from granteeCapabilities list
        # checking permissions is there for every downloaded endpoint
        endpoint_permissions_download = []
        for data_item in permissions_json:
            permissions = data_item.get('permissions', {})
            grantee_capabilities = permissions.get('granteeCapabilities', [])
            for item in grantee_capabilities:
                item[f"{self.endpoint.rstrip('s')}"] = permissions.get(f"{self.endpoint.rstrip('s')}", {}).get('id', 'Unknown')
                endpoint_permissions_download.append(item)
        # getting data into a dataframe
        df = pd.json_normalize(endpoint_permissions_download)
        # Row number added so this can be joined to the parsed out capabilities column (this df keeps the chosen endpoint ids to join back to chosen_endpoint data), this is due to the chosen endpoint id and other columns dropping when you json normalise a certain column
        df['Row_Number'] = range(1, len(df) + 1)
        # parsing out capabilities.capability column to columns as some will have read and write permissions enabled or more depending on endpoint
        df_normalized = pd.json_normalize(df['capabilities.capability'])
        # adding a row number to join back to df as the granularity changes after pivot
        df_normalized['Row_Number'] = range(1, len(df) + 1)
        # pivoting to get all columns from the split out capabilities column into 1 column reataining the row number
        df_melt = df_normalized.melt(id_vars=['Row_Number'],
                var_name="name",
                value_name="mode")
        # removing blank rows
        df_melt =  df_melt[df_melt['mode'].notna()]
        # adding a row number so we can join the normalised mode data back onto df_melt
        df_melt['Row_Number1'] = range(1, len(df_melt) + 1)
        # splits the mode (name and value) to columns 
        df_mode_normalized = pd.json_normalize(df_melt['mode'])
        # adds a row number to join back to df_melt
        df_mode_normalized['Row_Number'] = range(1, len(df_mode_normalized) + 1)

        # this section is joining each dataframe to the one before to make sure granularity is correct and each id has the correct parsed out permissions

        df_normal = pd.merge(df_mode_normalized,df_melt,'outer', right_on='Row_Number1', left_on='Row_Number')

        df_normal = df_normal[['name_x','mode_x','Row_Number_y']]

        df_final = pd.merge(df,df_normal,'outer',left_on='Row_Number',right_on='Row_Number_y')

        df_final = df_final[[f"{self.endpoint.rstrip('s')}",'group.id','name_x','mode_x']].rename(columns={"name_x":"capabilities","mode_x":"mode"})

        df_permissions_final = pd.merge(df_final,df_endpoint,'inner',left_on=f"{self.endpoint.rstrip('s')}",right_on='id')

        return df_permissions_final
