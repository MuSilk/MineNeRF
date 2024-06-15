import nbtlib
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
    R_1, G_1, B_1 = rgb_1
    R_2, G_2, B_2 = rgb_2
    rmean = (R_1 + R_2) / 2
    R = R_1 - R_2
    G = G_1 - G_2
    B = B_1 - B_2
    return math.sqrt((2 + rmean / 256) * (R ** 2) + 4 * (G ** 2) + (2 + (255 - rmean) / 256) * (B ** 2))


def get_nearest_blockID(rgb):
    id = 0
    # print(block_available)
    dis = color_distance(rgb, block_available["0"]["Color"])
    for key, value in block_available.items():
        tmpdis = color_distance(rgb, value["Color"])
        if tmpdis < dis:
            dis = tmpdis
            id = int(key)
    return id

def convert_voxel_grid_to_nbt(voxel_grid, outputname):
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
        'entities': List([]),  # 结构方块内的实体，示例中为空
        'blocks': block_list,
        'palette': palette_list,
        'DataVersion': Int(2566),  # Minecraft 1.16 的数据版本
    })

    nbt_file = nbtlib.File(structure)
    nbt_file.save(outputname, gzipped=True)
