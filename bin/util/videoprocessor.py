import cv2
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
import skimage.morphology as skmorph
import skimage.segmentation as skseg
import skimage.measure as skmeas
import skimage.filters as skfilt
import skimage.color as skcolor
import skimage.feature as skfeat
import subprocess

class VideoProcessor(object):
    def __init__(self, workspace_name):
        self.workspace_name = workspace_name
        with open('../workspaces/{}/config.json'.format(self.workspace_name), 'r') as fp:
            self.config_params = json.load(fp)
        fp.close()

    @staticmethod
    def extract_blobs(frame):
        img = np.asarray(frame, dtype=float)[:,:,0]*(1/255)
        img = abs(1-img)
        img = img > skfilt.threshold_otsu(img)
        img = skmorph.opening(img, skmorph.square(8))
        img = skseg.clear_border(skmorph.remove_small_objects(img))
        img = skmeas.label(img)
        return img
    
    def region_extraction(self, image):
        regions = skmeas.regionprops(image, cache=False)
        lower_bound = self.config_params['min_single_size']
        upper_bound = self.config_params['max_single_size']
        if not lower_bound or not upper_bound:
            raise ValueError('please check your config file for this workspace for single size bounds')
        singles = []
        for region in regions:
            region_size = region.area
            if (region_size > lower_bound) and (region_size < upper_bound):
                singles.append(region)
        return singles 
        
    def process_video(self):
        cap = cv2.VideoCapture('../workspaces/{}/cropped_video.mp4'.format(self.workspace_name))
        if not cap.isOpened():
            raise ValueError('unable to open video, check workspace name')
        
        frame_data = []
        frame_count = 1
        while(cap.isOpened()):
            ret, frame = cap.read()
            if not ret:
                break
            print('processing frame {:04d} of {:04d} : {:2.2f}%'.format(
                frame_count, self.config_params['frame_count'], 100*frame_count/self.config_params['frame_count'])
                , end='\r')
            frame_count += 1

            # preprocessing
            img = self.extract_blobs(frame)

            # region extraction
            singles = self.region_extraction(img)
            single_data = []
            for single in singles:
                centroid = tuple([int(np.round(single.centroid[i])) for i in range(2)])
                single_data.append(tuple((centroid, single.bbox)))
            
            frame_data.append(single_data)
        print('')
        print('writing frame data ...', end='')
        self.write_frame_data(frame_data)
        print('done.')
    
    def write_frame_data(self, frame_data):
        with open('../workspaces/{}/frame_data.pkl'.format(self.workspace_name), mode='wb') as fp:
            pickle.dump(frame_data, fp)
        fp.close()