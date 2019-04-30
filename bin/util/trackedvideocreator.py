import ast
import cv2
import json
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
import subprocess

class TrackedVideoCreator(object):
    def __init__(self, workspace_name):
        self.workspace_name = workspace_name
        with open('../workspaces/{}/config.json'.format(self.workspace_name), 'r') as fp:
            self.config_params = json.load(fp)
        fp.close()

    def create_video(self):
        ''' loads location data and for each frame plots location. saves each individual frame.
        '''
        location_data = self.load_location_data()
        video_path = '../workspaces/{}/cropped_video.mp4'.format(self.workspace_name)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError('unable to open video, check workspace name')
        
        for ii in range(len(location_data)):
            ret, frame = cap.read()
            if not ret:
                raise IndexError('frame count doesnt match data -- bad news here')
            self.plot_locations(frame, location_data[ii], ii)
        
        self.write_video()

    def load_location_data(self):
        ''' loads location data from pkl file
        '''
        with open('../workspaces/{}/frame_data.pkl'.format(self.workspace_name), mode='rb') as fp:
            data = pickle.load(fp)
        fp.close()
        return data
    
    def plot_locations(self, frame, location_data, frame_id):
        ''' plots the bounding boxes and centers on each bee. lots of indexing here. 
        gotta trust a bit. took a while to work out...
        '''
        rectangles = []
        circles = []
        for loc in location_data:
            x,y = loc[0]
            circle = patches.Circle((y,x), radius=10, facecolor='red')
            circles.append(circle)
            min_row, min_col = loc[1][0], loc[1][1]
            height, width = loc[1][2] - min_row, loc[1][3] - min_col
            rect = patches.Rectangle((min_col, min_row),width,height,linewidth=1,edgecolor='lime',facecolor='none')
            rectangles.append(rect)
        f, ax = plt.subplots(figsize=(10,10))
        ax.imshow(frame)
        for circle in circles:
            ax.add_patch(circle)
        for rectangle in rectangles:
            ax.add_patch(rectangle)
        save_path = '../workspaces/{}/marked_frames'.format(self.workspace_name)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        plt.savefig(os.path.join(save_path, 'frame{:04d}.png'.format(frame_id)))

    def write_video(self):
        ''' calls fffmpeg to turn the set of frames into a video. 
        '''
        subprocess.call(['ffmpeg',
                         '-y',
                         '-i',
                         '../workspaces/{}/marked_frames/frame%04d.png'.format(self.workspace_name),
                         '-vcodec',
                         'mpeg4', 
                         '../workspaces/{}/marked_video.mp4'.format(self.workspace_name)])
