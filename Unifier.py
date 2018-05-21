############################################
#                     _    _  _            #
#        |  | |\ | | |_ | |_ |_|           #
#        \_/  | \| | |  | |_ | \           #
#                                          #
#  I've been quite irritated with the UI   #
#  mess that is Blender 2.8. You normally  #
#  need to move between engines to change  #
# most options. This addon aims to "Unify" #
#the engines into one large engine (Cycles)#
#   and allow you to do things like edit   #
#   materials from the matcap engine or    #
#from the solid engine. You can also change#
#the post processing effects for the real- #
#  time engine from the toolbar as well.   #
############################################

#sites.google.com/site/sidedvirusartandanimation

bl_info = {"name": "Unifier v0.3", "category": "All"}
#Addon details.

import bpy
from bpy_extras.node_utils import (
        find_node_input,
        find_output_node,
        )

from bpy.types import (
        Panel,
        Menu,
        Operator,
        )

class UnifierButtonsPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOL_PROPS"

class UnifierMaterialsButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.material and (context.engine in cls.COMPAT_ENGINES)

#Real-time settings

#Materials
class UnifierMaterialContext(UnifierMaterialsButtonsPanel, Panel):
    #DO NOT enable in raytracer or real-time engine.
    #This will lead to a duplicate material list.
    bl_label = ""
    bl_context = "material"
    bl_options = {'HIDE_HEADER'}
    COMPAT_ENGINES = {'BLENDER_CLAY', 'BLENDER_WORKBENCH'}

    @classmethod
    def poll(cls, context):
        engine = context.engine
        return (context.material or context.object) and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        mat = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data

        if ob:
            is_sortable = len(ob.material_slots) > 1
            rows = 1
            if (is_sortable):
                rows = 4

            row = layout.row()

            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ZOOMIN', text="")
            col.operator("object.material_slot_remove", icon='ZOOMOUT', text="")

            col.menu("MATERIAL_MT_specials", icon='DOWNARROW_HLT', text="")

            if is_sortable:
                col.separator()

                col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

        split = layout.split(percentage=0.65)

        if ob:
            split.template_ID(ob, "active_material", new="material.new")
            row = split.row()

            if slot:
                row.prop(slot, "link", text="")
            else:
                row.label()
        elif mat:
            split.template_ID(space, "pin_id")
            split.separator()


def panel_node_draw(layout, ntree, output_type):
    node = find_output_node(ntree, output_type)

    if node:
        input = find_node_input(node, 'Surface')
        if input:
            layout.template_node_view(ntree, node, input)
        else:
            layout.label(text="Incompatible output node")
    else:
        layout.label(text="No output node")


class UnifierMaterialSurface(UnifierMaterialsButtonsPanel, Panel):
    bl_label = "OpenGL Surface"
    bl_context = "material"
    #COMPAT_ENGINES = {'BLENDER_EEVEE'}
    #Disabling COMPAT_ENGINES for now. This means active in all engines.

    @classmethod
    def poll(cls, context):
        engine = context.engine
        return context.material and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        mat = context.material

        layout.prop(mat, "use_nodes", icon='NODETREE')
        layout.separator()

        if mat.use_nodes:
            panel_node_draw(layout, mat.node_tree, ('OUTPUT_EEVEE_MATERIAL', 'OUTPUT_MATERIAL'))
        else:
            raym = mat.raytrace_mirror
            layout.prop(mat, "diffuse_color", text="Base Color")
            layout.prop(raym, "reflect_factor", text="Metallic")
            layout.prop(mat, "specular_intensity", text="Specular")
            layout.prop(raym, "gloss_factor", text="Roughness")

class UnifierMaterialPreview(UnifierMaterialsButtonsPanel, Panel):
    #Do not use in raytracer. When implemented to raytracer it uses raytraced preview.
    #Implimenting it provides no real benefit. Only necessary in matcap, real-time, and solid.
    bl_label = "Preview"
    COMPAT_ENGINES = {'BLENDER_EEVEE', 'BLENDER_CLAY', 'BLENDER_WORKBENCH', 'BLENDER_RENDER'}

    def draw(self, context):
        self.layout.template_preview(context.material)

