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

bl_info = {"name": "Unifier V:0.6", "category": "All"}
#Addon details.
import bpy
import nodeitems_utils
from bpy_extras.node_utils import (
        find_node_input,
        find_output_node,
        )
from bpy.types import (
        Panel,
        Menu,
        Operator,
        Header,
        )

#With Version 0.4 and 0.5 bugs patched and newer Blender 2.8 build issues resolved, the next task is to unify the node editor.
#This may be a large task. Any contributions would be appreciated here: https://developer.blender.org/T55120.

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

class UnifierDataButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        engine = context.engine
        return context.lamp and (engine in cls.COMPAT_ENGINES)

class UnifierLightProbeButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        engine = context.engine
        return context.lightprobe and (engine in cls.COMPAT_ENGINES)

#Real-time settings

#Lamps
class UnifierLampPreview(UnifierDataButtonsPanel, Panel):
    bl_label = "OpenGL Preview"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}

    def draw(self, context):
        self.layout.template_preview(context.lamp)

class UnifierLampLamp(UnifierDataButtonsPanel, Panel):
    bl_label = "OpenGL Lamp Properties"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_CLAY', 'CYCLES', 'BLENDER_WORKBENCH'}

    def draw(self, context):
        layout = self.layout

        lamp = context.lamp

        layout.row().prop(lamp, "type", expand=True)

        split = layout.split()

        col = split.column()
        sub = col.column()
        sub.prop(lamp, "color", text="")
        sub.prop(lamp, "energy")

        if lamp.type in {'POINT', 'SPOT'}:
            sub.label(text="Falloff:")
            sub.prop(lamp, "falloff_type", text="")
            sub.prop(lamp, "distance")
            sub.prop(lamp, "shadow_soft_size", text="Radius")
            if lamp.falloff_type == 'LINEAR_QUADRATIC_WEIGHTED':
                col.label(text="Attenuation Factors:")
                sub = col.column(align=True)
                sub.prop(lamp, "linear_attenuation", slider=True, text="Linear")
                sub.prop(lamp, "quadratic_attenuation", slider=True, text="Quadratic")

            elif lamp.falloff_type == 'INVERSE_COEFFICIENTS':
                col.label(text="Inverse Coefficients:")
                sub = col.column(align=True)
                sub.prop(lamp, "constant_coefficient", text="Constant")
                sub.prop(lamp, "linear_coefficient", text="Linear")
                sub.prop(lamp, "quadratic_coefficient", text="Quadratic")

        if lamp.type == 'AREA':
            col.prop(lamp, "distance")

        col = split.column()
        col.label()

class UnifierLampLampRealTime(UnifierDataButtonsPanel, Panel):
    bl_label = "OpenGL Lamp"
    COMPAT_ENGINES = {'BLENDER_EEVEE', 'BLENDER_CLAY', 'BLENDER_WORKBENCH', 'CYCLES'}

    def draw(self, context):
        layout = self.layout

        lamp = context.lamp

        layout.row().prop(lamp, "type", expand=True)

        split = layout.split()

        col = split.column()
        sub = col.column()
        sub.prop(lamp, "color", text="")
        sub.prop(lamp, "energy")

        if lamp.type in {'POINT', 'SPOT', 'SUN'}:
            sub.prop(lamp, "shadow_soft_size", text="Radius")
        elif lamp.type == 'AREA':
            sub = sub.column(align=True)
            sub.prop(lamp, "shape", text="")
            if lamp.shape  in {'SQUARE', 'DISK'}:
                sub.prop(lamp, "size")
            elif lamp.shape in {'RECTANGLE', 'ELLIPSE'}:
                sub.prop(lamp, "size", text="Size X")
                sub.prop(lamp, "size_y", text="Size Y")

        col = split.column()
        col.prop(lamp, "specular_factor", text="Specular")

