# Import of TIFF Grid (.tif) for Blender
# Installs import menu entry in Blender

# Ian Daniel METELSKI  metelski.ian.p@gmail.com
# 23/08/2024

# This code is based on the original ASCII version from Hans Rudolf Bär
# Original Credits ↓
# Magnus Heitzler hmagnus@ethz.ch
# Hans Rudolf Bär  hansruedi.baer@bluewin.ch
# 24/10/2015
# Institute of Cartography and Geoinformation
# ETH Zurich

bl_info = {
    "name": "Import GeoTIFF (.tif)",
    "author": "Ian METELSKI",
    "blender": (3, 2, 0),
    "version": (1, 0, 0),
    "location": "File > Import > GeoTIFF (.tif)",
    "description": "Import meshes from GeoTIFF file format",
    "warning": "",
    "support": "COMMUNITY",
    "category": "Import-Export",
}

import bpy
import os
import math
from bpy_extras.io_utils import ImportHelper
import OpenImageIO as oiio
import numpy as np

class ImportGeoTIFF(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.tif"
    bl_label = "Import GeoTIFF"
    bl_options = {'PRESET'}

    filename_ext = ".tif"

    filter_glob = bpy.props.StringProperty(
        default="*.tif",
        options={"HIDDEN"},
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        filename = self.filepath
        img = oiio.ImageInput.open(filename)
        if not img:
            self.report({'ERROR'}, "Unable to open GeoTIFF file.")
            return {'CANCELLED'}

        spec = img.spec()
        cols = spec.width
        rows = spec.height
        data = np.array(img.read_image("float"), dtype=np.float32).reshape((rows, cols))
        img.close()
        data = np.flipud(data)  # Flip data

        vertices = []
        faces = []

        # Create vertices
        for r in range(rows):
            for c in range(cols):
                z_value = float(data[r, c])
                vertices.append((c, r, z_value))

        # Construct faces
        index = 0
        for r in range(rows - 1):
            for c in range(cols - 1):
                v1 = index
                v2 = v1 + cols
                v3 = v2 + 1
                v4 = v1 + 1
                faces.append((v1, v2, v3, v4))
                index += 1
            index += 1

        # Create mesh
        name = os.path.splitext(os.path.basename(filename))[0]
        me = bpy.data.meshes.new(name)
        ob = bpy.data.objects.new(name, me)
        ob.location = (0, 0, 0)
        ob.show_name = True

        col = bpy.context.collection
        col.objects.link(ob)
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)

        # Transform mesh
        ob.scale = (0.5, 0.5, 1)  # Apply scaling
        center_x = -0.5 * 0.5 * (cols - 1)
        center_y = -0.5 * 0.5 * (rows - 1)
        bpy.ops.transform.translate(value=(center_x, center_y, 0))

        me.from_pydata(vertices, [], faces)
        me.update()

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout

    def invoke(self, context, event):
        return super().invoke(context, event)


def menu_func(self, context):
    self.layout.operator(ImportGeoTIFF.bl_idname, text="GeoTIFF (.tif)")


def register():
    bpy.utils.register_class(ImportGeoTIFF)
    bpy.types.TOPBAR_MT_file_import.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ImportGeoTIFF)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)


if __name__ == "__main__":
    register()
