# Web Application Setup

# SSM Infrastructure Web App developer's instructions
Run the following commands:
- Create virtual environment outside of source tree if have not done yet
```shell
python3.7.4 -m venv venv
```
- Activate virtual environment if have not done yet
```shell
# Bash
source venv/bin/activate
# CSH
source venv/bin/activate.csh
# CMD
venv\Scripts\activate
```
- Change directory to `web`
```shell
cd /path/to/sources/methodology/web
```
- Install Python dependencies
```shell
pip install -r resources/requirements/webapp.txt
```

# Web App backend developer's instructions
The structure of the backend directory that hosts the Flask application is as follows.
```buildoutcfg
web
  backend
     static
     templates
  server.py
```
In our setup the Flask server doubles up as the web server as well.
The static directory contains the css, js, img etc files that are to be served by the application.
All files under static/ will be served by Flask.
The templates directory will contain all the .html files and will be rendered via the Flask API responses.
More information on serving static files: https://stackabuse.com/serving-static-files-with-flask/
The Flask servers main file is the server.py.
This can be executed by running 
```
python server.py
OR
set FLASK_APP=server.py
flask run
```

To get details of the group to which the IAM authenticates against check 
https://adsadm.intel.com/search.aspx
In here search for the group, e.g. ssdv and then click on Properties Viewer after selecting the group from the result.
The field 'Distinguished Name:' is the group we check with IAMWS

Notes on IAMWS:
  - https://soco.intel.com/groups/iam-ws/blog/2017/10/13/how-to-get-a-bearer-token-from-the-iam-ws-token-endpoint#comment-202394750
  - https://soco.intel.com/groups/iam-ws/blog/2017/12/26/how-to-do-internal-single-sign-on-with-iam-ws
  - The url 'https://iamws-i.intel.com/api/v1/token' works only on domains that have .intel.com 
    This is a production url
  - For dev purpose (for e.g while hosting the app from localhost) use the dev url
    https://iamws-icd.intel.com/api/v1/token
  - All POST requests required a Proxy to be set even though proxy was set in the environment
  - IAMWS first authenticates our apps url and returns a user token that is valid for 10s
  - Then the users identity and memberships are retreived
  - The above process is effected via callbacks to a different endpoint in the app.
  - <TODO: list the actual workflow> 
    - service account and its AGS permissions and its password
    - IAMWS endpoints for getting bearer tokens and user authorization and memberships
    - callback implementation using app endpoints.
  
   
For more information on how to run a Flask app please see: https://opensource.com/article/18/4/flask
# Testing the backend
<TBD>

# Web App frontend developer's instructions
- This section sets up the Angular dev environment.  
  - <NODE
  - Several of the below steps are taken from the below links
  - https://itdz.intel.com/#/content/itdz$markdown-content$intro-angular-sails$tool-install.md#general-software-installs 
  - In above link go to https://itdz.intel.com/#/content/itdz$markdown-content$intro-angular-sails$tool-install.md#app-generator
  - The following details have been picked up from email titled "IP Store - look and feel & security/user access" 
    - Intel guide for mastering look and feel - https://mlaf.intel.com/getting-started/introduction
    - Download page: https://pixi-ui.apps1-fm-int.icloud.intel.com/#/pixi-detail/it-mlaf-sass-bs4
    - Intel Icon Fonts: https://soco.intel.com/servlet/JiveServlet/download/2385209-17-906820/intelicon-2.7.zip
    - Intel Assets: https://digitallibrary.intel.com/content/digital-library/us/en/homepage.html
    - Simics Assets: https://gitlab.devtools.intel.com/simics-open/digital-library
    - Application security: https://wiki.ith.intel.com/display/public/ASC/Application+Registration+and+Setup    

- The below step initializes the src directory where the Angular source will reside 
```shell
cd frontend\hawk-web\src
npm init
```
- The below steps downloads the dependent packages into the node_modules directory 
`methodology\web\frontend\hawk-web\node_modules`
``` shell
sudo n  10.13
cd ..
npm set proxy http://proxy-chain.intel.com:911
npm set https-proxy http://proxy-chain.intel.com:911
npm set registry https://pixi.intel.com/
npm install -g intc
npm install -g intc --registry https://pixi.intel.com/ # DID NOT WORK
npm install angular OR 
npm install -g @angular/cli
npm install -g bower
npm install -g gulp-cli
```
- Go to https://github.com/dlmanning/gulp-sass and follow instructions here.
```shell
npm install node-sass gulp-sass --save-dev
```

- Go to https://mlaf.intel.com/getting-started/introduction. 
  The main steps are listed below 
  - Option1
```shell
npm install it-mlaf-sass-bs4 --save --registry https://pixi.intel.com
```
  - Option2: instead of main.scss save it as style.scss
```shell
Option2 : instead of main.scss we have created style.scss
```
  - Option3: Install additional dependencies
```shell
npm install bootstrap@4.x jquery@3.x popper.js@1.x --save
```

Now the Angular application is setup and dependencies are installed

# Testing the frontend
<TBD>

# Web App release instructions
To release the frontend/hawk-web code it has to be built 
and the contents of the resulting dist/ directory should be copied into backend/static as shown below 
To build the frontend code for distribution
```shell
cd methodology\web\frontend\hawk-web\
ng build --prod --output-path ../../backend/static --watch --output-hashing none 
cp dist/index.html backend/templates

Update src=/static/ along with the existing path reference in the index.html for the CSS and the JS file reference
update src=/static/a alogn with the existing path referene in the main.js
dont update the assets directory inside the static directory of the backend which contains the css and the images directory

```