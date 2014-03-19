# Copyright 2009-2014 Eucalyptus Systems, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
# Please contact Eucalyptus Systems, Inc., 6755 Hollister Ave., Goleta
# CA 93117, USA or visit http://www.eucalyptus.com/licenses/ if you need
# additional information or have any questions.

import worker.config as config
import os
import worker.floppy

def write_certificate(cert_file, cert_pem):
    if not os.path.exists(cert_file):
        f_cert = open(cert_file, 'w')
        f_cert.write(cert_pem)
        f_cert.close()
        os.chmod(cert_file, 400)

def download_server_certificate(cert_arn, cert_file, pubkey_included=False):
    if os.path.exists(cert_file):
        return
    f = FloppyCredential() 
    host = config.get_clc_host()
    access_key_id = config.get_access_key_id()
    secret_access_key = config.get_secret_access_key()
    security_token = config.get_security_token()
    con = worker.ws.connect_euare(host_name=host, aws_access_key_id = access_key_id, aws_secret_access_key=secret_access_key, security_token=security_token)
    cert= con.download_server_certificate(f.get_instance_pub_key(), f.get_instance_pk(), f.get_iam_pub_key(), f.get_iam_token(), cert_arn)
    if pubkey_included:
        cert_pem = '%s\n%s' % (cert.get_certificate(), cert_get_private_key())
    else:
        cert_pem = cert.get_private_key()
    write_certificate(cert_file, cert_pem) 