class UnifierMaterialOptions(UnifierMaterialsButtonsPanel, Panel):
    #This option is much different than raytracer "Settings."
    #Controls real-time engine's transparency blending as well as SSS and SSR.
    bl_label = "OpenGL Options"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        engine = context.engine
        return context.material and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        mat = context.material

        layout.prop(mat, "blend_method")

        if mat.blend_method != "OPAQUE":
            layout.prop(mat, "transparent_shadow_method")

            row = layout.row()
            row.active = ((mat.blend_method == "CLIP") or (mat.transparent_shadow_method == "CLIP"))
            row.prop(mat, "alpha_threshold")

        if mat.blend_method not in {"OPAQUE", "CLIP", "HASHED"}:
            layout.prop(mat, "transparent_hide_backside")

        layout.prop(mat, "use_screen_refraction")
        layout.prop(mat, "refraction_depth")

        layout.prop(mat, "use_screen_subsurface")
        row = layout.row()
        row.active = mat.use_screen_subsurface
        row.prop(mat, "use_sss_translucency")

class UnifierMaterialViewport(UnifierMaterialsButtonsPanel, Panel):
    #Breaks Cycles interface. Becomes duplicate.
    bl_label = "Solid Viewport Colors"
    bl_context = "material"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE', 'BLENDER_CLAY', 'BLENDER_WORKBENCH', 'BLENDER_RENDER'}

    @classmethod
    def poll(cls, context):
        return context.material and CyclesButtonsPanel.poll(context)

    def draw(self, context):
        mat = context.material

        layout = self.layout
        split = layout.split()

        col = split.column(align=True)
        col.label("Color:")
        col.prop(mat, "diffuse_color", text="")
        
        #The following were commented out to clean up the interface. Specular and alpha currently (19.05.18) are useless.
        #col.prop(mat, "alpha")

        #col = split.column(align=True)
        #col.label("Specular:")
        #col.prop(mat, "specular_color", text="")

