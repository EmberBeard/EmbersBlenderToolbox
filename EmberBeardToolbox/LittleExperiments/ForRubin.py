import bpy
import bmesh
from mathutils import Vector

class MESH_OT_mirror_uv_seams(bpy.types.Operator):
    """Flip the UV seam information across the X axis"""
    bl_idname = "mesh.mirror_uv_seams"
    bl_label = "Mirror Mesh Seams (X axis)"
    bl_options = {'REGISTER', 'UNDO'}
    
    tolerance: bpy.props.FloatProperty(name="Tolerance", default=0.001)
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH' or obj.mode != 'EDIT':
            self.report({'ERROR'}, "Must be in Edit Mode with a Mesh object.")
            return {'CANCELLED'}

        bm = bmesh.from_edit_mesh(obj.data)

        selected_verts = [v for v in bm.verts if v.select]
        if not selected_verts:
            self.report({'WARNING'}, "No vertices selected.")
            return {'FINISHED'}
        
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
    
        # 1. Create a spatial map of vertices for quick lookup
        # We use rounded coordinates as keys to find mirrors fast
        kd = {}
        for v in bm.verts:
            key = (round(v.co.x, 4), round(v.co.y, 4), round(v.co.z, 4))
            kd[key] = v

        # 2. Iterate and match
        for edge in bm.edges:
            # Define the target mirrored positions for both verts of this edge
            v1_pos = edge.verts[0].co
            v2_pos = edge.verts[1].co
            
            m1_key = (round(-v1_pos.x, 4), round(v1_pos.y, 4), round(v1_pos.z, 4))
            m2_key = (round(-v2_pos.x, 4), round(v2_pos.y, 4), round(v2_pos.z, 4))
        
            # Find the mirrored vertices in our map
            mv1 = kd.get(m1_key)
            mv2 = kd.get(m2_key)
            
            if mv1 and mv2 and mv1 != mv2:
                # Find the edge connecting the two mirrored vertices
                #mirror_edge = bmesh.ops.find_double_edges(bm, edges=[edge], verts=[mv1, mv2])
                # Alternatively, use the direct sequence lookup:
                mirror_edge = bm.edges.get((mv1, mv2))
                
                if mirror_edge:
                    mirror_edge.seam = edge.seam

        bmesh.update_edit_mesh(obj.data)
        
        return {'FINISHED'}

class MESH_OT_mirror_uv_coords(bpy.types.Operator):
    """Copy UV coordinates from selected vertices to their mirrored counterparts on X-axis"""
    bl_idname = "mesh.mirror_uv_coords"
    bl_label = "Mirror UV Coords (X-Axis)"
    bl_options = {'REGISTER', 'UNDO'}

    tolerance: bpy.props.FloatProperty(name="Tolerance", default=0.001)

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH' or obj.mode != 'EDIT':
            self.report({'ERROR'}, "Must be in Edit Mode with a Mesh object.")
            return {'CANCELLED'}

        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.active
        
        if not uv_layer:
            self.report({'ERROR'}, "No active UV layer found.")
            return {'CANCELLED'}

        selected_verts = [v for v in bm.verts if v.select]
        if not selected_verts:
            self.report({'WARNING'}, "No vertices selected.")
            return {'FINISHED'}

        all_verts = bm.verts
        updated_count = 0

        for s_vert in selected_verts:
            target_pos = s_vert.co.copy()
            target_pos.x *= -1 # Find mirrored point
            
            # Locate mirrored vertex by position
            t_vert = None
            for v in all_verts:
                if (v.co - target_pos).length < self.tolerance:
                    t_vert = v
                    break
            
            if t_vert:
                # Mirror UVs across face loops
                for s_loop in s_vert.link_loops:
                    s_face_center = s_loop.face.calc_center_median()
                    s_face_center.x *= -1
                    
                    for t_loop in t_vert.link_loops:
                        if (t_loop.face.calc_center_median() - s_face_center).length < self.tolerance:
                            t_loop[uv_layer].uv = s_loop[uv_layer].uv.copy()
                            updated_count += 1

        bmesh.update_edit_mesh(obj.data)
        self.report({'INFO'}, f"Updated {updated_count} loop UVs.")
        return {'FINISHED'}


class VIEW3D_PT_EmbersTools(bpy.types.Panel):
    bl_space_type = "VIEW_3D" # https://docs.blender.org/api/current/bpy_types_enum_items/space_type_items.html#rna-enum-space-type-items
    bl_region_type = "UI" # https://docs.blender.org/api/current/bpy_types_enum_items/region_type_items.html#rna-enum-region-type-items
    bl_category = "Ember's Mini Tools"
    bl_label = "Ember's Mini Toolbox"
    
    def draw(self, context):
        self.layout.label(text="For Rubin")
        MirrorCoordsRow = self.layout.row()
        MirrorCoordsRow.operator("mesh.mirror_uv_coords", text="X mirror UV coords")
        MirrorSeamRow = self.layout.row()
        MirrorSeamRow.operator("mesh.mirror_uv_seams", text="X mirror UV seams")


classes = (
    VIEW3D_PT_EmbersTools,
    MESH_OT_mirror_uv_coords,
    MESH_OT_mirror_uv_seams,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        del bpy.types.Scene.EmbersToolBox

if __name__ == "__main__":
    register()