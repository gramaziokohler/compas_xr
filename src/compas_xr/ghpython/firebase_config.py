class FirebaseConfig(object):
    def __init__(self, api_key, auth_domain, database_url, storage_bucket):
        self.api_key = api_key
        self.auth_domain = auth_domain
        self.database_url = database_url
        self.storage_bucket = storage_bucket

    def ToString(self):
        return str(self)

    def __str__(self):
        return "FirebaseConfig, api_key={}, auth_domain={}, database_url={}, storage_bucket={}".format(self.api_key, self.auth_domain, self.database_url, self.storage_bucket)

    def __data__(self):
        return {
            "apiKey": self.api_key,
            "authDomain": self.auth_domain,
            "databaseURL": self.database_url,
            "storageBucket": self.storage_bucket,
        }
