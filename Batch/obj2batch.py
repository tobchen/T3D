import struct
import sys
from os import path

class Mesh(object):
    def __init__(self, path):
        def get_face_vert(raw):
            data = raw.split("/")
            v = vt = int(data[0]) - 1
            if len(data) > 1 and data[1] != "":
                vt = int(data[1]) - 1
            return (v, vt)

        self.path = path

        self.xyz = []
        self.uv = []
        faces = []

        with open(path) as file:
            for line in file:
                data = line.split()
                if len(data) == 0:
                    continue

                if data[0] == "v":
                    w = 1.0 if len(data) < 5 else float(data[4])
                    self.xyz.append((float(data[1]) / w, float(data[2]) / w, float(data[3]) / w))
                elif data[0] == "vt":
                    u = float(data[1])
                    v = 1.0 - float(data[2])
                    self.uv.append((u, v))
                elif data[0] == "f":
                    face = []
                    v0 = get_face_vert(data[1])
                    v1 = get_face_vert(data[2])
                    for i in range(3, len(data)):
                        v2 = get_face_vert(data[i])
                        faces.append((v0, v1, v2))
                        v1 = v2

        self.vertices = []
        self.triangles = []

        for face in faces:
            triangle = []
            for vertex in face:
                for i in range(len(self.vertices)):
                    if vertex == self.vertices[i]:
                        triangle.append(i)
                        break
                else:
                    self.vertices.append(vertex)
                    triangle.append(len(self.vertices) - 1)
            self.triangles.append(tuple(triangle))

if len(sys.argv) < 3:
    print("Not enough arguments! Needs at least one input and an output file!")
    exit()

meshes = []
for i in range(1, len(sys.argv) - 1):
    meshes.append(Mesh(sys.argv[i]))

with open(sys.argv[-1], "wb") as file:
    # GLuint version;
    file.write(struct.pack(">I", 1))

    # GLushort vertexCount;
    vertex_count = 0
    for mesh in meshes:
        vertex_count += len(mesh.vertices)
    file.write(struct.pack(">H", vertex_count))
    # GLfloat xyzuv[5 * vertexCount];
    for mesh in meshes:
        for vertex in mesh.vertices:
            for c in mesh.xyz[vertex[0]] + mesh.uv[vertex[1]]:
                file.write(struct.pack(">f", c))

    # GLushort triangleCount;
    triangle_count = 0
    for mesh in meshes:
        triangle_count += len(mesh.triangles)
    file.write(struct.pack(">H", triangle_count))
    # GLushort triangles[3 * triangleCount]
    offset = 0
    for mesh in meshes:
        for triangle in mesh.triangles:
            for i in triangle:
                file.write(struct.pack(">H", i + offset))
        offset += len(mesh.vertices)

    # GLubyte meshCount;
    file.write(struct.pack(">B", len(meshes)))
    # struct mesh meshes[meshCount];
    for mesh in meshes:
        name = path.basename(mesh.path)
        # GLubyte nameLength;
        file.write(struct.pack(">B", len(name)))
        # char letter[nameLength]
        for letter in name:
            file.write(struct.pack("c", letter.encode('ascii')))
        # GLushort triangleCount;
        file.write(struct.pack(">H", len(mesh.triangles)))

print("Vertices:", vertex_count)
print("Triangles:", triangle_count)
print("Indices:", triangle_count * 3)
