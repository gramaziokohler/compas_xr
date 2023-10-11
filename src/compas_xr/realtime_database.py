from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json
import pyrebase


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

else:
    print ("FILE DOES NOT EXIST: " + config_path)

# initialize the connection to firebase
firebase = pyrebase.initialize_app(config)

# reference to firebase database
db = firebase.database()


def stream_handler(message):
    print(message["event"])
    print(message["path"])
    print(message["data"])


def set_json_data(json_f, parentname, keys):
    with open(json_f) as json_file:
        json_data = json.load(json_file)
        children = []
        for key in keys:
            values = json_data[key]
            children.append(values)

    for child, key in zip(children, keys):
        db.child(parentname).child(key).set(child)


def set_json_data_joints(json_f):
    with open(json_f) as json_file:
        json_data = json.load(json_file)

    db.child("Joints").set(json_data)


# def set_qr_frames(json_fr): 
#     with open(json_fr) as json_file:
#         json_data = json.load(json_file)

#     db.child("QRFrames").set(json_data)


def set_qr_frames(data, parent_name): 
  db.child(parent_name).set(data)


def set_data(childname, data): 
  db.child(childname).set(data)

# get keys_built
def get_keys_built():
    keys_built = []
    keys = db.child("Built Keys").get()
    if keys.each():
        for key in keys.each():
            # print("key to built key ", key.key())
            keys_built.append(key.val())
    return keys_built


def set_keys_built(keys):
    data = {}
    for key in keys:
        data[str(key)] = str(key)
    db.child("Built Keys").set(data)


def remove_key_built(key):
    db.child("Built Keys").child(str(key)).remove()

# update data


def add_key_built(new_key_built):
    db.child("Built Keys 2").update({str(new_key_built): str(new_key_built)})


# get users' ids
def get_users():
    users_ids = []
    users = db.child("Users").get()
    for user in users.each():
        print(user.key())
        users_ids.append(user.key())
        # print("Selected Key is ", user.val()["selectedKey"])
        # print("Selected by user Nr.", user.val()["userID"])
    return users_ids


def get_users_attribute(attribute):
    users_attributes = []
    users = db.child("user").get()
    for user in users.each():
        users_attributes.append(user.val()[attribute])
    return users_attributes


def get_json_data(name, childname):
    json_data = {}
    data = db.child(name).child(childname).get()
    if data.each():
        for d in data.each():
            json_data[d.key()] = d.val()
        return json_data
    else:
        dt = db.child(name).child(childname).get().val()
        return dt
    
def get_json_data_qr(name):
    json_data = {}
    data = db.child(name).get()
    if data.each():
        for d in data.each():
            json_data[d.key()] = d.val()
        return json_data
    else:
        dt = db.child(name).get().val()
        return dt


def listen():
    pass
    # my_stream = db.child("Built Keys").stream(stream_handler)

# add a stream_id for multiple streams
# my_stream = db.child("posts").stream(stream_handler, stream_id="new_post")


def close_stream(my_stream):
    my_stream.close()


# if __name__ == "__main__":

#     add_key_built(4)
#     remove_key_built(10)
#     print(get_keys_built())
    # my_stream = db.child("Built Keys").stream(stream_handler)
    # my_stream = db.child("Users").stream(stream_handler)
    # close_stream(my_stream)
    # remove_key_built(17)
