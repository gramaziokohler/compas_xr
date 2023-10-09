import pyrebase
import json
import os

# Get the current file path
current_file_path = os.path.abspath(__file__)
print ("CURRENT FILE PATH = " + current_file_path)

# Define the number of levels to navigate up
levels_to_go_up = 3

#Construct File path to the correct location
parent_folder = os.path.abspath(os.path.join(current_file_path, "../" * levels_to_go_up))

# Enter another folder
target_folder = os.path.join(parent_folder, "scripts")
print ("TARGET FOLDER PATH = " + target_folder)

#JSON file path
config_path = os.path.join(target_folder, "firebase_config.json")

# Load the firebase configuration file from the JSON file if it exists: Else: Print.
if os.path.exists(config_path):
    with open(config_path) as config_file:
        print (config_path)
        config = json.load(config_file)

# initialize the connection to firebase
firebase = pyrebase.initialize_app(config)

# reference to firebase storage
storage = firebase.storage()


def upload_to_firebase(path_on_cloud, path_local):
    storage.child(path_on_cloud).put(path_local)


def download_from_firebase(path_on_cloud, path_local):
    filename = path_local
    storage.child(path_on_cloud).download(path_local, filename)


# if __name__ == "__main__":

#     # download_from_firebase(path_on_cloud, path_local)
#     print(path_local)
#     upload_to_firebase(path_on_cloud, path_local)
