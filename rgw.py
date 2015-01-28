#!/usr/bin/env python
import os
import requests
from awsauth import S3Auth
from collections import namedtuple
import six.moves.urllib.parse as urlparse


class RGWAdminClient(object):
    def __init__(self, endpoint, access_key, secret_key):
        self.access_key = access_key
        self.secret = secret_key
        self.endpoint = endpoint
        self.hostname = urlparse.urlparse(endpoint).netloc

    def get_bucket(self, tenant_id):
        METHOD = "bucket"
        uri = "{0}/{1}".format(self.endpoint, METHOD)
        r = requests.get(uri, params={"uid": tenant_id, "stats": True},
                         auth=S3Auth(self.access_key, self.secret,
                                     self.hostname)
                         )
        stats = self._process_bucket_stats(r.json(), tenant_id)
        return stats

    def get_usage(self, tenant_id):
        METHOD = "usage"
        r = requests.get("{0}/{1}".format(self.endpoint, METHOD),
                         params={"uid": tenant_id},
                         auth=S3Auth(self.access_key, self.secret,
                                     self.hostname)
                         )
        return self._process_usage_stats(r.json())

    @staticmethod
    def _process_bucket_stats(json_data, tenant_id):
        stats = {'num_buckets': 0, 'buckets': [], 'size': 0, 'num_objects': 0}
        Bucket = namedtuple('Bucket', 'name, num_objects, size')
        stats['num_buckets'] = len(json_data)
        for it in json_data:
            for k, v in it["usage"].items():
                stats['num_objects'] += v["num_objects"]
                stats['size'] += v["size_kb"]
                stats['buckets'].append(Bucket(it["bucket"], v["num_objects"],
                                               v["size_kb"]))

        return stats

    @staticmethod
    def _process_usage_stats(json_data):
        usage_data = json_data["summary"]
        return sum((it["total"]["successful_ops"] for it in usage_data))


if __name__ == "__main__":
    akey = os.getenv('S3_ACCESS_KEY_ID')
    skey = os.getenv('S3_SECRET_ACCESS_KEY')
    s3host = 'http://127.0.0.1:8080/admin'

    admin = RGWAdminClient(s3host, akey, skey, secure=False)
    stats = admin.get_bucket("admin")
    import pprint
    pp = pprint.PrettyPrinter()

    pp.pprint(stats)
    pp.pprint(stats['buckets'])
    pp.pprint(admin.get_usage("admin"))
