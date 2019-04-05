import argparse
import cv2
import util.videoprocessor as videoprocessor

def main():
    # parsing command line arguments
    parser = argparse.ArgumentParser(description='tracking bees')
    parser.add_argument('workspace_name', metavar='workspace_name', type=str, 
                            help='the name of the workspace to do tracking on')
    args = parser.parse_args()
    
    processor = videoprocessor.VideoProcessor(args.workspace_name)
    processor.process_video()

if __name__ == "__main__":
    main()