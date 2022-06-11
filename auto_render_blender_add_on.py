bl_info = {
	"name": "Auto Render PNGs",
	"blender": (2,80,0),
	"category": "Render",
}

import bpy
from os.path import join

CAMERA_FRONT = "Front"
CAMERA_BACK = "Back"
CAMERA_LEFT = "Left"
CAMERA_RIGHT = "Right"

CHARACTER_NAME = "character_test"

ROOT_OUTPUT_FOLDER = "C:/tmp/"


TOTAL_FRAMES = 5 #(0~4)


BATTLE_ANIMATION_ACTIONS = ["atk", "be_hit", "die", "idle", "skill"]
MOVE_ANIMATION_ACTION = "run"

class AutoRenderPNGs(bpy.types.Operator):
	"""docstring for AutoRenderPNGs"""
	bl_idname = "object.render_pngs"
	bl_label = "Auto Render PNGs"
	bl_options = {"REGISTER", "UNDO"}

	root_folder: bpy.props.StringProperty(name="Root Folder", default="C:/tmp/", maxlen=128)
	name: bpy.props.StringProperty(name="Animate Name", default="AnimationDefault",maxlen=32)
	frames: bpy.props.IntProperty(name="Total Frames", default=TOTAL_FRAMES, min=1, max=16)

	def execute(self, context):
		auto_get_foucs()
		# init param
		global CHARACTER_NAME, ROOT_OUTPUT_FOLDER, TOTAL_FRAMES
		CHARACTER_NAME = self.name
		ROOT_OUTPUT_FOLDER = self.root_folder
		TOTAL_FRAMES = self.frames
		# render
		generate_battle()
		generate_move()
		
		return {'FINISHED'}

def auto_get_foucs():
	objs = bpy.context.scene.objects
	for obj in objs:
		if obj.type == "ARMATURE":
			bpy.context.view_layer.objects.active = obj
			break

def render_animate(middle_path):
	CURRENT_SCENE = bpy.context.scene
	current_folder = ROOT_OUTPUT_FOLDER + middle_path
	for f in range(TOTAL_FRAMES):
		f += 1
		CURRENT_SCENE.frame_set(f)
		if f < 10:
			file_name = "000{}".format(f)
		else:
			file_name = "00{}{}".format(1, f%10)
		# file_name += scene.render.file_extension
		file_name += ".png"
		bpy.context.scene.render.filepath = join(current_folder, file_name)
		bpy.ops.render.render(write_still = True)


def generate_battle():
	''' left '''
	target_camera = bpy.data.objects[CAMERA_RIGHT]
	bpy.context.scene.camera = target_camera
	for action in BATTLE_ANIMATION_ACTIONS:
		temp_battle = CHARACTER_NAME + "/battle/right/" + action + "/"
		bpy.context.object.animation_data.action = bpy.data.actions.get(action)
		render_animate(temp_battle)
	''' right '''
	target_camera = bpy.data.objects[CAMERA_LEFT]
	bpy.context.scene.camera = target_camera
	for action in BATTLE_ANIMATION_ACTIONS:
		temp_battle = CHARACTER_NAME + "/battle/left/l_" + action + "/"
		bpy.context.object.animation_data.action = bpy.data.actions.get(action)
		render_animate(temp_battle)


def generate_move():
	bpy.context.object.animation_data.action = bpy.data.actions.get(MOVE_ANIMATION_ACTION)
	
	target_camera = bpy.data.objects[CAMERA_FRONT]
	bpy.context.scene.camera = target_camera
	temp_battle = CHARACTER_NAME + "/move/down/"
	render_animate(temp_battle)

	target_camera = bpy.data.objects[CAMERA_BACK]
	bpy.context.scene.camera = target_camera
	temp_battle = CHARACTER_NAME + "/move/up/"
	render_animate(temp_battle)

	target_camera = bpy.data.objects[CAMERA_LEFT]
	bpy.context.scene.camera = target_camera
	temp_battle = CHARACTER_NAME + "/move/left/"
	render_animate(temp_battle)

	target_camera = bpy.data.objects[CAMERA_RIGHT]
	bpy.context.scene.camera = target_camera
	temp_battle = CHARACTER_NAME + "/move/right/"
	render_animate(temp_battle)

	target_camera = bpy.data.objects[CAMERA_FRONT]
	bpy.context.scene.camera = target_camera
	bpy.context.object.animation_data.action = bpy.data.actions.get("idle")
	temp_battle = CHARACTER_NAME + "/move/down_idle/"
	render_animate(temp_battle)

def menu_func(self, context):
	self.layout.operator(AutoRenderPNGs.bl_idname)

addon_keymaps = []

def register():
	bpy.utils.register_class(AutoRenderPNGs)
	bpy.types.VIEW3D_MT_object.append(menu_func)

	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon
	if kc:
		km = wm.keyconfigs.addon.keymaps.new(name="Object Mode", space_type="EMPTY")
		kmi = km.keymap_items.new(AutoRenderPNGs.bl_idname, "R", "PRESS", ctrl=True, shift=True)
		kmi.properties.frames = TOTAL_FRAMES
		addon_keymaps.append((km, kmi))


def unregister():
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()

	bpy.utils.unregister_class(AutoRenderPNGs)
	bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
	register()