class UnifierLampShadow(UnifierDataButtonsPanel, Panel):
    bl_label = "OpenGL Shadow"
    bl_options = {'DEFAULT_CLOSED'}
    #COMPAT_ENGINES = {'BLENDER_EEVEE'}

    @classmethod
    def poll(cls, context):
        lamp = context.lamp
        engine = context.engine
        return (lamp and lamp.type in {'POINT', 'SUN', 'SPOT', 'AREA'}) and (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
        lamp = context.lamp
        self.layout.prop(lamp, "use_shadow", text="")

    def draw(self, context):
        layout = self.layout

        lamp = context.lamp

        split = layout.split()
        split.active = lamp.use_shadow

        sub = split.column()
        col = sub.column(align=True)
        col.prop(lamp, "shadow_buffer_clip_start", text="Clip Start")
        col.prop(lamp, "shadow_buffer_clip_end", text="Clip End")
        col = sub.column()
        col.prop(lamp, "shadow_buffer_soft", text="Soft")

        col = split.column(align=True)
        col.prop(lamp, "shadow_buffer_bias", text="Bias")
        col.prop(lamp, "shadow_buffer_exp", text="Exponent")
        col.prop(lamp, "shadow_buffer_bleed_bias", text="Bleed Bias")

        if lamp.type == 'SUN':
            col = layout.column()
            col.active = lamp.use_shadow
            col.label("Cascaded Shadow Map:")

            split = col.split()

            sub = split.column()
            sub.prop(lamp, "shadow_cascade_count", text="Count")
            sub.prop(lamp, "shadow_cascade_fade", text="Fade")

            sub = split.column()
            sub.prop(lamp, "shadow_cascade_max_distance", text="Max Distance")
            sub.prop(lamp, "shadow_cascade_exponent", text="Distribution")

        layout.separator()

        layout.prop(lamp, "use_contact_shadow")
        split = layout.split()
        split.active = lamp.use_contact_shadow
        col = split.column()
        col.prop(lamp, "contact_shadow_distance", text="Distance")
        col.prop(lamp, "contact_shadow_soft_size", text="Soft")

        col = split.column()
        col.prop(lamp, "contact_shadow_bias", text="Bias")
        col.prop(lamp, "contact_shadow_thickness", text="Thickness")

class UnifierLampArea(UnifierDataButtonsPanel, Panel):
    bl_label = "Area Shape"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE', 'BLENDER_RENDER', 'BLENDER_CLAY', 'BLENDER_WORKBENCH'}

    @classmethod
    def poll(cls, context):
        lamp = context.lamp
        engine = context.engine
        return (lamp and lamp.type == 'AREA') and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        lamp = context.lamp

        col = layout.column()
        col.row().prop(lamp, "shape", expand=True)
        sub = col.row(align=True)

        if lamp.shape in {'SQUARE', 'DISK'}:
            sub.prop(lamp, "size")
        elif lamp.shape in {'RECTANGLE', 'ELLIPSE'}:
            sub.prop(lamp, "size", text="Size X")
            sub.prop(lamp, "size_y", text="Size Y")

class UnifierLampSpot(UnifierDataButtonsPanel, Panel):
    bl_label = "Spot Shape"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE', 'BLENDER_RENDER', 'BLENDER_CLAY', 'BLENDER_WORKBENCH'}

    @classmethod
    def poll(cls, context):
        lamp = context.lamp
        engine = context.engine
        return (lamp and lamp.type == 'SPOT') and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        lamp = context.lamp

        split = layout.split()

        col = split.column()
        sub = col.column()
        sub.prop(lamp, "spot_size", text="Size")
        sub.prop(lamp, "spot_blend", text="Blend", slider=True)
        col = split.column()
        col.prop(lamp, "show_cone")

class UnifierLampFalloff(UnifierDataButtonsPanel, Panel):
    bl_label = "Falloff Curve"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_CLAY', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}

    @classmethod
    def poll(cls, context):
        lamp = context.lamp
        engine = context.engine

        return (lamp and lamp.type in {'POINT', 'SPOT'} and lamp.falloff_type == 'CUSTOM_CURVE') and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        lamp = context.lamp

        self.layout.template_curve_mapping(lamp, "falloff_curve", use_negative_slope=True)

#Material Settings
class UnifierRealTimeShading(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtshg"
    bl_label = "Mat: Shading"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        

        view = context.space_data
        shading = view.shading

        col = layout.column()

        if shading.type in ('MATERIAL', 'RENDERED', 'SOLID', 'TEXTURED'):
            col.row().template_icon_view(shading, "studio_light")
            if shading.studio_light_orientation == 'WORLD':
                col.row().prop(shading, "studiolight_rot_z")
                col.row().prop(shading, "studiolight_background")
            col.row().prop(shading, "use_scene_light")

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
        #Old bug now fixed. Raytracer no longer has this duplicate option.

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
    bl_options = {'DEFAULT_CLOSED'}

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
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE', 'BLENDER_CLAY', 'BLENDER_WORKBENCH', 'BLENDER_RENDER'}

    def draw(self, context):
        self.layout.template_preview(context.material)

class UnifierMaterialOptions(UnifierMaterialsButtonsPanel, Panel):
    #This option is much different than raytracer "Settings."
    #Controls real-time engine's transparency blending as well as SSS and SSR.
    bl_label = "OpenGL Options"
    bl_context = "material"
    bl_options = {'DEFAULT_CLOSED'}

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
        engine = context.engine
        return context.material and (engine in cls.COMPAT_ENGINES)

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

#Light Probes
class UnifierLightProbeContext(UnifierLightProbeButtonsPanel, Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    COMPAT_ENGINES = {'BLENDER_WORKBENCH', 'BLENDER_RENDER', 'CYCLES'}

    def draw(self, context):
        layout = self.layout

        ob = context.object
        probe = context.lightprobe
        space = context.space_data

        if ob:
            layout.template_ID(ob, "data")
        elif probe:
            layout.template_ID(space, "pin_id")


class UnifierLightProbeProbe(UnifierLightProbeButtonsPanel, Panel):
    bl_label = "Probe"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_WORKBENCH', 'BLENDER_RENDER', 'CYCLES'}

    def draw(self, context):
        layout = self.layout

        ob = context.object
        probe = context.lightprobe

        split = layout.split()

        if probe.type == 'GRID':
            col = split.column(align=True)
            col.label("Influence:")
            col.prop(probe, "influence_distance", "Distance")
            col.prop(probe, "falloff")
            col.prop(probe, "intensity")

            col.separator()

            col.label("Resolution:")
            col.prop(probe, "grid_resolution_x", text="X")
            col.prop(probe, "grid_resolution_y", text="Y")
            col.prop(probe, "grid_resolution_z", text="Z")
        elif probe.type == 'PLANAR':
            col = split.column(align=True)
            col.label("Influence:")
            col.prop(probe, "influence_distance", "Distance")
            col.prop(probe, "falloff")
        else:
            col = split.column(align=True)
            col.label("Influence:")
            col.prop(probe, "influence_type", text="")

            if probe.influence_type == 'ELIPSOID':
                col.prop(probe, "influence_distance", "Radius")
            else:
                col.prop(probe, "influence_distance", "Size")

            col.prop(probe, "falloff")
            col.prop(probe, "intensity")

        col = split.column(align=True)

        col.label("Clipping:")
        col.prop(probe, "clip_start", text="Start")

        if probe.type != "PLANAR":
            col.prop(probe, "clip_end", text="End")

        if probe.type == 'GRID':
            col.separator()

            col.label("Visibility:")
            col.prop(probe, "visibility_buffer_bias", "Bias")
            col.prop(probe, "visibility_bleed_bias", "Bleed Bias")
            col.prop(probe, "visibility_blur", "Blur")

        col.separator()

        col.label("Visibility Group:")
        row = col.row(align=True)
        row.prop(probe, "visibility_group", text="")
        row.prop(probe, "invert_visibility_group", text="", icon='ARROW_LEFTRIGHT')


class UnifierLightProbeParallax(UnifierLightProbeButtonsPanel, Panel):
    bl_label = "Custom Parallax"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_WORKBENCH', 'BLENDER_RENDER', 'CYCLES'}

    @classmethod
    def poll(cls, context):
        engine = context.engine
        return context.lightprobe and context.lightprobe.type == 'CUBEMAP' and (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
        probe = context.lightprobe
        self.layout.prop(probe, "use_custom_parallax", text="")

    def draw(self, context):
        layout = self.layout

        probe = context.lightprobe

        col = layout.column()
        col.active = probe.use_custom_parallax

        row = col.row()
        row.prop(probe, "parallax_type", expand=True)

        if probe.parallax_type == 'ELIPSOID':
            col.prop(probe, "parallax_distance", "Radius")
        else:
            col.prop(probe, "parallax_distance", "Size")


class UnifierLightProbeDisplay(UnifierLightProbeButtonsPanel, Panel):
    bl_label = "Display"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_WORKBENCH', 'BLENDER_RENDER', 'CYCLES'}

    def draw(self, context):
        layout = self.layout

        ob = context.object
        probe = context.lightprobe

        row = layout.row()
        row.prop(probe, "show_data")

        if probe.type != "PLANAR":
            row.prop(probe, "data_draw_size", text="Size")
        else:
            row.prop(ob, "empty_draw_size", text="Arrow Size")

        split = layout.split()

        if probe.type in {'GRID', 'CUBEMAP'}:
            col = split.column()
            col.prop(probe, "show_influence")

            col = split.column()
            col.prop(probe, "show_clip")

        if probe.type == 'CUBEMAP':
            col = split.column()
            col.active = probe.use_custom_parallax
            col.prop(probe, "show_parallax")

#Post Processing
class UnifierPostProcessGTAO(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtao"
    bl_label = "Mat: GTAO"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "use_gtao", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        props = scene.eevee

        layout.active = props.use_gtao
        col = layout.column()
        col.prop(props, "use_gtao_bent_normals")
        col.prop(props, "use_gtao_bounce")
        col.prop(props, "gtao_distance")
        col.prop(props, "gtao_factor")
        col.prop(props, "gtao_quality")


class UnifierPostProcessBlur(UnifierButtonsPanel, Panel):
    #TODO Redo this section when object motion blur gets implemented.
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtmb"
    bl_label = "Mat: Motion Blur"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "use_motion_blur", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        props = scene.eevee

        layout.active = props.use_motion_blur
        col = layout.column()
        col.prop(props, "motion_blur_samples")
        col.prop(props, "motion_blur_shutter")


class UnifierPostProcessDOF(UnifierButtonsPanel, Panel):
    #The DOF system has been updated by Celement. 
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtdof"
    bl_label = "Mat: DOF"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "use_dof", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        props = scene.eevee

        layout.active = props.use_dof
        col = layout.column()
        col.prop(props, "bokeh_max_size")
        col.prop(props, "bokeh_threshold")


class UnifierPostProcessBloom(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtblm"
    bl_label = "Mat: Bloom"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "use_bloom", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.eevee

        layout.active = props.use_bloom
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
    bl_label = "Mat: Volume"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "use_volumetric", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.eevee

        layout.active = props.use_volumetric
        col = layout.column()
        sub = col.column(align=True)
        sub.prop(props, "volumetric_start")
        sub.prop(props, "volumetric_end")
        col.prop(props, "volumetric_tile_size")
        col.separator()
        col.prop(props, "volumetric_samples")
        sub.prop(props, "volumetric_sample_distribution")
        col.separator()
        col.prop(props, "use_volumetric_lights")

        sub = col.column()
        sub.active = props.use_volumetric_lights
        sub.prop(props, "volumetric_light_clamp", text="Light Clamping")
        col.separator()
        col.prop(props, "use_volumetric_shadows")
        sub = col.column()
        sub.active = props.use_volumetric_shadows
        sub.prop(props, "volumetric_shadow_samples", text="Shadow Samples")
        col.separator()
        col.prop(props, "use_volumetric_colored_transmittance")


class UnifierPostProcessSSS(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtsss"
    bl_label = "Mat: SSS"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "use_sss", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.eevee

        layout.active = props.use_sss

        col = layout.column()
        col.prop(props, "sss_samples")
        col.prop(props, "sss_jitter_threshold")
        col.prop(props, "use_sss_separate_albedo")


class UnifierPostProcessSSR(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtssr"
    bl_label = "Mat: SSR"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        props = scene.eevee
        self.layout.prop(props, "use_ssr", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.eevee

        col = layout.column()
        col.active = props.use_ssr
        col.prop(props, "use_ssr_refraction", text="Refraction")
        col.prop(props, "use_ssr_halfres")
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
    bl_label = "Mat: Shadows"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.eevee

        col = layout.column()
        col.prop(props, "shadow_method")
        col.prop(props, "shadow_cube_size")
        col.prop(props, "shadow_cascade_size")
        col.prop(props, "use_shadow_high_bitdepth")


class UnifierPostProcessSample(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtsam"
    bl_label = "Mat: Sampling"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.eevee

        col = layout.column()
        col.prop(props, "taa_samples")
        col.prop(props, "taa_render_samples")
        col.prop(props, "use_taa_reprojection")


class UnifierPostProcessGI(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtgi"
    bl_label = "Mat: GI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

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
    bl_label = "Mat: Film"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        rd = scene.render

        col = layout.column()
        col.prop(rd, "filter_size")
        col.prop(rd, "alpha_mode", text="Alpha")

class UnifierPostProcessHair(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rthar"
    bl_label = "Mat: Hair"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rd = scene.render

        row = layout.row()
        row.prop(rd, "hair_type", expand=True)

        layout.prop(rd, "hair_subdiv")

#Matcap settings
class UnifierMatcapSettings(UnifierButtonsPanel, Panel):
    #Hopefully there will be a matcap shading option in 3D view.
    #If not I may try adding this option myself.
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "mcset"
    bl_label = "Cap: Settings"
    bl_options = {'DEFAULT_CLOSED'}

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
class UnifierSolidShading(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "sdsha"
    bl_label = "Sol: Shading"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        

        view = context.space_data
        shading = view.shading

        col = layout.column()

        if shading.type in ('SOLID', 'TEXTURED', 'MATERIAL', 'RENDERED'):
            col.row().prop(shading, "light", expand=True)
            col.row().prop(shading, "color_type", expand=True)

            if shading.color_type == 'SINGLE':
                col.row().prop(shading, "single_color", text="")

            if shading.light == 'STUDIO':
                col.row().template_icon_view(shading, "studio_light")
                if shading.studio_light_orientation == 'WORLD':
                    col.row().prop(shading, "studiolight_rot_z")

                row = col.row()
                row.prop(shading, "show_specular_highlight")

            col.separator()

            row = col.row()
            row.prop(shading, "show_xray")

            row = col.row()
            row.active = not shading.show_xray
            row.prop(shading, "show_shadows")
            sub = row.row()
            sub.active = shading.show_shadows and not shading.show_xray
            sub.prop(shading, "shadow_intensity", text="")

            row = col.row()
            row.prop(shading, "show_object_outline")
            sub = row.row()
            sub.active = shading.show_object_outline
            sub.prop(shading, "object_outline_color", text="")

            layout.prop(scene.display, "light_direction", text="")
            layout.prop(scene.display, "shadow_shift")
            layout.prop(scene.display, "roughness")

#Debug Zone

#End Debug Zone

def draw_device(self, context):
    scene = context.scene
    layout = self.layout

def draw_pause(self, context):
    layout = self.layout
    scene = context.scene

def get_panels():
    exclude_panels = {
        'UnifierLampFalloff',
        'UnifierLampPreview',
        'UnifierLampSpot',
        'UnifierMaterialPreview',
        }

    panels = []
    return panels

#Textured Settings
    #TODO: Possibly split up the solid and textured shading options. Should be easy. Just not a huge priority.

#Renaming to "Unifier" is not necessary,
#but will ultimately lead to better organization.
classes = (
    #Lamp:
    UnifierLampPreview,
    UnifierLampLampRealTime,
    UnifierLampShadow,
    UnifierLampArea,
    UnifierLampSpot,
    UnifierLampFalloff,
    #Light Probe:
    UnifierLightProbeContext,
    UnifierLightProbeProbe,
    UnifierLightProbeParallax,
    UnifierLightProbeDisplay,
    #Material:
    UnifierMaterialPreview,
    UnifierMaterialContext,
    UnifierMaterialSurface,
    UnifierMaterialOptions,
    UnifierMaterialViewport,
    #Real-Time:
    UnifierRealTimeShading,
    #Post Process:
    UnifierPostProcessGTAO,
    UnifierPostProcessBlur,
    UnifierPostProcessDOF,
    UnifierPostProcessBloom,
    UnifierPostProcessVolume,
    UnifierPostProcessSSS,
    UnifierPostProcessSSR,
    UnifierPostProcessHair,
    UnifierPostProcessGI,
    UnifierPostProcessFilm,
    UnifierPostProcessShadow,
    UnifierPostProcessSample,
    #Solid:
    UnifierSolidShading,
    #Matcap:
    UnifierMatcapSettings,
    #Debug:
    #UnifierDebug,
)

#This section broke the addon. This could happen again. Just copy from end of raytracer's ui.py file.
def register():
    from bpy.utils import register_class

    bpy.types.RENDER_PT_context.append(draw_device)
    bpy.types.VIEW3D_HT_header.append(draw_pause)

    for panel in get_panels():
        panel.COMPAT_ENGINES.add('CYCLES')

    for cls in classes:
        register_class(cls)

#This section broke the addon. This could happen again. Just copy from end of raytracer's ui.py file.
def unregister():
    from bpy.utils import unregister_class

    bpy.types.RENDER_PT_context.remove(draw_device)
    bpy.types.VIEW3D_HT_header.remove(draw_pause)

    for panel in get_panels():
        if 'CYCLES' in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove('CYCLES')

    for cls in classes:
        unregister_class(cls)