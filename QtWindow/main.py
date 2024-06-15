import copy
import sys
import threading

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtGui import QWindow
from PyQt5.QtCore import QTimer
import open3d as o3d
import win32gui
import os
import numpy as np

import ui
from QtWindow import convert


class MainWindow(QMainWindow):
    voxel_grid = None

    def __init__(self):
        super().__init__()
        self.ui = ui.Ui_MineNeRF()
        self.ui.setupUi(self)

        self.pid = os.getpid()
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(visible=False, window_name="Open3d" + str(self.pid))
        self.winid = win32gui.FindWindow("GLFW30", "Open3d" + str(self.pid))
        self.sub_window = QWindow.fromWinId(self.winid)
        self.displayer = QWidget.createWindowContainer(self.sub_window)
        self.ui.grid_display.addWidget(self.displayer)
        self.clock = QTimer(self)
        self.clock.timeout.connect(self.draw_update)
        self.clock.start(20)

        self.valx = -1.56
        self.ui.SliderX.setMinimum(int(-np.pi * 100))
        self.ui.SliderX.setMaximum(int(np.pi * 100))
        self.ui.SliderX.setValue(int(self.valx*100))

        def fx():
            self.valx = self.ui.SliderX.value() / 100
            self.update_geometry()
            print(self.valx)

        self.ui.SliderX.valueChanged.connect(fx)

        self.valy = 0
        self.ui.SliderY.setMinimum(int(-np.pi * 100))
        self.ui.SliderY.setMaximum(int(np.pi * 100))
        self.ui.SliderY.setValue(int(self.valy*100))

        def fy():
            self.valy = self.ui.SliderY.value() / 100
            self.update_geometry()
            print(self.valy)

        self.ui.SliderY.valueChanged.connect(fy)

        self.valz = 0.52
        self.ui.SliderZ.setMinimum(int(-np.pi * 100))
        self.ui.SliderZ.setMaximum(int(np.pi * 100))
        self.ui.SliderZ.setValue(int(self.valz*100))

        def fz():
            self.valz = self.ui.SliderZ.value() / 100
            self.update_geometry()
            print(self.valz)

        self.ui.SliderZ.valueChanged.connect(fz)

        self.voxel_size = -1.83
        self.ui.SliderVoxelSize.setMinimum(-600)
        self.ui.SliderVoxelSize.setMaximum(600)
        self.ui.SliderVoxelSize.setValue(int(self.voxel_size * 100))

        def fv():
            self.voxel_size = self.ui.SliderVoxelSize.value() / 100
            self.update_geometry()
            print(self.voxel_size)

        self.ui.SliderVoxelSize.valueChanged.connect(fv)

        self.ply_origin = o3d.io.read_point_cloud("../point_cloud_treated.ply")
        self.ply = copy.deepcopy(self.ply_origin)
        self.voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(self.ply,
                                                                         voxel_size=pow(10, self.voxel_size))

        def export():
            def f():
                print("export start")
                convert.convert_voxel_grid_to_nbt(self.voxel_grid, "structure.nbt")
                print("export finished.")
            thread=threading.Thread(target=f)
            thread.start()

        self.ui.Export.released.connect(export)

        self.draw_init()

    def draw_init(self):
        RenderOption: o3d.visualization.RenderOption = self.vis.get_render_option()
        RenderOption.light_on = False
        self.vis.add_geometry(self.voxel_grid)
        axis = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1)
        self.vis.add_geometry(axis)

    def update_geometry(self):
        self.vis.remove_geometry(self.voxel_grid)
        self.ply = copy.deepcopy(self.ply_origin)
        R = self.ply.get_rotation_matrix_from_xyz((self.valx, self.valy, self.valz))
        self.ply.rotate(R)

        self.voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(self.ply,
                                                                         voxel_size=pow(10, self.voxel_size))
        self.vis.add_geometry(self.voxel_grid)

    def draw_update(self):
        self.vis.poll_events()
        self.vis.update_renderer()

    def __del__(self):
        self.vis.destroy_window()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
