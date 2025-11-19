import numpy as np
import os
import sys
import poses.colmap_read_model as read_model

def load_colmap_data_save_txt(realdir):
    sparse_txt_dir = os.path.join(realdir, 'sparse_txt')
    os.makedirs(sparse_txt_dir, exist_ok=True)

    camerasfile = os.path.join(realdir, 'sparse/0/cameras.bin')
    camdata = read_model.read_cameras_binary(camerasfile)
    with open(os.path.join(sparse_txt_dir, 'cameras.txt'), 'w') as f:
        for key, value in camdata.items():
            f.write(f'{key} {value.model} ')  # 添加相机模型
            f.write(' '.join(map(str, value.params)))  # 将相机参数转换为字符串并写入
            f.write('\n')

    imagesfile = os.path.join(realdir, 'sparse/0/images.bin')
    imdata = read_model.read_images_binary(imagesfile)
    with open(os.path.join(sparse_txt_dir, 'images.txt'), 'w') as f:
        for key, value in imdata.items():
            f.write(f'{key} {value.qvec[0]} {value.qvec[1]} {value.qvec[2]} {value.qvec[3]} ')  # 添加旋转四元数
            f.write(' '.join(map(str, value.tvec)))  # 将平移向量转换为字符串并写入
            f.write(f' {value.camera_id} {value.name}\n')  # 添加相机ID和图像名称

    points3Dfile = os.path.join(realdir, 'sparse/0/points3D.bin')
    ptdata = read_model.read_points3d_binary(points3Dfile)
    with open(os.path.join(sparse_txt_dir, 'points3D.txt'), 'w') as f:
        for key, value in ptdata.items():
            f.write(f'{key} ')  # point id
            f.write(' '.join(map(str, value.xyz)))  # xyz
            f.write(' ')  # 添加空格
            f.write(' '.join(map(str, value.rgb)))  # rgb
            f.write(f' {value.error} ')  # error
            f.write(' '.join(map(str, value.image_ids)))  # image_ids
            f.write(' '.join(map(str, value.point2D_idxs)) + '\n')  # point2D_idxs


if __name__=='__main__':
    load_colmap_data_save_txt(sys.argv[1])