#Post Processing
class UnifierPostProcessGTAO(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtao"
    bl_label = "Shade: GTAO"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "gtao_enable", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.eevee

        layout.active = props.gtao_enable
        col = layout.column()
        col.prop(props, "gtao_use_bent_normals")
        col.prop(props, "gtao_bounce")
        col.prop(props, "gtao_distance")
        col.prop(props, "gtao_factor")
        col.prop(props, "gtao_quality")


class UnifierPostProcessBlur(UnifierButtonsPanel, Panel):
    #TODO Redo this section when object motion blur gets implemented.
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtmb"
    bl_label = "Shade: Motion Blur"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "motion_blur_enable", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.eevee

        layout.active = props.motion_blur_enable
        col = layout.column()
        col.prop(props, "motion_blur_samples")
        col.prop(props, "motion_blur_shutter")


class UnifierPostProcessDOF(UnifierButtonsPanel, Panel):
    #TODO When Clement fixes the DOF, make sure to see if this feature needs updating. 
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtdof"
    bl_label = "Shade: DOF"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "dof_enable", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.eevee

        layout.active = props.dof_enable
        col = layout.column()
        col.prop(props, "bokeh_max_size")
        col.prop(props, "bokeh_threshold")


class UnifierPostProcessBloom(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtblm"
    bl_label = "Shade: Bloom"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "bloom_enable", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.eevee

        layout.active = props.bloom_enable
        col = layout.column()
        col.prop(props, "bloom_threshold")
        col.prop(props, "bloom_knee")
        col.prop(props, "bloom_radius")
        col.prop(props, "bloom_color")
        col.prop(props, "bloom_intensity")
        col.prop(props, "bloom_clamp")


class UnifierPostProcessVolume(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtvol"
    bl_label = "Shade: Volume"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "volumetric_enable", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.eevee

        layout.active = props.volumetric_enable
        col = layout.column()
        col.prop(props, "volumetric_start")
        col.prop(props, "volumetric_end")
        col.prop(props, "volumetric_tile_size")
        col.prop(props, "volumetric_samples")
        col.prop(props, "volumetric_sample_distribution")
        col.prop(props, "volumetric_lights")
        col.prop(props, "volumetric_light_clamp")
        col.prop(props, "volumetric_shadows")
        col.prop(props, "volumetric_shadow_samples")
        col.prop(props, "volumetric_colored_transmittance")


class UnifierPostProcessSSS(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtsss"
    bl_label = "Shade: SSS"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "sss_enable", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.eevee

        col = layout.column()
        col.prop(props, "sss_samples")
        col.prop(props, "sss_jitter_threshold")
        col.prop(props, "sss_separate_albedo")


class UnifierPostProcessSSR(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtssr"
    bl_label = "Shade: SSR"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "ssr_enable", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.eevee

        col = layout.column()
        col.active = props.ssr_enable
        col.prop(props, "ssr_refraction")
        col.prop(props, "ssr_halfres")
        col.prop(props, "ssr_quality")
        col.prop(props, "ssr_max_roughness")
        col.prop(props, "ssr_thickness")
        col.prop(props, "ssr_border_fade")
        col.prop(props, "ssr_firefly_fac")


class UnifierPostProcessShadow(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtsha"
    bl_label = "Shade: Shadows"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.eevee

        col = layout.column()
        col.prop(props, "shadow_method")
        col.prop(props, "shadow_cube_size")
        col.prop(props, "shadow_cascade_size")
        col.prop(props, "shadow_high_bitdepth")


class UnifierPostProcessSample(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtsam"
    bl_label = "Shade: Sampling"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.eevee

        col = layout.column()
        col.prop(props, "taa_samples")
        col.prop(props, "taa_render_samples")
        col.prop(props, "taa_reprojection")


class UnifierPostProcessGI(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtgi"
    bl_label = "Shade: GI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.eevee

        col = layout.column()
        col.prop(props, "gi_diffuse_bounces")
        col.prop(props, "gi_cubemap_resolution")
        col.prop(props, "gi_visibility_resolution")


class UnifierPostProcessFilm(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtfil"
    bl_label = "Shade: Film"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rd = scene.render

        split = layout.split()

        col = split.column()
        col.prop(rd, "filter_size")

        col = split.column()
        col.prop(rd, "alpha_mode", text="Alpha")

#Matcap settings
class UnifierMatcapSettings(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "mcset"
    bl_label = "Matcap: Settings"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_CLAY', 'CYCLES', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH', 'BLENDER_RENDER'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.display

        col = layout.column()
        col.template_icon_view(props, "matcap_icon")
        col.prop(props, "matcap_rotation")
        col.prop(props, "matcap_hue")
        col.prop(props, "matcap_saturation")
        col.prop(props, "matcap_value")
        col.prop(props, "matcap_ssao_samples")
        col.prop(props, "matcap_ssao_factor_cavity")
        col.prop(props, "matcap_ssao_factor_edge")
        col.prop(props, "matcap_ssao_distance")
        col.prop(props, "matcap_ssao_attenuation")
        col.prop(props, "matcap_hair_brightness_randomness")

#Solid settings
class UnifierSolidDisplay(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "sddisp"
    bl_label = "Solid: Shading"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene.display, "light_direction", text="")
        layout.prop(scene.display, "shadow_shift")

def draw_device(self, context):
    scene = context.scene
    layout = self.layout

def draw_pause(self, context):
    layout = self.layout
    scene = context.scene

def get_panels():
    exclude_panels = {
        'DATA_PT_area',
        'DATA_PT_camera_dof',
        'DATA_PT_falloff_curve',
        'DATA_PT_lamp',
        'DATA_PT_preview',
        'DATA_PT_spot',
        'MATERIAL_PT_context_material',
        'UnifierMaterialPreview',
        'VIEWLAYER_PT_filter',
        'VIEWLAYER_PT_layer_passes',
        'RENDER_PT_post_processing',
        'SCENE_PT_simplify',
        }

    panels = []
    return panels

#Renaming to "Unifier" is not necessary,
#but will ultimately lead to better organization.
classes = (
    UnifierMaterialPreview,
    UnifierMaterialContext,
    UnifierMaterialSurface,
    UnifierMaterialOptions,
    UnifierMaterialViewport,
    UnifierPostProcessGTAO,
    UnifierPostProcessBlur,
    UnifierPostProcessDOF,
    UnifierPostProcessBloom,
    UnifierPostProcessVolume,
    UnifierPostProcessSSS,
    UnifierPostProcessSSR,
    UnifierPostProcessShadow,
    UnifierPostProcessSample,
    UnifierPostProcessGI,
    UnifierPostProcessFilm,
    UnifierSolidDisplay,
    UnifierMatcapSettings,
)


def register():
    from bpy.utils import register_class

    bpy.types.RENDER_PT_render.append(draw_device)
    bpy.types.VIEW3D_HT_header.append(draw_pause)

    for panel in get_panels():
        panel.COMPAT_ENGINES.add('CYCLES')

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    bpy.types.RENDER_PT_render.remove(draw_device)
    bpy.types.VIEW3D_HT_header.remove(draw_pause)

    for panel in get_panels():
        if 'CYCLES' in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove('CYCLES')

    for cls in classes:
        unregister_class(cls)