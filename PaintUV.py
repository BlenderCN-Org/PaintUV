# bl_info
bl_info = {
	"name": "Paint UV islands",
	"author": "Nexus Studio",
	"version": (0,0,4),
	"blender": (2,79),
	"location": "T > Nexus Tools, Edit mesh > U > Unwrap and paint uv",
	"description": "Tools",
	"warning": "",
	"wiki_url": "None",
	"category": "User"
}

import bpy
from random import uniform
from bpy.props import BoolProperty
# import time

def MenuFuncUnwrap(self, context):
	self.layout.separator()
	self.layout.operator(MenuUnwrapOperator.bl_idname, text="Unwrap and paint uv", icon="VPAINT_HLT")

def SetRandomBrushColor():
	"""Generate random color to brush"""
	r = uniform(0.0, 1.0)
	g = uniform(0.0, 1.0)
	b = uniform(0.0, 1.0)
	bpy.data.brushes["Draw"].color = (r, g, b)

def IsWhiteVertex(color_map, index):
	""""Return True if vertex color equal white color (1.0, 1.0, 1.0)"""
	col = color_map.data[index].color
	return col[0] == 1.0 and col[1] == 1.0 and col[2] == 1.0

def CheckColorMapName(color_maps, FindName):
	for color_map in color_maps:
		if color_map.name == FindName:
			return True

	return False

def FindAndPaint():
	my_object = bpy.context.active_object.data

	my_object.use_paint_mask = True

	bpy.ops.object.mode_set( mode = 'EDIT' )
	bpy.ops.mesh.select_all( action = 'DESELECT' )
	bpy.ops.object.mode_set( mode = 'OBJECT' )

	# if not color map created else remove active color map and created new
	if not CheckColorMapName(my_object.vertex_colors, 'ISLANDS_PAINT'):
		color_map = my_object.vertex_colors.new()
		color_map.name = 'ISLANDS_PAINT'
	else:
		my_object.vertex_colors['ISLANDS_PAINT'].active = True
		bpy.ops.mesh.vertex_color_remove()
		color_map = my_object.vertex_colors.new()
		color_map.name = 'ISLANDS_PAINT'

	color_map = my_object.vertex_colors['ISLANDS_PAINT']
	color_map.active = True
	polygons = my_object.polygons

	index = 0
	for poly in polygons:
		for idx in poly.loop_indices:
			if IsWhiteVertex(color_map, index):
				bpy.ops.object.mode_set( mode = 'VERTEX_PAINT' )
				bpy.ops.paint.face_select_all( action = 'DESELECT' )
				poly.select = True
				bpy.ops.paint.face_select_linked()
				SetRandomBrushColor()
				bpy.ops.paint.vertex_color_set()
			index += 1

	bpy.ops.object.mode_set( mode = 'EDIT' )
	bpy.ops.mesh.select_all( action = 'DESELECT' )

class PaintUVPanel(bpy.types.Panel):
	"""Creates a Panel in the view3d context of the tools panel (key "T")"""
	bl_label = "Paint UV"
	bl_idname = "paintuvid"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "Nexus Tools"
	bl_context = "objectmode"

	def draw(self, context):
		layout = self.layout
		obj = context.object
		scene = context.scene

		row = layout.row()
		row.prop(scene, "seam_from_islands")
		row = layout.row()
		row.operator("object.paint_uv", text="Paint by UV")

class PaintUVOperator(bpy.types.Operator):
	"""Paint all UV islands"""
	bl_label = "Paint UV"
	bl_idname = "object.paint_uv"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT"

	def execute(self, context):
		temp_mode = context.mode
		if context.scene.seam_from_islands:
			bpy.ops.object.mode_set( mode = 'EDIT' )
			bpy.ops.uv.seams_from_islands()

		FindAndPaint()
		bpy.ops.object.mode_set( mode = temp_mode )

		return {'FINISHED'}

class MenuUnwrapOperator(bpy.types.Operator):
	"""Unwrap and paint all UV islands"""
	bl_label = "Unwrap and paint UV"
	bl_idname = "uv.unwrap_paint_uv"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == "EDIT_MESH"

	def execute(self, context):
		bpy.ops.uv.unwrap()
		FindAndPaint()

		return {'FINISHED'}

class VIEW3D_mark_seam_paint_uv(bpy.types.Operator):
	"""Create mark seam and paint UV vertex color"""
	bl_idname = "view3d.mark_seam_paint_uv"
	bl_label = "Mark Seam & Paint UV"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'

	def execute(self, context):
		bpy.ops.mesh.mark_seam(clear=False)
		FindAndPaint()
		bpy.ops.object.mode_set( mode = 'EDIT' )

		return {'FINISHED'}

class VIEW3D_paint_uv_menu(bpy.types.Menu):
	bl_label = "Paint UV"

	def draw(self, context):
		layout = self.layout
		sd = context.space_data
		layout.operator_context = 'INVOKE_REGION_WIN'
		layout.operator("view3d.mark_seam_paint_uv", text="Mark seam & Paint UV")
		layout.operator("object.paint_uv", text="Repaint UV")
		#layout.menu(align_submenu.bl_idname, text="Align by")

addon_keymaps = []
keymapsList = [
	{
		'name_view': "3D View",
		'space_type': "VIEW_3D",
		'prop_name': "VIEW3D_paint_uv_menu"
	}
	# },
	# {
	# 	'name_view': "Image",
	# 	'space_type': "IMAGE_EDITOR",
	# 	'prop_name': "uv_menu"
	# },
	# {
	# 	'name_view': "Graph Editor",
	# 	'space_type': "GRAPH_EDITOR",
	# 	'prop_name': "graph_menu"
	# },
	# {
	# 	'name_view': "Node Editor",
	# 	'space_type': "NODE_EDITOR",
	# 	'prop_name': "node_menu"
	# }
]

def register():
	bpy.types.Scene.seam_from_islands = BoolProperty(
		name = "Seam From Islands",
		default = False
	)
	bpy.utils.register_class(VIEW3D_mark_seam_paint_uv)
	bpy.utils.register_class(VIEW3D_paint_uv_menu)
	bpy.utils.register_class(PaintUVPanel)
	bpy.utils.register_class(PaintUVOperator)
	bpy.utils.register_class(MenuUnwrapOperator)
	bpy.types.VIEW3D_MT_uv_map.append(MenuFuncUnwrap)
	# VIEW3D_paint_uv_menu

	kc = bpy.context.window_manager.keyconfigs.addon
	if kc:
		for keym in keymapsList:
			km = kc.keymaps.new(name=keym['name_view'], space_type=keym['space_type'])
			kmi = km.keymap_items.new('wm.call_menu', 'E', 'PRESS', alt=True, ctrl=True)
			kmi.properties.name = keym['prop_name']
			addon_keymaps.append(km)

def unregister():
	bpy.utils.unregister_class(VIEW3D_mark_seam_paint_uv)
	bpy.utils.unregister_class(VIEW3D_paint_uv_menu)
	bpy.utils.unregister_class(PaintUVPanel)
	bpy.utils.unregister_class(PaintUVOperator)
	bpy.utils.unregister_class(MenuUnwrapOperator)
	bpy.types.VIEW3D_MT_uv_map.remove(MenuFuncUnwrap)
	del bpy.types.Scene.seam_from_islands

	wm = bpy.context.window_manager
	if wm.keyconfigs.addon:
		for km in addon_keymaps:
			for kmi in km.keymap_items:
				km.keymap_items.remove(kmi)
	addon_keymaps.clear()

if __name__ == "__main__":
	register()
