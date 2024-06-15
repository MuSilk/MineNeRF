import numpy as np
import open3d as o3d
from sklearn.neighbors import NearestNeighbors
from skimage.segmentation import slic

# 读取或生成点云数据
# 这里我们生成一个简单的3D点云数据作为示例
num_points = 1000
points = np.random.rand(num_points, 3)  # 生成随机点云数据


# 计算每个点的颜色特征（这里用点的坐标作为颜色特征）
colors = points

# 将点云数据和颜色特征合并
data = np.hstack((points, colors))

# 使用SLIC进行超像素分割
labels = slic(data, n_segments=100, compactness=10, multichannel=True, start_label=1)

# 将分割结果添加到点云数据中
point_cloud = o3d.geometry.PointCloud()
point_cloud.points = o3d.utility.Vector3dVector(points)
colors = plt.cm.jet(labels / labels.max())
point_cloud.colors = o3d.utility.Vector3dVector(colors[:, :3])

# 可视化分割结果
o3d.visualization.draw_geometries([point_cloud])