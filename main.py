import copy

import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import numpy as np

import convert


class App:

    def __init__(self):
        self.valX, self.valY, self.valZ = 0, 0, 0
        self.val_voxel_size = -1.9

        gui.Application.instance.initialize()
        self.window = gui.Application.instance.create_window('TestApp')
        em = self.window.theme.font_size

        self.scene = gui.SceneWidget()
        self.scene.scene = rendering.Open3DScene(self.window.renderer)

        self.material = rendering.MaterialRecord()
        self.material.shader = 'defaultUnlit'

        self.ply_origin = o3d.io.read_point_cloud("point_cloud_treated.ply")
        self.ply = copy.deepcopy(self.ply_origin)

        self.voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(self.ply,
                                                                         voxel_size=pow(10, self.val_voxel_size))
        self.scene.scene.add_geometry("voxel_grid", self.voxel_grid, self.material)

        axis = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1)
        self.scene.scene.add_geometry("axis", axis, self.material)

        bounds = self.ply.get_axis_aligned_bounding_box()
        self.scene.setup_camera(60, bounds, bounds.get_center())

        self.sliderX = gui.Slider(gui.Slider.Type(1))
        self.sliderX.set_limits(-np.pi, np.pi)

        def sliderX(val):
            self.valX = val
            self.rerenderscene()

        self.sliderX.set_on_value_changed(sliderX)

        self.sliderY = gui.Slider(gui.Slider.Type(1))
        self.sliderY.set_limits(-np.pi, np.pi)

        def sliderY(val):
            self.valY = val
            self.rerenderscene()

        self.sliderY.set_on_value_changed(sliderY)

        self.sliderZ = gui.Slider(gui.Slider.Type(1))
        self.sliderZ.set_limits(-np.pi, np.pi)

        def sliderZ(val):
            self.valZ = val
            self.rerenderscene()

        self.sliderZ.set_on_value_changed(sliderZ)

        self.slider_voxel_grid = gui.Slider(gui.Slider.Type(3))
        self.slider_voxel_grid.set_limits(-6, 6)
        self.slider_voxel_grid.double_value = self.val_voxel_size

        def slider_voxel_grid(val):
            self.val_voxel_size = val
            self.rerenderscene()

        self.slider_voxel_grid.set_on_value_changed(slider_voxel_grid)

        self.export_button = gui.Button("export nbt file(structure.nbt)")
        self.export_button.horizontal_padding_em = 0.5
        self.export_button.vertical_padding_em = 0

        def export_button():
            convert.convert_voxel_grid_to_nbt(self.voxel_grid, "structure.nbt")
            print("export finished.")
            # o3d.io.write_voxel_grid("output.ply", self.voxel_grid, write_ascii=True, print_progress=True)

        self.export_button.set_on_clicked(export_button)

        self.sidebar = gui.Vert(0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.254 * em))
        self.sidebar.add_child(self.sliderX)
        self.sidebar.add_child(self.sliderY)
        self.sidebar.add_child(self.sliderZ)
        self.sidebar.add_child(self.slider_voxel_grid)
        self.sidebar.add_child(self.export_button)

        self.window.set_on_layout(self.init_layout)
        self.window.add_child(self.scene)
        self.window.add_child(self.sidebar)

    def run(self):
        gui.Application.instance.run()

    def init_layout(self, layout_content):
        r = self.window.content_rect
        self.scene.frame = r

        sidebar_width = 0.2 * r.width
        sidebar_height = r.height
        self.sidebar.frame = gui.Rect(r.get_right() - sidebar_width, r.y, sidebar_width, sidebar_height)

    def rerenderscene(self):
        self.scene.scene.remove_geometry("voxel_grid")
        self.ply = copy.deepcopy(self.ply_origin)
        R = self.ply.get_rotation_matrix_from_xyz((self.valX, self.valY, self.valZ))
        self.ply.rotate(R)

        self.voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(self.ply,
                                                                         voxel_size=pow(10, self.val_voxel_size))
        self.scene.scene.add_geometry("voxel_grid", self.voxel_grid, self.material)

        self.scene.force_redraw()


if __name__ == "__main__":
    app = App()
    app.run()
