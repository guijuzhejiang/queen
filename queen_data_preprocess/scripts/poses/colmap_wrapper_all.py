import os
import subprocess
from queen_data_preprocess.scripts import database
import shutil



# $ DATASET_PATH=/path/to/dataset

# $ colmap feature_extractor \
#    --database_path $DATASET_PATH/database.db \
#    --image_path $DATASET_PATH/images

# $ colmap exhaustive_matcher \
#    --database_path $DATASET_PATH/database.db

# $ mkdir $DATASET_PATH/sparse

# $ colmap mapper \
#     --database_path $DATASET_PATH/database.db \
#     --image_path $DATASET_PATH/images \
#     --output_path $DATASET_PATH/sparse

# $ mkdir $DATASET_PATH/dense
def run_colmap(basedir, match_type):
    
    logfile_name = os.path.join(basedir, 'colmap_output.txt')
    logfile = open(logfile_name, 'w')
    
    feature_extractor_args = [
        'colmap', 'feature_extractor', 
            '--database_path', os.path.join(basedir, 'database.db'), 
            '--image_path', os.path.join(basedir, 'images'),
            # '--ImageReader.single_camera', '1',
            '--SiftExtraction.max_image_size', '4096',
            '--SiftExtraction.max_num_features', '16384',
            '--SiftExtraction.estimate_affine_shape', '1',
            '--SiftExtraction.domain_size_pooling', '1',
    ]
    feat_output = (subprocess.check_output(feature_extractor_args, universal_newlines=True) )
    logfile.write(feat_output)
    print('Features extracted')

    parent_dir = os.path.dirname(basedir)
    src = os.path.join(parent_dir, "colmap", "sparse_custom")
    dst = os.path.join(basedir, "sparse_custom")
    # 复制整个目录（递归）
    shutil.copytree(src, dst, dirs_exist_ok=True)

    #参考queen_data_preprocess/colmap.sh:17增加-----------
    db_path = os.path.join(basedir, 'database.db')
    txt_path = os.path.join(basedir, 'sparse_custom', 'cameras.txt')
    data_preprocess_args = [
        'python',
        'database.py',
        '--database_path', db_path,
        '--txt_path', txt_path
    ]
    data_preprocess_output = subprocess.check_output(data_preprocess_args, universal_newlines=True)
    logfile.write(data_preprocess_output)
    print('data_preprocess over')

    exhaustive_matcher_args = [
        'colmap', match_type, 
            '--database_path', os.path.join(basedir, 'database.db'), 
    ]

    match_output = ( subprocess.check_output(exhaustive_matcher_args, universal_newlines=True) )
    logfile.write(match_output)
    print('Features matched')
    
    p = os.path.join(basedir, 'sparse')
    if not os.path.exists(p):
        os.makedirs(p)

    # Reference queen_data_preprocess/colmap.sh:19 and 21 - point_triangulator
    point_triangulator_path = os.path.join(basedir, 'sparse', '0')
    if not os.path.exists(point_triangulator_path):
        os.makedirs(point_triangulator_path)

    point_triangulator_args = [
        'colmap', 'point_triangulator',
            '--database_path', os.path.join(basedir, 'database.db'),
            '--image_path', os.path.join(basedir, 'images'),
            '--input_path', os.path.join(basedir, 'sparse_custom'),
            '--output_path', point_triangulator_path,
            '--clear_points', '1'
    ]
    point_triangulator_output = (subprocess.check_output(point_triangulator_args, universal_newlines=True) )
    logfile.write(point_triangulator_output)
    print('Point triangulator over')

    # Reference queen_data_preprocess/colmap.sh:23 and 24 - image_undistorter
    dense_workspace_path = os.path.join(basedir, 'dense', 'workspace')
    if not os.path.exists(dense_workspace_path):
        os.makedirs(dense_workspace_path)

    image_undistorter_args = [
        'colmap', 'image_undistorter',
            '--image_path', os.path.join(basedir, 'images'),
            '--input_path', point_triangulator_path,
            '--output_path', dense_workspace_path
    ]
    image_undistorter_output = (subprocess.check_output(image_undistorter_args, universal_newlines=True) )
    logfile.write(image_undistorter_output)
    print('Image undistorter over')

    # Reference queen_data_preprocess/colmap.sh:25 - patch_match_stereo
    patch_match_stereo_args = [
        'colmap', 'patch_match_stereo',
            '--workspace_path', dense_workspace_path
    ]
    patch_match_stereo_output = (subprocess.check_output(patch_match_stereo_args, universal_newlines=True) )
    logfile.write(patch_match_stereo_output)
    print('Patch match stereo over')

    # Reference queen_data_preprocess/colmap.sh:26 - stereo_fusion
    stereo_fusion_args = [
        'colmap', 'stereo_fusion',
            '--workspace_path', dense_workspace_path,
            '--output_path', os.path.join(dense_workspace_path, 'fused.ply')
    ]
    stereo_fusion_output = (subprocess.check_output(stereo_fusion_args, universal_newlines=True) )
    logfile.write(stereo_fusion_output)
    print('Stereo fusion over')

    # mapper_args = [
    #     'colmap', 'mapper', 
    #         '--database_path', os.path.join(basedir, 'database.db'), 
    #         '--image_path', os.path.join(basedir, 'images'),
    #         '--output_path', os.path.join(basedir, 'sparse'),
    #         '--Mapper.num_threads', '16',
    #         '--Mapper.init_min_tri_angle', '4',
    # ]
    mapper_args = [
        'colmap', 'mapper',
            '--database_path', os.path.join(basedir, 'database.db'),
            '--image_path', os.path.join(basedir, 'images'),
            '--output_path', os.path.join(basedir, 'sparse'), # --export_path changed to --output_path in colmap 3.6
            '--Mapper.num_threads', '16',
            '--Mapper.init_min_tri_angle', '4',
            '--Mapper.multiple_models', '0',
            '--Mapper.extract_colors', '0',
    ]

    map_output = ( subprocess.check_output(mapper_args, universal_newlines=True) )
    logfile.write(map_output)
    logfile.close()
    print('Sparse map created')
    
    print( 'Finished running COLMAP, see {} for logs'.format(logfile_name) )


