import pyrebase
import json

config_path = "scripts\firebase_config.json"

with open(config_path) as config_file:
    config = json.load(config_file)

    
path_on_cloud = "test_assembly_withoutgeometry.json"  # path to download/upload from/to cloud
# localpath to store files
path_local = r"C:\Users\eleni\Documents\GitHub\cdf_unity\data\test_assembly_withoutgeometry.json"

# initialize the connection to firebase
firebase = pyrebase.initialize_app(config)

# reference to firebase storage
storage = firebase.storage()


def upload_to_firebase(path_on_cloud, path_local):
    storage.child(path_on_cloud).put(path_local)


def download_from_firebase(path_on_cloud, path_local):
    filename = path_local
    storage.child(path_on_cloud).download(path_local, filename)


if __name__ == "__main__":

    # download_from_firebase(path_on_cloud, path_local)
    print(path_local)
    upload_to_firebase(path_on_cloud, path_local)
