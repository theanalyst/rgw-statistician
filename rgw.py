import requests
from awsauth import S3Auth
from collections import namedtuple


class RGWStats(object):
    def __init__(self, user_id):
        """
        Container holding some stats per user
        """
        self.api_requests = 0
        self.num_buckets = 0
        self.num_objects = 0
        self.uid = user_id
        self.buckets = []


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

    @staticmethod
    def iter_bucket_stats(json_data):
        # TODO: handle failures
        Bucket = namedtuple('Bucket', 'name, num_objects, size')
        for it in json_data:
            for k, v in it["usage"].items():
                yield Bucket(it["bucket"], v["num_objects"], v["size_kb"])
            else:
                yield Bucket(it["bucket"], 0, 0)
