- Build Docker Container
```shell
#Traverse to the folder which contains the Dockerfile. Run below command:

docker build -t amr-registry.caas.intel.com/simics-vp-registry/sas-ssm/<OS-NAME>:<VERSION> .

#Ex:
docker build -t amr-registry.caas.intel.com/simics-vp-registry/sas-ssm/sles12sp5:2.5.3 .
```

- Convert Docker to a Singularity Container Image
```shell
singularity build <OS-NAME>:<VERSION>.sif docker-daemon://amr-registry.caas.intel.com/simics-vp-registry/sas-ssm/<OS-NAME>:<VERSION>

Ex:
singularity build sles12sp5.2.5.3.sif docker-daemon://amr-registry.caas.intel.com/simics-vp-registry/sas-ssm/sles12sp5:2.5.3

```

- Push Docker Container Image to Intel Harbor Registry
```shell
#One Time pre-requisite authentication to Harbor with below command:
docker login amr-registry.caas.intel.com

docker push amr-registry.caas.intel.com/simics-vp-registry/sas-ssm/<OS-NAME>:<VERSION>

#Ex:
docker push amr-registry.caas.intel.com/simics-vp-registry/sas-ssm/sles12sp5:2.5.3
```

- Copy Singularity Container to SC NFS
```shell
rsync -arh --progress <OS-NAME>:<VERSION>.sif sccj001387a.sc.intel.com:/nfs/site/disks/container_images_tmp/containers/singularity/<OS-NAME>/

#Remote copy from host your are building to SC site path "/nfs/site/disks/container_images_tmp/containers/singularity/<OS-NAME>"

rsync -arh --progress <OS-NAME>:<VERSION>.sif sccj001387a.sc.intel.com:/nfs/site/disks/container_images_tmp/containers/singularity/sles12sp5/
```
