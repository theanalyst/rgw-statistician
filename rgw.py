#!/usr/bin/env python
from __future__ import print_function

import os
import pprint
import requests
import argparse

from awsauth import S3Auth
from collections import namedtuple

import six.moves.urllib.parse as urlparse


class RGWAdminClient(object):
    def __init__(self, host, access_key, secret_key):
        self.access_key = access_key
        self.secret = secret_key
        self.endpoint = host + "/admin"
        self.hostname = urlparse.urlparse(host).netloc

    def get_method(self, method, params):
        uri = "{0}/{1}".format(self.endpoint, method)
        r = requests.get(uri, params=params,
                         auth=S3Auth(self.access_key, self.secret, self.hostname))
        return r.json()

    def get_user(self, user_id):
        params={"uid":user_id}
        # TODO: redact keys from output
        return self.get_method("user", params)

    def get_bucket(self, user_id, bucket):
        params={"uid": user_id, "stats": True}
        if bucket is not None:
            params["bucket"]=bucket
        return self.get_method("bucket", params)

    def get_usage(self, user_id):
        params={"uid": user_id}
        return self.get_method("usage", params)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='get rgw statistics using a RESTful api')
    parser.add_argument('--uid', type=str, help='rgw user id for the user')
    parser.add_argument('--bucket', type=str, help='bucket/container to get statistics from')
    parser.add_argument('--s3host', type=str, help='rgw url',
                        default = os.getenv('S3_HOSTNAME'))
    parser.add_argument('--access', type=str,
                        help='rgw access key (defaults to $S3_ACCESS_KEY)',
                        default = os.getenv('S3_ACCESS_KEY_ID'))
    parser.add_argument('--secret', type=str,
                        help='rgw secret key (defaults to $S3_SECRET_KEY)',
                        default = os.getenv('S3_SECRET_ACCESS_KEY'))


    args = parser.parse_args()

    admin = RGWAdminClient(args.s3host, args.access, args.secret)

    pp = pprint.PrettyPrinter()
    print("user")
    pp.pprint(admin.get_user(args.uid))

    print("\nbucket stats")
    pp.pprint(admin.get_bucket(args.uid, args.bucket))
