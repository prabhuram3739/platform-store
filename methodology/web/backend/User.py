#!/usr/bin/env python3
#
# INTEL CONFIDENTIAL
# Copyright (c) 2017, Intel Corporation.
#
# The source code contained or described herein and all documents related to
# the source code("SIMICSaaS") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material contains trade secrets and proprietary
# and confidential information of Intel or its suppliers and licensors. The
# Material is protected by worldwide copyright and trade secret laws and treaty
# provisions. No part of the Material may be used, copied, reproduced,
# modified, published, uploaded, posted, transmitted, distributed, or disclosed
# in any way without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be
# express and approved by Intel in writing.
#
# File: User.py
#
# Description:
#
# Author:       Jerry C. Wang - jerry.c.wang@intel.com

# TODO: windows and Centos install of ldap is having issues
#import ldap
from werkzeug.security import check_password_hash, generate_password_hash

LDAP_SERVER = "ldap://corpad.intel.com:3268"

class User():
    def __init__(self, username, group='user', max_tbox=1, servers=[]):
        self.username = username
        self.group = group
        self.max_tbox = max_tbox
        self.servers = servers

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def get_group(self):
        return self.group

    def get_servers(self):
        return self.servers

    def get_max_tbox(self):
        return self.max_tbox

    @staticmethod
    def validate_login_ldap(username, region, password):
        return True
        '''
        userPrincipalName = "{}@{}.corp.intel.com".format(username, region)
        try:
            l = ldap.initialize(LDAP_SERVER)
            l.simple_bind_s(userPrincipalName, password)
            return True
        except ldap.INVALID_CREDENTIALS:
            return False
        '''

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)
