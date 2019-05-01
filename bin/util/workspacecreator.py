import cv2
import json
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np
import os 
import skimage.measure as skmeas
import subprocess
import util.videoprocessor as videoprocessor

class WorkSpaceCreator(object):
    def __init__(self, video_path, workspace_name):
        self.config_params = {}
        self.demo_frame = None
        self.video_path = video_path
        self.workspace_name = workspace_name
        
    def count_frames(self):
        ''' counts rame in video and sets as config param. this is usually a couple frames
        off. not sure why. 
        '''
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError('unable to open video, please check file path')
        
        frame_count = 1
        ret, _ = cap.read()
        while ret:
            frame_count += 1
            ret, _ = cap.read()
        self.config_params['frame_count'] = frame_count

    def create_directory(self):
        '''  creates the new workspaces directory
        '''
        dir_path = os.path.join('../workspaces', self.workspace_name)
        if os.path.exists(dir_path):
            raise ValueError('a workspace with this name already exists.'
                             ' please try a unique name')
        os.makedirs(dir_path)
    
    def create_workspace(self):
        ''' runs entire flow
        '''
        self.create_directory()
        self.get_crop_points()
        self.crop_video()
        self.get_singles_sizes()
        self.count_frames()
        self.write_config_file()

    def crop_video(self):
        ''' uses crop points to call ffmpeg to run cropping.
        '''
        out_w = self.config_params['bottom_right'][1] - self.config_params['top_left'][1]
        out_h = self.config_params['bottom_right'][0] - self.config_params['top_left'][0]
        y, x = self.config_params['top_left']
        subprocess.call(['ffmpeg',
                         '-y',
                         '-i',
                         self.video_path,
                         '-filter:v',
                         'crop={}:{}:{}:{}'.format(out_w, out_h, x, y), 
                         '../workspaces/{}/cropped_video.mp4'.format(self.workspace_name)])
    
    def get_crop_points(self):
        ''' collects crop points using roi and saves them to config params.
        '''
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError('unable to open video, please check file path')
        
        _ret, frame = cap.read()
        
        region = cv2.selectROI(frame)
        cv2.destroyAllWindows()
        self.config_params['top_left'] = (int(region[1]), int(region[0]))
        self.config_params['bottom_right'] = (int(region[1]+region[3]), int(region[0]+region[2]))
        self.demo_frame = frame[int(region[1]):int(region[1]+region[3]), 
                                int(region[0]):int(region[0]+region[2]), :]
            
    
    def get_singles_sizes(self):
        ''' displays histogram of region sizes and asks for min and max from user/
        '''
        # runs preprocessing to extract blobs
        img = videoprocessor.VideoProcessor.extract_blobs(self.demo_frame)
        regions = skmeas.regionprops(img, cache=False)
        regions.sort(key= lambda x : x.area)
        region_sizes = [region.area for region in regions if region.area < 10000]
        f, ax = plt.subplots(figsize=(20,20))
        ax.tick_params(axis='x', rotation=90)
        plt.hist(region_sizes, bins=100)
        plt.xticks(np.arange(0,region_sizes[-1], 150))
        plt.savefig('../workspaces/{}/object_sizes.png'.format(self.workspace_name))
        plt.show()

        min_single_size = int(input('min single size: '))
        max_single_size = int(input('max single size: '))

        self.config_params['min_single_size'] = min_single_size
        self.config_params['max_single_size'] = max_single_size

    def write_config_file(self):
        ''' writes config file to workspace directory.
        '''
        with open('../workspaces/{}/config.json'.format(self.workspace_name), 'w') as write_file:
            json.dump(self.config_params, write_file, indent=4)
        write_file.close()
    