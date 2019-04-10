import argparse
import cv2
import sys
import util.workspacecreator as workspacecreator

def main():
    # parsing command line arguments
    parser = argparse.ArgumentParser(description='initialize bee tracking workspace')
    parser.add_argument('video_path', metavar='video-path', type=str, 
                            help='the path to the mp4 file')
    parser.add_argument('workspace_name', metavar='workspace-name', type=str, 
                            help='the name of the new workspace')
    args = parser.parse_args()
    
    video_path = args.video_path
    workspace_name = args.workspace_name

    workspace_creator = workspacecreator.WorkSpaceCreator(video_path, workspace_name)
    workspace_creator.create_directory()
    workspace_creator.get_crop_points()
    workspace_creator.crop_video()
    workspace_creator.get_singles_sizes()
    workspace_creator.count_frames()
    workspace_creator.write_config_file()

if __name__ == "__main__":
    main()