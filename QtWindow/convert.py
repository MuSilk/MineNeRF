import nbtlib
import skimage
import numpy as np
from nbtlib.tag import *
import math
import json

import open3d as o3d

block_available = {}


def get_block_available():
    global block_available
    with open("../block_available/color_table.json", 'r') as file:
        block_available = json.load(file)
    # print(color_table)


def color_distance(rgb_1, rgb_2):  # LAB
    lab1 = skimage.color.rgb2lab(np.array(rgb_1) / 255)
    lab2 = skimage.color.rgb2lab(np.array(rgb_2) / 255)

    return skimage.color.deltaE_ciede2000(lab1,lab2)


def get_nearest_blockID(rgb):
    id = 0
    dis = color_distance(rgb, block_available["0"]["Color"])
    for key, value in block_available.items():
        tmpdis = color_distance(rgb, value["Color"])
        if tmpdis < dis:
            dis = tmpdis
            id = int(key)
    return id


def convert_voxel_grid_to_nbt(voxel_grid: o3d.geometry.VoxelGrid, outputname):
    get_block_available()
    palette_list = List[Compound]()
    for key, value in block_available.items():
        palette_list.append(
            Compound({
                'Name': String(value["Name"])
            })
        )

    block_list = List[Compound]()
    for voxel in voxel_grid.get_voxels():
        block = Compound({
            'pos': List[Int]([Int(voxel.grid_index[0]), Int(voxel.grid_index[1]), Int(voxel.grid_index[2])]),
            'state': Int(get_nearest_blockID(voxel.color * 255)),
        })
        block_list.append(block)

    size = (voxel_grid.get_max_bound() - voxel_grid.get_min_bound()) / voxel_grid.voxel_size

    structure = Compound({
        'size': List[Int]([Int(size[0]), Int(size[1]), Int(size[2])]),
        'entities': List([]),  # 结构方块内的实体
        'blocks': block_list,
        'palette': palette_list,
        'DataVersion': Int(2566),  # Minecraft 1.16 的数据版本
    })

    nbt_file = nbtlib.File(structure)
    nbt_file.save(outputname, gzipped=True)


if "__main__" == __name__:
    pc = o3d.io.read_point_cloud("../point_cloud_treated.ply")
    vg = o3d.geometry.VoxelGrid.create_from_point_cloud(pc,voxel_size=0.018)
    convert_voxel_grid_to_nbt(vg, "test.nbt")

    print(1)
