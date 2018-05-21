bl_info = {"name": "Unifier0.2", "category": "All"}

import bpy
from bpy_extras.node_utils import (
        find_node_input,
        find_output_node,
        )

from bpy.types import (
        Panel,
        Menu,
        Operator,
        UIList,
        )

class UnifierButtonsPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOL_PROPS"

#EEVEE settings
class RENDER_PT_eevee_ambient_occlusion(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtao"
    bl_label = "Real-Time: GTAO"
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


class RENDER_PT_eevee_motion_blur(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtmb"
    bl_label = "Real-Time: Motion Blur"
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


class RENDER_PT_eevee_depth_of_field(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtdof"
    bl_label = "Real-Time: DOF"
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


class RENDER_PT_eevee_bloom(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtblm"
    bl_label = "Real-Time: Bloom"
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


class RENDER_PT_eevee_volumetric(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtvol"
    bl_label = "Real-Time: Volumetric"
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


class RENDER_PT_eevee_subsurface_scattering(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtsss"
    bl_label = "Real-Time: SSS"
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


class RENDER_PT_eevee_screen_space_reflections(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtssr"
    bl_label = "Real-Time: SSR"
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


class RENDER_PT_eevee_shadows(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtsha"
    bl_label = "Real-Time: Shadows"
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


class RENDER_PT_eevee_sampling(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtsam"
    bl_label = "Real-Time: Sampling"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.eevee

        col = layout.column()
        col.prop(props, "taa_samples")
        col.prop(props, "taa_render_samples")
        col.prop(props, "taa_reprojection")


class RENDER_PT_eevee_indirect_lighting(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtgi"
    bl_label = "Real-Time: GI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.eevee

        col = layout.column()
        col.prop(props, "gi_diffuse_bounces")
        col.prop(props, "gi_cubemap_resolution")
        col.prop(props, "gi_visibility_resolution")


class RENDER_PT_eevee_film(UnifierButtonsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Unifier"
    bl_idname = "rtfil"
    bl_label = "Real-Time: Film"
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

#Clay settings
class RENDER_PT_clay_settings(UnifierButtonsPanel, Panel):
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

#WorkBench settings
class SCENE_PT_viewport_display(UnifierButtonsPanel, Panel):
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

    if context.engine == 'CYCLES':
        from . import engine
        cscene = scene.cycles

        split = layout.split(percentage=1 / 3)
        split.label("Feature Set:")
        split.prop(cscene, "feature_set", text="")

        split = layout.split(percentage=1 / 3)
        split.label("Device:")
        row = split.row()
        row.active = show_device_active(context)
        row.prop(cscene, "device", text="")

        if engine.with_osl() and use_cpu(context):
            layout.prop(cscene, "shading_system")


def draw_pause(self, context):
    layout = self.layout
    scene = context.scene

    if context.engine == "CYCLES":
        view = context.space_data

        cscene = scene.cycles
        layout.prop(cscene, "preview_pause", icon="PAUSE", text="")


def get_panels():
    exclude_panels = {
        'DATA_PT_area',
        'DATA_PT_camera_dof',
        'DATA_PT_falloff_curve',
        'DATA_PT_lamp',
        'DATA_PT_preview',
        'DATA_PT_spot',
        'MATERIAL_PT_context_material',
        'MATERIAL_PT_preview',
        'VIEWLAYER_PT_filter',
        'VIEWLAYER_PT_layer_passes',
        'RENDER_PT_post_processing',
        'SCENE_PT_simplify',
        }

    panels = []
    for panel in bpy.types.Panel.__subclasses__():
        if hasattr(panel, 'COMPAT_ENGINES') and 'BLENDER_RENDER' in panel.COMPAT_ENGINES:
            if panel.__name__ not in exclude_panels:
                panels.append(panel)

    return panels


classes = (
    RENDER_PT_eevee_ambient_occlusion,
    RENDER_PT_eevee_motion_blur,
    RENDER_PT_eevee_depth_of_field,
    RENDER_PT_eevee_bloom,
    RENDER_PT_eevee_volumetric,
    RENDER_PT_eevee_subsurface_scattering,
    RENDER_PT_eevee_screen_space_reflections,
    RENDER_PT_eevee_shadows,
    RENDER_PT_eevee_sampling,
    RENDER_PT_eevee_indirect_lighting,
    RENDER_PT_eevee_film,
    SCENE_PT_viewport_display,
    RENDER_PT_clay_settings,
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
