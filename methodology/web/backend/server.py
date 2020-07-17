import logging.handlers
from collections import namedtuple

import requests
from LoginForm import LoginForm
from User import User
from flask import (Flask, render_template, request, redirect, session, flash, url_for)
from flask_cors import CORS
from flask_login import LoginManager
from flask_login import login_required, login_user, logout_user, current_user
from requests.auth import HTTPBasicAuth

from container import K8SessionManager

logger = logging.getLogger("main_logger")
logger.setLevel(logging.INFO)

GRP_SSDV = 'CN=ssdv,OU=Groups,OU=Accounts,OU=Russian Research and Development,OU=Customer Labs,OU=Engineering Computing,OU=Resources,DC=ccr,DC=corp,DC=intel,DC=com'

# When we get a domain name .intel.com for he webapp use this 'https://iamws-i.intel.com'
BASE_IAMWS_URL       = 'https://iamws-icd.intel.com'
USER_MEMBERSHIPS_URL = f'{BASE_IAMWS_URL}/api/v1/Authorizations'
USER_DATA_URL        = f'{BASE_IAMWS_URL}/api/v1/windows/auth'
SSO_AUTH_URL         = f'{BASE_IAMWS_URL}/api/v1/windows/auth'
TOKEN_URL            = f'{BASE_IAMWS_URL}/api/v1/token'
FACELESS_USER        = 'sys_vpsaas'
FACELESS_PASS        = 'Simicsaas@2020200514'

proxies = {'http': 'http://proxy-chain.intel.com:911',
           'https': 'http://proxy-chain.intel.com:912'
           }

app = Flask(__name__)
app.secret_key = 'Methodology@SSM061079'

# Initiate Login Manager
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
CORS(app)

@lm.user_loader
def load_user(user_id):
    # get the user specs from DB. OR can we get it from IAMWS again? But it will be very slow.
    # this information is required by Flask
    return User(user_id, 'ssdv')

@app.route("/", methods=['GET', 'POST'])
#@login_required
def home():
    message = f'Hello {current_user.get_id()}, from hawk-web!'
    print (message)
    return render_template('index.html', userid=current_user.get_id())

@app.route("/userdata", methods=['GET', 'POST'])
def listUserData():
    r = {'userid': current_user.get_id()}
    return r

def _get_access_token(scope='Token_WindowsAuth'):
    #auth_url = 'https://iamws-icd.intel.com/api/v1/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = ('scope=' + scope + '&grant_type=client_credentials')
    logging.info("Posting to ", TOKEN_URL, 'payload: ', payload)

    response = requests.post(
        TOKEN_URL,
        auth=HTTPBasicAuth(FACELESS_USER, FACELESS_PASS),
        headers=headers,
        data=payload,
        verify=False,
        proxies=proxies)
    response_obj = response.json()
    Result = namedtuple('Result', ['access_token', 'expires_in'])
    result = Result(response_obj['access_token'], response_obj['expires_in'])
    return result


