

workdir=$1
datatype=$2 # blender, hypernerf, llff
CUDA_ID=$3
export CUDA_VISIBLE_DEVICES="$CUDA_ID"
rm -rf $workdir/sparse_
rm -rf $workdir/image_colmap
python queen_data_preprocess/scripts/"$datatype"2colmap.py $workdir
rm -rf $workdir/colmap
rm -rf $workdir/colmap/sparse/0

mkdir $workdir/colmap
cp -r $workdir/image_colmap $workdir/colmap/images
cp -r $workdir/sparse_ $workdir/colmap/sparse_custom
# 1) 特征提取：更多特征、开启 DSP-SIFT / 仿射估计
colmap feature_extractor \
  --database_path $workdir/colmap/database.db \
  --image_path $workdir/colmap/images \
  --SiftExtraction.use_gpu "$CUDA_ID" \
  --SiftExtraction.max_image_size 4096 \
  --SiftExtraction.max_num_features 32768 \
  --SiftExtraction.estimate_affine_shape 1 \
  --SiftExtraction.domain_size_pooling 1 \
  --SiftExtraction.peak_threshold 0.004       # 默认 ~0.0067，降低可提取更多点（小幅降噪风险）

python queen_data_preprocess/scripts/database.py --database_path $workdir/colmap/database.db --txt_path $workdir/colmap/sparse_custom/cameras.txt
# 2) 匹配：启用 guided matching（降低错误配对），可以适当放宽 ratio
colmap exhaustive_matcher \
  --database_path $workdir/colmap/database.db \
  --SiftMatching.max_ratio 0.85 \
  --ExhaustiveMatching.block_size 200 \
  --FeatureMatching.guided_matching 1
mkdir -p $workdir/colmap/sparse/0

# 3) 三角化（point_triangulator）：取消忽略两视图轨迹并放低最小三角角度
colmap point_triangulator \
  --database_path $workdir/colmap/database.db \
  --image_path $workdir/colmap/images \
  --input_path $workdir/colmap/sparse_custom \
  --output_path $workdir/colmap/sparse/0 \
  --clear_points 1 \
  --Mapper.tri_ignore_two_view_tracks 0 \
  --Mapper.tri_min_angle 1.0                # 默认 ~1.5°，降低可增加近远景点（但易噪）
mkdir -p $workdir/colmap/dense/workspace
colmap image_undistorter --image_path $workdir/colmap/images --input_path $workdir/colmap/sparse/0 --output_path $workdir/colmap/dense/workspace
# 4) dense MVS：patch-match 调参，放松 photo-consistency 检查、增大 window radius、增大 cache
colmap patch_match_stereo \
  --workspace_path $workdir/colmap/dense/workspace \
  --PatchMatchStereo.max_image_size 4096 \
  --PatchMatchStereo.window_radius 7 \
  --PatchMatchStereo.num_iterations 5 \
  --PatchMatchStereo.filter 1 \
  --PatchMatchStereo.filter_min_ncc 0.06 \
  --PatchMatchStereo.filter_min_num_consistent 2 \
  --PatchMatchStereo.geom_consistency 1 \
  --PatchMatchStereo.cache_size 64                # GB (根据你机器改)，增大减少磁盘 IO

# 5) fusion：允许更少视图就生成点（更稠密，但更可能噪）
colmap stereo_fusion \
  --workspace_path $workdir/colmap/dense/workspace \
  --output_path $workdir/colmap/dense/workspace/fused.ply \
  --StereoFusion.max_image_size 4096 \
  --StereoFusion.min_num_pixels 2 \
  --StereoFusion.cache_size 64