import cv2
import json
import matplotlib.pyplot as plt
import os 
import skimage.measure as skmeas
import subprocess
import util.videoprocessor as videoprocessor

class WorkSpaceCreator(object):
    def __init__(self, video_path, workspace_name):
        self.video_path = video_path
        self.workspace_name = workspace_name
        self.config_params = {}
        self.demo_frame = None
    
    def create_directory(self):
        dir_path = os.path.join('../workspaces', self.workspace_name)
        if os.path.exists(dir_path):
            raise ValueError('a workspace with this name already exists.'
                             ' please try a unique name')
        os.makedirs(dir_path)
    
    def get_crop_points(self):
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError('unable to open video, please check file path')
        
        ret, frame = cap.read()
        
        satisifed_with_crop = False
        while not satisifed_with_crop:
            f, ax = plt.subplots(figsize=(20,20))
            ax.imshow(frame)
            plt.show()

            top_left_row = int(input('top left row: '))
            top_left_col = int(input('top left col: '))
            bottom_right_row = int(input('bottom right row: '))
            bottom_right_col = int(input('bottom right col: '))

            f, ax = plt.subplots(figsize=(20,20))
            ax.imshow(frame[top_left_row:bottom_right_row, top_left_col:bottom_right_col, :])
            plt.show()

            satisifed = input('satisfied with crop y/n: ')
            if satisifed == 'y':
                satisifed_with_crop = True
        self.config_params['top_left'] = (top_left_row, top_left_col)
        self.config_params['bottom_right'] = (bottom_right_row, bottom_right_col)
        self.demo_frame = frame[top_left_row:bottom_right_row, top_left_col:bottom_right_col, :]
            
    def crop_video(self):
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
    
    def get_singles_sizes(self):
        img = videoprocessor.VideoProcessor.extract_blobs(self.demo_frame)
        regions = skmeas.regionprops(img, cache=False)
        regions.sort(key= lambda x : x.area)
        region_sizes = [region.area for region in regions if region.area < 10000]
        plt.hist(region_sizes, bins=100)
        plt.show()

        min_single_size = int(input('min single size: '))
        max_single_size = int(input('max single size: '))

        self.config_params['min_single_size'] = min_single_size
        self.config_params['max_single_size'] = max_single_size
    
    def count_frames(self):
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError('unable to open video, please check file path')
        
        frame_count = 1
        ret, _frame = cap.read()
        while ret:
            frame_count += 1
            ret, frame = cap.read()
        self.config_params['frame_count'] = frame_count

    def write_config_file(self):
        with open('../workspaces/{}/config.json'.format(self.workspace_name), 'w') as write_file:
            json.dump(self.config_params, write_file, indent=4)
        write_file.close()
        