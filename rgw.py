import os
import requests
from awsauth import S3Auth
from collections import namedtuple


class RGWStats(object):
    def __init__(self, user_id):
        """
        Container holding some stats per user
        """
        self.uid = user_id
        self._api_requests = 0
        self._num_buckets = 0
        self._num_objects = 0
        self._buckets = []
        self._size = 0


def iter_bucket_stats(bucket_json):
    Bucket = namedtuple('Bucket', 'name, num_objects, size')
    for it in bucket_json:
        for k, v in it["usage"].items():
            yield Bucket(it["bucket"], v["num_objects"], v["size_kb"])
        else:
            yield Bucket(it["bucket"], 0, 0)


class RGWAdminOp(object):
    def __init__(self, host, access_key, secret, secure=True):
        """
        Basic class holding the admin details
        """
        self.access_key = access_key
        self.secret = secret
        self.host = host
        self.protocol = "https" if secure else "http"
        self.endpoint = "{0}://{1}/admin".format(self.protocol, host)

    def get_bucket_stats(self, tenant_id):
        METHOD = "bucket"
        r = requests.get("{0}/{1}".format(self.endpoint, METHOD),
                         params={"uid": tenant_id, "stats": True},
                         auth=S3Auth(self.access_key, self.secret, self.host)
                         )

        stats = RGWStats(tenant_id)
        stats.buckets = [b for b in self.iter_bucket_stats(r.json())]
        return stats

    def get_usage_stats(self, tenant_id):
        METHOD = "usage"
        r = requests.get("{0}/{1}".format(self.endpoint, METHOD),
                         params={"uid": tenant_id},
                         auth=S3Auth(self.access_key, self.secret, self.host)
                         )
        return list(self.iter_usage_stats(r.json()))

    @staticmethod
    def iter_bucket_stats(json_data):
        # TODO: handle failures
        Bucket = namedtuple('Bucket', 'name, num_objects, size')
        for it in json_data:
            for k, v in it["usage"].items():
                yield Bucket(it["bucket"], v["num_objects"], v["size_kb"])
            else:
                yield Bucket(it["bucket"], 0, 0)

    def iter_usage_stats(user_data):
        Usage = namedtuple('Usage', 'api, s_bytes, r_bytes, ops, success_ops')
        usage_data = user_data["summary"][0]["categories"]
        for it in usage_data:
            yield Usage(it["category"], it["bytes_sent"], it["bytes_received"],
                        it["ops"], it["successful_ops"])


if __name__ == "__main__":
    akey = os.getenv('S3_ACCESS_KEY_ID')
    skey = os.getenv('S3_SECRET_ACCESS_KEY')
    s3host = os.getenv('S3_HOSTNAME')

    admin = RGWAdminOp(s3host, akey, skey, secure=False)
    stats = admin.get_bucket_stats("admin")
    print stats.buckets
    admin.get_usage_stats("admin")
