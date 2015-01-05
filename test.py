import os
import requests
import json
from awsauth import S3Auth


akey = os.getenv('S3_ACCESS_KEY_ID')
skey = os.getenv('S3_SECRET_ACCESS_KEY')
s3host = os.getenv('S3_HOSTNAME')


methods_allowed = ["user", "usage", "bucket"]

for method in methods_allowed:
    uri = "http://{host}/admin/{method}?uid=admin".format(host=s3host,
                                                          method=method,)
    r = requests.get(uri, auth=S3Auth(akey, skey, s3host))
    print json.dumps(r.json(), indent=2)
