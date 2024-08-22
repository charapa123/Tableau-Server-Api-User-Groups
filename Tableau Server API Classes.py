from Credentials_Module import *


# creating our dataframes and removing where we have no groups specified
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


#Views join to workbooks on workbook id
df_part_1 = pd.merge(df_views,df_workbook,'inner',right_on=['Workbook_id','project.id'],left_on=['workbook.id','project.id'])
#join our workbooks/views to projects on project id,some workbooks are not in projects so union these workbooks back on to our main data stream
df_part_2 = pd.merge(df_part_1,df_projects,'outer',left_on='project.id',right_on='project_id')
#Transpose, our group id's for views,workbooks,projects this is because not all project groups will have access to all workbooks in the project so they won't join.
df_part_3 = pd.melt(df_part_2,id_vars=['view_name','project_name','Workbook_name','project_id'])
#Join our id field from groups to the id's from our transposed group id's this is so we can bring in the names of the groups.
df_Final = pd.merge(df_groups,df_part_3,'outer',left_on='id',right_on='value')







