# Tableau Server Api User Groups
 API call to see which users access

There are 3 Scripts 

Tableau Server Base was used for parsing out the API
Tableau Server API Classes is now used as the part to see group access to objects on Tableau Server
Credentials_Module is used as a module for our Credentials class allowing more flexibility for your own projects

This code allows you to interact with the Tableau Server API

There are 4 main functions in the Credentials Class

Setup:
This function uses a post request to initialize our session getting a site_id and Token

chosen_endpoint:
This retrieves all the data for your chosen endpoint, in this code an endpoint is defined as workbooks,views,projects and groups as the rest of the structure is the same.

permissions:
This gives you all the permissions data for chosen endpoint and needs the setup and chosen_endpoint function to run first.

permissions_group:
This function gives us all the groups that have access to all objects in our chosen endpoint and needs setup,chosen_endpoint,permissions functions to run first.

The main goal of this script is to see which groups have access to workbooks,views and projects but has been setup in this way to be able to interact with the Tableau Server API at which ever stage you desire.