def _get_user_data(access_token, user_token):
    print ("Getting USER DATA")
    headers={
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = ('token=' + user_token)
    response = requests.post(
        USER_DATA_URL,
        headers=headers,
        data=payload,
        verify=False,
        proxies=proxies)
    user_data = response.json()['IntelUserExtension']
    logging.info("USER DATA: ", user_data)
    print ("USER DATA:" , user_data)
    return user_data

def _get_user_membership(access_token, user_data):
    print ("GET USER MEMBERSHIP")
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    payload = {
        "enterpriseId": user_data['id'],
        'memberships': [],
        'schemas': ['urn:scim:schemas:extension:intelauthorization:1.0']
    }
    payload['memberships'].append({'name': GRP_SSDV , 'type': "CORPAD"})
    response = requests.post(
        USER_MEMBERSHIPS_URL,
        headers=headers,
        json=payload,
        verify=False,
        proxies=proxies)

    logging.info("MEMBERSHIP: ", response.json())
    print("MEMBERSHIP: ", response.json())
    groups = []
    for entry in response.json()['memberships']:
        print ("CHECKING ENTRY ", entry)
        if entry['isMember']:
            groups.append(entry['name'])
    return groups

@app.route('/sso_login')
def sso_login():
    try:
        user_token = request.args.get('token')
    except:
        return redirect(url_for("login"))

    if user_token == None:
        print("Error: user_token is expected for login")
        return redirect(url_for("login"))

    try:
        authentication_result = _get_access_token('Token_WindowsAuth')
        authentication_access_token = authentication_result.access_token
        user_data = _get_user_data(authentication_access_token, user_token)
    except:
        logging.error("Unable to get USER DATA")
        return redirect(url_for("login"))

    try:
        membership_result = _get_access_token('Token_WindowsAuth User_Read Authorization')
        membership_access_token = membership_result.access_token
        print("Membership acces token:", membership_access_token)
        user_membership = _get_user_membership(membership_access_token, user_data)
    except:
        logging.error("Unable to get USER MEMBERSHIP")
        return redirect(url_for("login"))

    print ("USER MEMBERSHIPS:", user_membership)
    if GRP_SSDV not in user_membership:
        error_msg = "Please Apply for group 'ssdv' in AGS!"
        form = LoginForm()
        return render_template('login.html', title='login', form=form, error_msg=error_msg)

    session['userInfo'] = {'userName': user_data['userName'],
                           'displayName': user_data['displayName'],
                           'id': user_data['id'],
                           'externalId': user_data['externalId'],
                           'email': user_data["emails"][0]["value"]
                           }
    logging.info(session['userInfo'])

    if session['userInfo']['userName']:
        user_info = session['userInfo']['userName'].split("\\")
        region = user_info[0]
        username = user_info[1]

        # section to add user to database is deleted
        # TODO: looks like some DB will be needed to return user information to Flask login/logout plugins

        user_obj = User(username)
        login_user(user_obj) # Flask function
        flash("Logged in successfully!", category='success')
        print ("Logged in successfully!")
        return redirect(url_for("home"))
    else:
        error_msg = "Cannot get valid username info from Authorization server!"
        form = LoginForm()
        return render_template('login.html', title='login', form=form, error_msg=error_msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    error_msg = ""
    if request.method == 'POST':
        sso_url = url_for('sso_login', _external=True)
        #print(sso_url)
        #windows_auth_url = 'https://iamws-i.intel.com/api/v1/windows/auth'
        redirect_url = SSO_AUTH_URL + '?redirecturl=' + sso_url
        print(redirect_url)
        return redirect(redirect_url)
    return render_template('login.html', title='login', form=form, error_msg=error_msg)

@app.route('/logout')
#@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/projects/')
#@login_required
def projects():
    return 'The project page'

def _list_platforms():
    print("Returning static list of platforms")
    return {'s10-soc': ['2020.ww24.5.0', '2020.ww24.5.1', '2020.ww25.0.0', '2020.ww25.3.0', '2020.ww26.1.0',
                        '2020.ww26.1.1', '2020.ww26.1.2', '2020.ww26.1.3', '2020.ww26.1.4', '2020.ww26.1.5',
                        '2020.ww26.1.6', '2020.ww26.1.7', '2020.ww26.3.0'],
            'tigerlake': ['2020.ww25.3.0'],
            'willard': ['2020.ww24.5.0', '2020.ww24.5.1', '2020.ww24.5.2', '2020.ww24.5.3', '2020.ww24.5.4',
                        '2020.ww24.5.5', '2020.ww24.5.6', '2020.ww24.5.7', '2020.ww24.5.8', '2020.ww25.0.0',
                        '2020.ww25.1.0', '2020.ww25.1.1', '2020.ww25.1.2', '2020.ww25.2.0', '2020.ww25.3.0',
                        '2020.ww25.3.1', '2020.ww25.3.2', '2020.ww25.3.3', '2020.ww25.3.4', '2020.ww25.4.0',
                        '2020.ww25.4.1', '2020.ww25.5.0', '2020.ww25.5.1', '2020.ww26.1.0', '2020.ww26.1.1',
                        '2020.ww26.1.10', '2020.ww26.1.2', '2020.ww26.1.3', '2020.ww26.1.4', '2020.ww26.1.5',
                        '2020.ww26.1.6', '2020.ww26.1.7', '2020.ww26.1.8', '2020.ww26.1.9', '2020.ww26.2.0',
                        '2020.ww26.2.1', '2020.ww26.2.10', '2020.ww26.2.11', '2020.ww26.2.12', '2020.ww26.2.2',
                        '2020.ww26.2.3', '2020.ww26.2.4', '2020.ww26.2.5', '2020.ww26.2.6', '2020.ww26.2.7',
                        '2020.ww26.2.8', '2020.ww26.2.9', '2020.ww26.3.0', '2020.ww26.3.1', '2020.ww26.3.10',
                        '2020.ww26.3.11', '2020.ww26.3.12', '2020.ww26.3.13', '2020.ww26.3.14', '2020.ww26.3.15',
                        '2020.ww26.3.16', '2020.ww26.3.2', '2020.ww26.3.3', '2020.ww26.3.4', '2020.ww26.3.5',
                        '2020.ww26.3.6', '2020.ww26.3.7', '2020.ww26.3.8', '2020.ww26.3.9', '2020.ww26.4.0',
                        '2020.ww26.4.1']
            }

@app.route('/listplatforms', methods=['GET'])
#@login_required
def list_platforms():
    print ("In list_platforms")
    simics_version = request.args.get('simics_version')
    ret = {}
    status = 'OK'
    ret = _list_platforms()
    '''try:
        release_tree = simics.ReleaseTree()
        platforms = release_tree.get_platform_names()
        print(platforms)
        if platforms:
            for platform in platforms:
                versions = release_tree.get_platform_versions(platform, simics_version)
                print(versions)
                ret[platform] = versions
            status = 'OK'
        else:
            status = 'NOK'
    except Exception as e:
        print ("Exception occured")
        status = 'OK'
        ret = _list_platforms()
    '''

    return {'status': status, 'data': ret}

@app.route('/createsession/', methods=['POST', 'GET'])
#@login_required
def create_session():
    userid = current_user.get_id()
    try:
        service_info = K8SessionManager.getInstance().create_session(
            #session_type=request.args.get('session_type'),
            session_type='simulation',
            platform=request.args.get('platform'),
            simics_version=request.args.get('simics_version'),
            version=request.args.get('version'),
            host_os=request.args.get('host'),
            user=userid
        )
        name, host_port, created = service_info
        headers = ["Session Name", "VNC", "Created Date"]
        print (headers, service_info)
        return {'status': 'ok', 'headers': headers, 'data': [name, host_port, created]}
    except Exception as error:
        return {'status': 'nok', 'data': f'Failed to create session for {userid}.  Please contact ssm.methodology@intel.com'}

@app.route('/deletesession', methods=['DELETE'])
#@login_required
def delete_session():
    userid = current_user.get_id()
    try:
        session_name = request.args.get("session_name")
        session_type = request.args.get("session_type")
        print(f"Will delete {session_name}")
        K8SessionManager.getInstance().delete_session(
            session_type=session_type, session_name=session_name, user=userid)
        return {'status': 'success', 'data': f'Successfully deleted {session_name}'}
    except Exception as error:
        return {'status': 'nok', 'data': f'Failed to delete session for {userid}.  Please contact ssm.methodology@intel.com'}

@app.route('/listsessions', methods=['GET'])
#@login_required
def get_sessions():
    userid = current_user.get_id()
    try:
        (headers, data) = K8SessionManager.getInstance().list_sessions('simulation', user=userid)
        #print(headers, data)
        return {'status': 'ok', 'header': headers, 'data': data}
    except Exception as error:
        return {'status': 'nok', 'data': f'Failed to list session for {userid}.  Please contact ssm.methodology@intel.com'}


@app.route('/hostos', methods=['GET'])
#@login_required
def get_oses():
    try:
        (headers, data) = K8SessionManager.getInstance().get_oses()
        print(headers, data)
        return {'status': 'ok', 'header': headers, 'data': data}
    except:
        return {'status': 'nok', 'data': f'Failed to get Host OS.  Please contact ssm.methodology@intel.com'}

@app.route('/<platform>/versions')
#@login_required
def get_versions(platform):
    versions = ['v1', 'v2']
    return f"{platform} versions are {versions}"

# (venv) C:\Users\sachinsk\Desktop\infra\methodology\web>flask run --host=0.0.0.0
if __name__ == '__main__':
    # frontend/source/hawk-web/src/environments/*.requests
    # change apiURL to current host
    #apiUrl: 'https://localhost:8001'
    app.run(host='0.0.0.0', port=8001, ssl_context='adhoc', debug=True)
    #app.run(debug=True)

# https://soco.intel.com/groups/iam-ws/blog/2017/12/26/how-to-do-internal-single-sign-on-with-iam-ws
# https://code.tutsplus.com/tutorials/flask-authentication-with-ldap--cms-23101
# https://stackabuse.com/serving-static-files-with-flask/
# https://stackoverflow.com/questions/53824239/python-flask-serving-angular-projects-index-html-file
# https://code.tutsplus.com/tutorials/flask-authentication-with-ldap--cms-23101
