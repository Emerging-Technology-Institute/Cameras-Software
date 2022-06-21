# Functions for the purpose of loading and running models
import os

import cv2
import numpy as np
import pandas as pd
import pymongo


def to_planar(arr: np.ndarray, shape: tuple) -> list:
    return [val for channel in cv2.resize(arr, shape).transpose(2, 0, 1) for y_col in channel for val in y_col]


def frame_norm(frame, bbox):
    normVals = np.full(len(bbox), frame.shape[0])
    normVals[::2] = frame.shape[1]
    return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)


def get_label_map(directory: str):
    d = os.path.realpath(directory)


def det_to_json(db, **kwargs):
    df = pd.DataFrame()
    for i in kwargs['dets']:
        detection = {}
        for feature in kwargs.keys():
            detection[feature] = kwargs[feature]
        row = pd.Series(data=detection)
        row = row.drop('dets')
        df[i] = row
        if kwargs['label'] == 'person':
            with open(f'{os.getcwd()}/vectors/{kwargs["id"]}.json',"w") as outfile:
                outfile.write(row.to_json())
            db['people'].insert_one(row.to_dict())
        if kwargs['label'] == 'vehicle':
            with open(f'{os.getcwd()}/vectors/{kwargs["license"]}.json',"w") as outfile:
                outfile.write(row.to_json())
            db['vehicles'].insert_one(row.to_dict())
    out_json = df.to_json(orient='split')
    with open(f'{os.getcwd()}/{kwargs["camera"]}_{kwargs["time"]}.json', "w") as outfile:
        outfile.write(out_json)

def pull_identities(db, label):
    count = 0
    if label == 'person':
        p_cursor = db.people.find({'label':'person'})
        stored_identities = []
        for det in p_cursor:
            stored_identities.append(det)
            count = count + 1
        return [count,stored_identities]
    elif label == 'vehicle':
        v_cursor = db.vehicles.find({'label':'vehicle'})
        stored_identities = []
        for det in v_cursor:
            stored_identities.append(det)
            count = count + 1
        return [count,stored_identities]

def clear_db(db):
    while True:
        cursor = db.people.find({})
        for data in cursor:
            db.people.delete_one({'_id':data['_id']})

if __name__ =='__main__':
    # client = pymongo.MongoClient('192.168.50.115', 27017)
    client = pymongo.MongoClient('45.79.221.195', 27017)
    db = client['detections']
    clear_db(db)