# CSC5201-Final_Project

## Site Access
Site can be accessed at this url: https://white-hill-0b99d2510.3.azurestaticapps.net/index.html

## High Level Architecture Diagram
![High Level Diagram](image.png)


## Site Usage Instructions
The site allows users to login and upload pdf documents to translate into different languages.
The current languages supported are:
   - English
   - Spanish
   - French
   - Chinese (Simplified)

To get started, create an account via the signup page and login.
Uploaded documents are stored for future access.

Select a pdf file and language to translate and click upload, you will recieve a notification once you file has been uploaded.
It may take some time for the ML processor to ingest the file and translate it but once it is done it will appear in the 'View Uploaded Document'
section.

## Deployment Procedure
Front end is automatically deployed via github webhooks.

To update docker container apps. Run deploy.sh
**Note: You must have access to the Azure Workspace in order to push up changes the container apps**