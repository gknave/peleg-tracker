import cv2
import util.erosion
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

    def erode_n_clusters(self, clusters):
        ''' estimates number of bees using mean bee size and erodes cluster until that many
        blobs are present. stops eroding once a blob is detached. 
        documentation for regionprops here (https://scikit-image.org/docs/dev/api/skimage.measure.html#skimage.measure.regionprops)

        Returns:
            list of regionprops objects
        
        '''
        eroded_clusters = []
        mean_size = 0.5*(self.config_params['max_single_size'] + self.config_params['min_single_size'])
        for cluster in clusters:
            if cluster.area < self.config_params['max_single_size']:
                continue
            # to avoid catching massive clusters b/c erosion doesn't work on these
            if cluster.area > 20000:
                continue
            number_bees = round(cluster.area/mean_size)
            if number_bees < 2: 
                continue
            image = cluster.image.astype(float)
            cluster_bbox = cluster.bbox
            cont = True
            count = 0
            while cont:
                boundary, dims = util.erosion.findBoundary(image)
                boundary_map = util.erosion.createBoundaryMap(boundary, dims).astype('float')
                # erosion happens here
                image -= boundary_map

                labeled_image = skmeas.label(image)
                
                # no blobs remaining
                if sum(labeled_image.flatten()) == 0:
                    cont = False
                
                # removing the smallest blob from the erosion
                if max(labeled_image.flatten()) != 1:
                    region_props = skmeas.regionprops(labeled_image)
                    region_props.sort(key= lambda x : x.area)
                    # all but smallest
                    for region in region_props[:-1]:
                        eroded_clusters.append((region, cluster_bbox))
                        # this slicing gets complicated. gotta trust a bit here
                        image[region.bbox[0]:region.bbox[2], region.bbox[1]:region.bbox[3]] =\
                             np.zeros((region.bbox[2]-region.bbox[0], region.bbox[3]-region.bbox[1]))
                        count += 1
                        if (count == number_bees-1):
                            cont = False
                            eroded_clusters.append((region_props[-1], cluster_bbox))
                            break
        return eroded_clusters

    @staticmethod
    def extract_blobs(frame):
        ''' extracts blobs from a frame. this is static because it is used in 
        initialization of workspace to get histogram. this is @Gary's preprocessing code.

        Returns:
            labelled image where each island has a different integer value.
        '''
        img = np.asarray(frame, dtype=float)[:,:,0]*(1/255)
        img = abs(1-img)
        img = img > skfilt.threshold_otsu(img)
        img = skmorph.opening(img, skmorph.square(8))
        img = skseg.clear_border(skmorph.remove_small_objects(img))
        return skmeas.label(img)

    def process_video(self):
        ''' for each frame finds blobs and erodes blobs. each frame data written to file.
        '''
        cap = cv2.VideoCapture('../workspaces/{}/cropped_video.mp4'.format(self.workspace_name))
        if not cap.isOpened():
            raise ValueError('unable to open video, check workspace name')
        
        os.makedirs('../workspaces/{}/frame_data'.format(self.workspace_name))
        frame_count = 0
        while(cap.isOpened()):
            frame_data = []
            ret, frame = cap.read()
            if not ret:
                break
            print('processing frame {:04d} of {:04d} : {:2.2f}%'.format(
                frame_count, self.config_params['frame_count'], 100*frame_count/self.config_params['frame_count'])
                , end='\r')

            # preprocessing
            img = self.extract_blobs(frame)

            # region extraction -- single bees
            singles = self.single_region_extraction(img)
            single_data = []
            for single in singles:
                centroid = tuple([int(np.round(single.centroid[i])) for i in range(2)])
                single_data.append(tuple((centroid, single.bbox)))
            
            # region extraction -- more than 1 bee
            regions = skmeas.regionprops(img, cache=False)
            clusters_eroded = self.erode_n_clusters(regions)
            cluster_data = []
            for cluster_set in clusters_eroded:
                cluster_region = cluster_set[0]
                cluster_bbox = cluster_set[1]
                centroid = tuple([int(np.round(cluster_region.centroid[i]+cluster_bbox[i])) for i in range(2)])
                new_bbox = list(cluster_region.bbox)
                new_bbox[0] += cluster_bbox[0]
                new_bbox[1] += cluster_bbox[1]
                new_bbox[2] += cluster_bbox[0]
                new_bbox[3] += cluster_bbox[1]
                cluster_data.append(tuple((centroid, tuple(new_bbox))))
            frame_data.append(single_data+cluster_data)
            self.write_frame_data(frame_data, frame_count)
            frame_count += 1
        print('')
        print('writing frame data ...', end='')
        
        print('done.')
    
    def single_region_extraction(self, image):
        ''' extracts all the single regions based on max and min sizes specified in config params.
        documentation for regionprops here (https://scikit-image.org/docs/dev/api/skimage.measure.html#skimage.measure.regionprops)

        Returns:
            list of regionprops objects
        '''
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
    
    def write_frame_data(self, frame_data, frame_count):
        ''' writes data to pkl file. 
        '''
        with open('../workspaces/{}/frame_data/frame{}.pkl'.format(self.workspace_name, frame_count), mode='wb') as fp:
            pickle.dump(frame_data, fp)
        fp.close()