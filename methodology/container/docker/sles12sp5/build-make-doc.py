import os, sys
os.environ["label"] = "6.0_lnx64"
os.environ['JOB_NAME'] = "tbh-6.0_build"
os.environ["JENKINS_SHARED_DIR"] = "/nfs/site/disks/ssg_stc_simics_jen_build_tmp"
sys.path.append("../_tools")
from jenkins_python_shell import *
build_documentation([7397])
