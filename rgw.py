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

