import numpy as np

# Path to the poses_bounds.npy file
poses_bounds_path_org = "/media/zzg/GJ_disk01/data/Videos/dynerf/cook_spinach_4DG/poses_bounds.npy"
poses_bounds_path_gen = "/home/zzg/data/CV/dynerf/Take_154814_aligned_sorted_4DG/poses_bounds.npy"

# Load the .npy file
poses_bounds_org = np.load(poses_bounds_path_org)
poses_bounds_gen = np.load(poses_bounds_path_gen)

print(f"Loaded poses_bounds.npy with shape: {poses_bounds_org.shape}")
print(f"Loaded poses_bounds.npy with shape: {poses_bounds_gen.shape}")

# Split into poses and bounds
poses_org = poses_bounds_org[:, :-2].reshape([-1, 3, 5])  # (N, 3, 5)
bounds_org = poses_bounds_org[:, -2:]                     # (N, 2)
# Extract rotation (R) and translation (t)
R_org = poses_org[:, :, :3]  # rotation matrices (N, 3, 3)
t_org = poses_org[:, :, 3]   # translation vectors (N, 3)
# Print a quick summary
print(f"Number of frames: {len(poses_org)}")
print("Example rotation matrix:\n", R_org[0])
print("Example translation vector:\n", t_org[0])
print("Example bounds (near, far):", bounds_org[0])

# Split into poses and bounds
poses_gen = poses_bounds_gen[:, :-2].reshape([-1, 3, 5])  # (N, 3, 5)
bounds_gen = poses_bounds_gen[:, -2:]                     # (N, 2)
# Extract rotation (R) and translation (t)
R_gen = poses_gen[:, :, :3]  # rotation matrices (N, 3, 3)
t_gen = poses_gen[:, :, 3]   # translation vectors (N, 3)
# Print a quick summary
print(f"Number of frames: {len(poses_gen)}")
print("Example rotation matrix:\n", R_gen[0])
print("Example translation vector:\n", t_gen[0])
print("Example bounds (near, far):", bounds_gen[0])