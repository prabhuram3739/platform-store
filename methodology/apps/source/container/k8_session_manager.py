import getpass
import json
import logging
import os
import pathlib
import platform
import re
import shutil
import tempfile
import time

import requests
import urllib3
from errors import CreateSessionError, DeleteSessionError, HarborError, CtorError, ContainerError
from kubernetes import client, config
from shell import run

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


CONFIG_DIR = '/nfs/site/disks/ssg_stc_simics_scratch/ssm_methodology/sources/methodology/container'
PATH_CONFIG = pathlib.Path('/nfs/site/disks/ssg_stc_simics_scratch/ssm_methodology/sources/methodology/container')
#PATH_KUBECTL = pathlib.Path('/nfs/site/disks/ssg_stc_simics_scratch/ssm_methodology/tools/kubernetes/stable/kubectl')
PATH_KUBECTL = pathlib.Path('/home/sachinsk/kubectl')

if platform.system() == 'Windows':
    __path_server = pathlib.Path('//pdxsmb.pdx.intel.com/samba')
    PATH_CONFIG = __path_server / PATH_CONFIG
    PATH_KUBECTL = __path_server / PATH_KUBECTL.with_suffix('.exe')

class K8SessionManager:
    ''' Singleton class that interacts with the CaaS cluster and the Harbor store for docker images
    This class uses Kubernetes API, kubectl tool and Harbour API
    Responsibilities:
        - List, create, delete session as per user options in K8 cluster
        - list available oses from Harbor
    '''

    __instance = None

    def __init__(self):
        if K8SessionManager.__instance is not None:
            raise CtorError("K8SessionManager is a singleton!")

        self._prepare()
        self._user = getpass.getuser()
        config.load_kube_config()
        self._api = client.CoreV1Api()
        path_resources = pathlib.Path(__file__).parent.parent.parent / 'resources'
        path_templates = path_resources / 'templates'
        filename = 'launch-service.yaml.template'
        self.path_template = path_templates / 'devtools' / filename
        dirname = os.path.dirname(__file__)
        path_root = os.path.join(dirname, '../../')
        path_templates = os.path.join(path_root, 'resources/templates')
        self._path_template = os.path.join(path_templates, f'devtools/{filename}')
        self._namespace = 'simics'
        self._docker_repo_url = "https://amr-registry.caas.intel.com/api/repositories?project_id=147&q=sas-ssm"
        K8SessionManager.__instance = self
        self._set_env()

    @staticmethod
    def getInstance():
        if K8SessionManager.__instance is None:
            K8SessionManager()

        return K8SessionManager.__instance

    def _prepare(self):
        path_home = pathlib.Path.home()
        path_kubeconfig = path_home / '.kube' / 'config'
        path_kubeconfig.parent.mkdir(exist_ok=True, parents=True)
        if not path_kubeconfig.exists():
            shutil.copy(PATH_CONFIG / 'kube.config', path_kubeconfig)
        if platform.system() == 'Windows':
            path_kubectl = path_home / 'bin' / PATH_KUBECTL.name
            path_kubectl.parent.mkdir(exist_ok=True, parents=True)
            if not path_kubectl.exists():
                shutil.copy(PATH_KUBECTL, path_kubectl)
        else:
            path_kubectl = PATH_KUBECTL

        self.path_kubectl = path_kubectl

    def _set_env(self):
        os.environ['http_proxy'] = 'http://proxy-chain.intel.com:911'
        os.environ['https_proxy'] = 'http://proxy-chain.intel.com:911'
        os.environ['no_proxy'] = 'intel.com,.intel.com,localhost,127.0.0.1,10.0.0.0/8'  # ,192.168.0.0/16,172.16.0.0/12'
        command = f'{self.path_kubectl} config set-context --current --namespace={self._namespace}'
        run(command, capture_outputs=True)

    def _get_new_session_name(self, session_type):
        user_sessions = self._get_user_sessions(session_type)
        next_session_number = 1
        if user_sessions:
            session_numbers = [session.split('-')[2] for session in user_sessions]
            if session_numbers:
                next_session_number = int(max(session_numbers)) + 1

        next_session_name = f'{self._user}-{session_type}-{next_session_number}'
        return next_session_name

    def _get_user_sessions(self, session_type):
        # TODO: this returns None, none
        # cmd = f'{self.path_kubectl} get pods --no-headers -o custom-columns=":metadata.labels.app"'
        cmd = f'{self.path_kubectl} get pods -o=name'
        returncode, stdout, _ = run(cmd, None, capture_outputs=True)
        if returncode:
            raise ConnectionError(f'Failed to get sessions for {self._user}')

        pattern = f"{self._user}-{session_type}-[0-9]+"
        all_sessions = [i.split('/')[1] for i in stdout.split()]
        user_sessions = ['-'.join(session.split('-')[:3]) for session in all_sessions if re.match(pattern, session)]

        return user_sessions

    def _get_pod_info(self):
        command = f'{self.path_kubectl} get pods -o json'
        returncode, stdout, stderr = run(command, capture_outputs=True)

        if returncode:
            raise CreateSessionError(
                f'Failed to get pods info: {stderr}. Please contact ssm.methodology@intel.com'
            )

        data = json.loads(stdout)
        pod_info = {}
        for item in data['items']:
            pod_name = item['metadata']['name']
            dep_name = "-".join(item['metadata']['name'].split("-")[0:3])
            image = item['spec']['containers'][0]['image']
            pod_info[dep_name] = {'os_image': image.split("/")[-1], 'pod_name': pod_name}

        return pod_info

    def _get_user_info(self):
        if platform.system() == 'Windows':
            user_info = ''
        else:
            returncode, stdout, _ = run('id -a', None, capture_outputs=True)
            if returncode:
                raise errors.ContainerError('cannot fetch user information')
            user_info = stdout
        return user_info

    def generate_config(self, session_type, platform_name, simics_version, version, host_os):
        data = self.path_template.read_text()
        session_name = self._get_new_session_name(session_type) # TODO: add platform data to name or label
        path_sandbox = '/tmp/sandbox'
        if session_type == 'simulation':
            command = f"xterm -e 'mkdir -p {path_sandbox}; cd {path_sandbox}; flc launch {platform_name} --path project_{platform_name}; bash'"
        elif session_type == 'interactive':
            command = f"xterm -e 'mkdir -p {path_sandbox}; cd {path_sandbox}; flc co vp; cd vp; bash'"

        data = data.replace('<SIM_CMD>', command)\
                   .replace('<POD_NAME>', session_name)\
                   .replace('<OS_IMAGE>', host_os)\
                   .replace('<NAMESPACE>', self._namespace)\
                   .replace('<USER_INFO>', self._get_user_info()) \

        path_config = pathlib.Path.cwd() / f'{session_name}.yaml'
        path_config.write_text(data)

        return session_name, path_config
        
    def create_session(self, session_type, platform, simics_version, version, host_os, user=None):
        if user is not None:
            self._user = user
            print(f'Create Session setting user to {self._user}')
        session_name, path_config = self.generate_config(session_type, platform, simics_version, version, host_os)
        command = f'{self.path_kubectl} apply -f {path_config}'
        returncode, stdout, stderr = run(command, capture_outputs=True)
        path_config.unlink()
        if returncode:
            message = f'kubectl apply failed with {returncode}:'
            message = f'{message}\nSTDOUT:{stdout}\nSTDERR:{stderr}'
            raise errors.ContainerError(message)

        time.sleep(3)
        # check if the pod deployment was successful
        dep_info = self._verify_deployment(session_name)
        if not dep_info:
            self.delete_session(session_name=session_name, session_type=session_type)
            raise CreateSessionError(
                f'Failed to create session {session_name}. Please contact ssm.methodology@intel.com'
            )
        session_name = dep_info['metadata']['labels']['app']
        ip = json.loads(dep_info['metadata']['annotations']['field.cattle.io/publicEndpoints'])[0]['addresses'][0]
        vnc_port = json.loads(dep_info['metadata']['annotations']['field.cattle.io/publicEndpoints'])[0]['port']
        ip_port = f'{ip}:{vnc_port}'
        created = dep_info['metadata']['creationTimestamp']

        return session_name, ip_port, created

    def _verify_deployment(self, session_name):
        cmd = f'{self.path_kubectl} get deployment {session_name} -o json'
        while True:
            returncode, stdout, stderr = run(cmd, None, capture_outputs=True)
            if returncode:
                logging.error(stderr)
                return None

            dep_info = json.loads(stdout)
            status = dep_info.get('status')
            if status.get('readyReplicas', 0) == 1:
                return dep_info


    def _get_deployment_info(self, session_type):
        cmd = f'{self.path_kubectl} get deployment -o json'
        returncode, stdout, _ = run(cmd, None, capture_outputs=True)
        if returncode:
            raise ContainerError(
                f'Failed to get deployment info for user {self._user}. Please contact ssm.methodology@intel.com'
            )

        dep_info = json.loads(stdout)
        if not len(dep_info):
            return None

        session_info = list()
        session_name_pat = f'^{self._user}-{session_type}-[0-9]+'
        regex = re.compile(f'^{self._user}-{session_type}-[0-9]+')
        for dep in dep_info['items']:
            session_name = dep['metadata']['labels']['app']
            if not regex.match(session_name):
                continue
            endpoints = dep['metadata']['annotations']['field.cattle.io/publicEndpoints']
            endpoints = json.loads(endpoints)
            endpoint = endpoints[0]
            address = endpoint.get('addresses')[0]
            port = endpoint.get('port')
            address_full = f'{address}:{port}'
            created = dep['metadata']['creationTimestamp']
            session_info.append([session_name, address_full, created])

        return session_info

    def is_valid_os(self, OS):
        return OS in [o_s for o_s in self.get_oses()[1]]

    def _is_valid_session(self, session_name, session_type):
        return session_name in [session[0] for session in self._get_deployment_info(session_type)]

    def delete_session(self, session_type=None, session_name=None, user=None):
        if user is not None:
            self._user = user
            print(f'Delete Session setting user to {self._user}')

        if not self._is_valid_session(session_name, session_type):
            raise DeleteSessionError(f'No such session {session_name}')

        for kind in ['service', 'deployment']:
            cmd = f"{self.path_kubectl} get {kind} {session_name} -o yaml"
            returncode, stdout, _ = run(cmd, None, capture_outputs=True)
            if returncode:
                raise DeleteSessionError(f'Failed to delete session {session_name}. Please contact ssm.methodology@intel.com')

            tempyaml = tempfile.NamedTemporaryFile(mode="w",
                                                   prefix=f'{session_name}.{kind}_',
                                                   suffix=".yaml",
                                                   delete=False)
            tempyaml.write(stdout)
            tempyaml.close()
            cmd = f'{self.path_kubectl} delete -f {tempyaml.name}'
            returncode, stdout, _ = run(cmd, None, capture_outputs=True)
            if returncode:
                raise DeleteSessionError(f'Failed to delete session {session_name}. Please contact ssm.methodology@intel.com')
            tempyaml.delete
            logging.debug(f"Deleted {kind} for {session_name}")

    def get_oses(self):
        r = requests.get(self._docker_repo_url, verify=False, timeout=60)

        if r.status_code == 200:
            headers = ["Host OS"]
            data = [entry['name'].split("/")[2] for entry in json.loads(r.content)]
            return headers, data

        raise HarborError(f'Unable to fetch OS information from {self._docker_repo_url}. Please contact ssm.methodology@intel.com')

    def list_sessions(self, session_type, user=None):
        if user is not None:
            self._user = user
            print(f'List Session setting user to {self._user}')
        dep_info = self._get_deployment_info(session_type)
        headers, data = None, None
        if dep_info:
            pod_info = self._get_pod_info()  # TODO: what if this is empty?!
            data = []
            headers = ["Session Name", "Host OS", "VNC Address", "Created Date"]
            for session_name, ip_port, created in dep_info:
                if session_name in pod_info.keys():
                    data.append([session_name, pod_info[session_name]['os_image'], ip_port, created])
        else:
            logging.info(f'No sessions created for {self._user}')

        return headers, data

