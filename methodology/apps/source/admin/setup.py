from setuptools import setup


setup(
    name='ssm_tools',
    version='0.0.2',
    description='SSM Methodology Tools',
    author='SSM Methodology',
    author_email='ssm.methodology@intel.com',
    url='https://gitlab.devtools.intel.com/simics/methodology-and-infra/methodology',
    package_dir={'': '.'},
    package_data={'': ['../resources/templates/devtools/config-global.mk.ninja',]},
    data_files=[
        ('', ['../resources/templates/devtools/config-global.mk.ninja',]),
    ],
    packages=[
        'bin',
        'container',
        'eagle',
        'environment',
        'errors',
        'falcon',
        'falcon_flow',
        'shell',
        'simics',
        'source',
        'storage',
    ],
    entry_points={
        'console_scripts': [
            'egl=bin.eagle:main',
            'hwk=bin.hawk:main',
            'flc=bin.falcon:main',
            'flc-mgm=bin.falcon_mgm:main',
            'flc-flow=bin.falcon_flow:main',
        ]
    },
    install_requires=[
        'Jinja2==2.11.2',
        'click==7.1.2',
        'columnar==1.3.1',
        'kubernetes==11.0.0',
        'requests==2.23.0',
    ],
)
