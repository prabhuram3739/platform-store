import os
import sys
import subprocess
import shlex
import argparse
import re
import urllib
from urllib.request import urlopen
import base64

parser = argparse.ArgumentParser()
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument("--simics-ver", required=True, help="")
requiredNamed.add_argument("--platform", required=True, help="")
requiredNamed.add_argument("--release-ver", required=True, help="")

gBaseUrl = 'https://ubit-artifactory-or.intel.com/artifactory/simics-repos/vp-release'
SimicsScratch = '/nfs/site/disks/ssg_stc_simics_scratch/ssm_methodology/sources/methodology/container'
gSimicsInstaller = '%s/simics-installer-0.6.4/linux/simics-installer-cli' % SimicsScratch
download_dir = 'download'
install_dir  = 'install'
project_dir  = 'project'

gPlatformInfo = {'tigerlake' : {'short_name': 'tgl', 
                                    'run' : 'targets/x86-tgl/tgl-a0.simics'
                                  },
                    'alderlake' : {'short_name':'adl',
                                    'run' : 'targets/adl/adl-s.simics'
                                  }
                   }

def get_base_dir(simics_ver, platform):
    return 'simics-%s-%s' % (gPlatformInfo[platform]['short_name'], simics_ver)
    
def add_on(simics_ver):
    print ("cwd is ", os.getcwd())
    os.chdir(install_dir)
    installed_dirs = os.listdir('.')
    print (installed_dirs)
    simics_basedir = get_simics_base_dir(simics_ver, installed_dirs)
    for installed_dir in installed_dirs:
        if installed_dir == simics_basedir: continue    
        if re.match('^simics-.*?$', installed_dir):
            cmd = '%s/bin/addon-manager -b -s %s' % (simics_basedir, 
                                                    installed_dir)
            print (cmd)
            os.system(cmd)
            
    cmd = "%s/bin/simics -v" % simics_basedir
    os.system(cmd)
    os.chdir("../")

def get_simics_base_dir(simics_ver, installed_dirs):
    for d in installed_dirs:
        print (d)
        if re.match("simics-%s.[0-9]+$" % (simics_ver), d):
            return d
    
def get_platform_base_dir(simics_ver, platform):
    installed_dirs = os.listdir(install_dir)
    short_name = gPlatformInfo[platform]['short_name']
    pat = 'simics-%s-%s.pre[0-9]+$' % (short_name, simics_ver)
    for d in installed_dirs:
        if re.match(pat, d):
            return d

def create_project(simics_ver, platform):
    installed_dirs = os.listdir(install_dir)
    simics_basedir = get_simics_base_dir(simics_ver, installed_dirs)
    platform_basedir = get_platform_base_dir(simics_ver, platform)
    print ("Simics Base Directory is ", simics_basedir) 
    print ("Platform Base Directory is ", platform_basedir)

    if not os.path.isdir(project_dir):
        os.mkdir(project_dir)

    os.chdir(project_dir)
    proj_setup = '../%s/%s/bin/project-setup' % (install_dir, 
								                 simics_basedir)

    print ("Running : ", proj_setup)
    os.system(proj_setup)

    cmd = 'bin/simics -v'
    print ("Running :", cmd)
    os.system(cmd)
    os.system("tree targets/")
    os.chdir('../') 

def run_target(platform):
    os.chdir(project_dir)
    cmd = 'bin/simics %s -e "run"' % gPlatformInfo[platform]['run']
    print  ("Running ", cmd)
    os.system(cmd)
    
def download(simics_ver, platform, release):
    if os.path.isdir(install_dir):
        os.system("rm -rf %s/*" % install_dir)
    else:
        os.mkdir(install_dir)
        
    cmd = gSimicsInstaller
    cmd += ' --package-repo %s/%s/%s/%s ' % (gBaseUrl, simics_ver, platform, release)
    cmd += ' --install-all --non-interactive'
    cmd += ' --install-dir %s' % install_dir    
    if not os.path.isdir(install_dir):
        os.mkdir(install_dir)
    print (cmd)
    os.system(cmd)
        
args = parser.parse_args()

def main():
    simics_ver = args.simics_ver
    platform = args.platform
    release = args.release_ver
	
    download(simics_ver, platform, release)
    add_on(simics_ver)
    create_project(simics_ver, platform)
    run_target(platform)

if __name__ == '__main__':
	main()

#how to run
#python3.7.4 simulation.py --simics-ver 6.0 --platform tigerlake --release-ver Silver/2020ww24.4
#python3.7.4 simulation.py --simics-ver 6.0 --platform alderlake --release-ver Silver/2020ww25.3

'''
cd myws
cd ../simics-install/simics-6.0.38/bin/project-setup
./simics --version
./bin/addon-manager -s ../simics-install/simics-tgl-6.-pre133

'''
