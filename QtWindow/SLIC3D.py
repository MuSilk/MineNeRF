import copy
import statistics

import numpy as np
import open3d as o3d
import skimage
import matplotlib.pyplot as plt
import time


class SLIC3D:
    points = None  # normalized to [0,1]
    colors = None  # lab
    cluster_centers_points = None  # normalized to [0,1]
    cluster_centers_colors = None  # lab

    voxel_grid = None  # int
    voxel_grid_color = None

    def __init__(self, filename, voxel_size, up_samples=1, weight=1):
        print("--init begin--")
        self.voxel_size = voxel_size
        self.weight = weight
        self.up_samples = up_samples

        self.point_cloud: o3d.geometry.PointCloud = o3d.io.read_point_cloud(filename)
        self.min_bound = self.point_cloud.get_min_bound()
        self.range = self.point_cloud.get_max_bound() - self.point_cloud.get_min_bound()
        self.max_dis_2 = np.sum(self.range * self.range)

        self.points = self.point_cloud.points - self.min_bound
        self.colors = skimage.color.rgb2lab(self.point_cloud.colors)

        voxel_indices = np.floor((self.point_cloud.points - self.min_bound) / (voxel_size / up_samples)).astype(int)
        voxel_bound = np.max(voxel_indices, axis=0) + 1

        voxel_grid = np.full((voxel_bound[0], voxel_bound[1], voxel_bound[2], 4), 0.0)

        for coord, color in zip(voxel_indices, self.colors):
            x, y, z = coord
            voxel_grid[x, y, z] += np.append(color, 1)
        self.cluster_centers_points = []
        self.cluster_centers_colors = []
        for x in range(voxel_bound[0]):
            for y in range(voxel_bound[1]):
                for z in range(voxel_bound[2]):
                    if voxel_grid[x][y][z][3] > 0.1:
                        coord = (np.array([x, y, z], dtype=np.float64) + 0.5) * voxel_size / up_samples
                        color = voxel_grid[x][y][z][0:3] / voxel_grid[x][y][z][3]
                        self.cluster_centers_points.append(coord)
                        self.cluster_centers_colors.append(color)
        self.cluster_centers_points = np.array(self.cluster_centers_points)
        self.cluster_centers_colors = np.array(self.cluster_centers_colors)

        self.init_voxel_grid()
        print("--init finish--")

    def init_voxel_grid(self):
        voxel_indices = np.floor((self.point_cloud.points - self.min_bound) / self.voxel_size).astype(int)
        voxel_bound = np.max(voxel_indices, axis=0) + 1

        voxel_grid = np.full((voxel_bound[0], voxel_bound[1], voxel_bound[2], 4), 0.0)

        for coord, color in zip(voxel_indices, self.colors):
            x, y, z = coord
            voxel_grid[x, y, z] += np.append(color, 1)
        self.voxel_grid = []
        self.voxel_grid_color = []
        for x in range(voxel_bound[0]):
            for y in range(voxel_bound[1]):
                for z in range(voxel_bound[2]):
                    if voxel_grid[x][y][z][3] > 0.1:
                        self.voxel_grid.append(np.array([x, y, z]))
                        color = voxel_grid[x][y][z][0:3] / voxel_grid[x][y][z][3]
                        self.voxel_grid_color.append(color)
        self.voxel_grid = np.array(self.voxel_grid)
        self.voxel_grid_color = np.array(self.voxel_grid_color)

    def get_center(self, coord, color):
        ds = self.cluster_centers_points - coord
        ds = np.sum(ds * ds, axis=-1)
        dc = self.cluster_centers_colors - color
        dc = np.sum(dc * dc, axis=-1)
        D = np.sqrt(ds/self.max_dis_2 * self.weight + dc)
        return np.argmin(D), np.min(D)

    def get_new_centers(self):
        clusters = np.full((len(self.cluster_centers_points), 7), 0.0)
        D = 0
        for coord, color in zip(self.points, self.colors):
            center, d = self.get_center(coord, color)
            clusters[center] += np.concatenate((coord, color, [1.0]))
            D += d
        for i in range(len(self.cluster_centers_points)):
            if clusters[i][6] > 0:
                self.cluster_centers_points[i] = clusters[i][0:3] / clusters[i][6]
                self.cluster_centers_colors[i] = clusters[i][3:6] / clusters[i][6]
        return D

    def get_voxel_grid(self):
        o3d_voxel_grid = o3d.geometry.VoxelGrid()
        o3d_voxel_grid.voxel_size = self.voxel_size
        for coord in self.voxel_grid:
            real_coord = (coord + 0.5) * self.voxel_size
            # id=self.get_center(real_coord,color)
            ds = self.cluster_centers_points - real_coord
            ds = np.sum(ds * ds, axis=-1)
            id = np.argmin(ds)

            color = skimage.color.lab2rgb(self.cluster_centers_colors[id])

            o3d_voxel_grid.add_voxel(o3d.geometry.Voxel(coord, color))
        return o3d_voxel_grid


if __name__ == '__main__':
    t0=time.time()
    cluster = SLIC3D("../point_cloud_treated.ply", 0.018, weight=10000, up_samples=1)
    # voxel_grid = cluster.get_voxel_grid()
    # o3d.visualization.draw_geometries([voxel_grid])
    x=np.arange(20)
    y=np.full(20,0)
    y[0]=time.time()-t0
    for i in range(19):
        print("--iteration {} begin--".format(i), end=" ")
        D = cluster.get_new_centers()
        y[i+1]=time.time()-t0
        print("--iteration {} finish--,D={}".format(i, D))

    voxel_grid = cluster.get_voxel_grid()
    o3d.visualization.draw_geometries([voxel_grid])

    plt.xticks(range(len(x)), x)
    plt.xlabel("Iterations")
    plt.ylabel("D")
    plt.plot(x,y)
    plt.show()
