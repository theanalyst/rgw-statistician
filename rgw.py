class RGWBucket(object):
    def __init__(self, bucket_name):
        """
        Basic container to hold a bucket data
        """
        self.bucket_name = bucket_name
        self.num_objects = 0
        self.size = 0

    @property
    def size(self):
        return self.size

    @size.setter
    def size(self, value):
        self.size = value

    @property
    def num_objects(self):
        return self.num_objects

    @num_objects.setter
    def num_objects(self, value):
        self.num_objects = value
