bl_info = {
    "name": "T3D Animated Mesh (.t3d)",
    "author": "Tobias Heukäufer",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "File > Export > T3D Animated (.t3d)",
    "description": "Export T3D Animated Mesh (.t3d)",
    "category": "Import-Export"}


import bpy
from bpy_extras.io_utils import ExportHelper
import bmesh
import struct
from mathutils import Matrix
from math import radians


class Vertex(object):
    def __init__(self, index, uv):
        self.index = index
        self.uv = uv

    def is_same(self, index, uv):
        if self.index != index:
            return False

        for i in range(2):
            if abs(uv[i] - self.uv[i]) > 0.0001:
                return False

        return True


def export(context, path):
        # Find mesh
        mesh = context.active_object
        
        # Find frames
        frames = []
        if len(bpy.data.actions) > 0:
            # Currently only one action supported :(
            for fcu in bpy.data.actions[0].fcurves:
                for frame in fcu.keyframe_points:
                    time = frame.co[0]
                    for time_ref in frames:
                        if abs(time - time_ref) < 0.001:
                            break
                    else:
                        frames.append(time)
        frames = sorted(frames)
        if len(frames) == 0:
            frames.append(1.0)

        # Build triangles and vertices
        vertices = []
        triangles = []
        for polygon in mesh.data.polygons:
            indices = [None] * 3
            uvs = [None] * 3
            indices[0] = polygon.vertices[0]
            indices[1] = polygon.vertices[1]
            uvs[0] = polygon.loop_indices[0]
            uvs[1] = polygon.loop_indices[1]
            # Triangulate mesh
            for i in range(2, len(polygon.vertices)):
                indices[2] = polygon.vertices[i]
                uvs[2] = polygon.loop_indices[i]
                triangle = [0] * 3
                # Find vertices in list or create new ones
                for j in range(3):
                    index = indices[j]
                    uv = [0.0, 0.0]
                    if mesh.data.uv_layers.active:
                        uv = mesh.data.uv_layers.active.data[uvs[j]].uv
                    for k in range(len(vertices)):
                        if vertices[k].is_same(index, uv):
                            triangle[j] = k
                            break
                    else:
                        vertices.append(Vertex(index, uv))
                        triangle[j] = len(vertices) - 1
                triangles.append(triangle)
                indices[1] = indices[2]
                uvs[1] = uvs[2]

        # Write file
        with open(path, "wb") as file:
            # GLuint version;
            file.write(struct.pack(">I", 1))

            # GLubyte frameCount;
            file.write(struct.pack(">B", len(frames)))
            # GLfloat frameTimes[frameCount];
            for frame in frames:
                file.write(struct.pack(">f", frame))

            # GLushort vertexCount;
            file.write(struct.pack(">H", len(vertices)))
            # GLfloat uv[2 * vertexCount];
            for vertex in vertices:
                file.write(struct.pack(">f", vertex.uv[0]))
                file.write(struct.pack(">f", 1.0 - vertex.uv[1]))

            # GLfloat xyz[3 * vertexCount * frameCount];
            correction = Matrix.Rotation(radians(-90), 4, 'X')
            for frame in frames:
                context.scene.frame_set(frame)
                mesh_frame = mesh.to_mesh(context.scene, True, 'PREVIEW')
                for vertex in vertices:
                    coordinate = correction * mesh.matrix_world * mesh_frame.vertices[vertex.index].co
                    file.write(struct.pack(">f", coordinate[0]))
                    file.write(struct.pack(">f", coordinate[1]))
                    file.write(struct.pack(">f", coordinate[2]))

            # GLushort triangleCount;
            file.write(struct.pack(">H", len(triangles)))
            # GLushort triangles[3 * triangleCount];
            for triangle in triangles:
                file.write(struct.pack(">H", triangle[0]))
                file.write(struct.pack(">H", triangle[1]))
                file.write(struct.pack(">H", triangle[2]))

        print(len(vertices), "vertices,", len(triangles), "triangles,", len(frames), "frames")


class ExportT3DAnimated(bpy.types.Operator, ExportHelper):
    bl_idname = "export.t3d"
    bl_label = "Export T3D Animated"
    
    filename_ext = ".t3d"

    @classmethod
    def poll(cls, context):
        return context.active_object.type == "MESH"


    def execute(self, context):
        path = bpy.path.ensure_ext(self.filepath, self.filename_ext)

        export(context, path)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ExportT3DAnimated.bl_idname, text="T3D Animated (.t3d)")


def register():
    bpy.utils.register_class(ExportT3DAnimated)
    bpy.types.INFO_MT_file_export.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ExportT3DAnimated)
    bpy.types.INFO_MT_file_export.remove(menu_func)
