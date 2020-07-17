#su - vsiddara
cd /tmp/
git clone ssh://git@gitlab.devtools.intel.com:29418/simics/vp/vp.git
cd vp
git lfs install
git lfs pull
cd tbh
python ../_tools/set_workspace.py -60
gmake -j16 pkg-7397
