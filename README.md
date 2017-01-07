# T3D File Format

A very simple 3D mesh file format collection.

## T3D Animated Meshes (*.t3d)

T3D Animated Meshes use vertex morphing for animation.

### Specification

What follows is a specification in C code style. Data types are used as defined in the [OpenGL wiki.](https://www.opengl.org/wiki/OpenGL_Type) T3D Animated Meshes are stored in big endian.

    GLuint version; /* version = 1 */
    
    GLubyte frameCount;
    GLfloat frameTimes[frameCount];
    
    GLushort vertexCount;
    GLfloat uv[2 * vertexCount];
    GLfloat xyz[3 * vertexCount * frameCount];
    
    GLushort triangleCount;
    GLushort triangles[3 * triangleCount];

### Software/Scripts

#### Blender Exporter

See *Animated/io_export_t3d.py* for a Blender export script (successfully tested with Blender 2.78). It converts skeletal animation (achieved by armature) to vertex morphing.

## T3D Mesh Batches (*.t3db)

T3D Mesh Batches are multiple meshes bundled together in a file to be retrieved by name.

### Specification

What follows is a specification in C code style. Data types are used as defined in the [OpenGL wiki.](https://www.opengl.org/wiki/OpenGL_Type) T3D Mesh Batches are stored in big endian.

    struct mesh {
        GLubyte nameLength;
        char letters[nameLength]
        GLushort triangleCount;
    };
    
    GLuint version; /* version = 1 */
    
    GLushort vertexCount;
    GLfloat xyzuv[5 * vertexCount];
    GLushort triangleCount;
    GLushort triangles[3 * triangleCount]
    
    GLubyte meshCount;
    struct mesh meshes[meshCount];

### Software/Scripts

#### OBJ Bundler

See *Batch/obj2batch.py* for a OBJ bundler. It takes a list of Wavefront Object files and the output file name as arguments (e.g. `obj2batch.py foo.obj bar.obj foobar.t3db`) storing the OBJ files under their file names/paths as given by argument.