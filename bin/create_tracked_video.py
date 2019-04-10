import argparse
import cv2
import pickle
import util.trackedvideocreator as trackedvideocreator

def main():
    # parsing command line arguments
    parser = argparse.ArgumentParser(description='creating a tracking video from location data')
    parser.add_argument('workspace_name', metavar='workspace_name', type=str, 
                            help='the name of the workspace to do tracking on')
    args = parser.parse_args()
    
    creator = trackedvideocreator.TrackedVideoCreator(args.workspace_name)
    creator.create_video()

if __name__ == "__main__":
    main()