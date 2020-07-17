# Applications

# SSM Infrastructure Tools developer's instructions
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
- Change directory to `apps`
```shell
cd /path/to/sources/methodology/apps
```
- Install dependnecies
```shell
pip install -r resources/requirements/devtools.txt
```
- Change directory to `source`
```shell
cd source
```
- Install Falcon in development mode
```shell
python admin/setup.py develop
```
- Update shell if `flc` is not available
```shell
rehash
```
- Check help
```shell
flc -h
```
