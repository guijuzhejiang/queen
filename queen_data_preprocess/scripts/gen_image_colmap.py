import os
import glob
from argparse import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser(description="Extract images from dynerf videos")
    parser.add_argument("--datadir", default='/media/zzg/GJ_disk01/data/Videos/dynerf_test/cook_spinach_4DG', type=str)
    args = parser.parse_args()
    datadir = args.datadir
    videos = glob.glob(os.path.join(datadir, "cam[0-9][0-9]"))
    videos = sorted(videos)
    image_paths = []
    for index, video_path in enumerate(videos):
        image_path = os.path.join(video_path, "images", "0000.png")
        image_paths.append(image_path)
    print(image_paths)
    goal_dir = os.path.join(datadir, "image_colmap")
    if not os.path.exists(goal_dir):
        os.makedirs(goal_dir)
    import shutil

    image_name_list = []
    for index, image in enumerate(image_paths):
        image_name = image.split("/")[-1].split('.')
        image_name[0] = "r_%03d" % index
        print(image_name)
        # breakpoint()
        image_name = ".".join(image_name)
        image_name_list.append(image_name)
        goal_path = os.path.join(goal_dir, image_name)
        shutil.copy(image, goal_path)
