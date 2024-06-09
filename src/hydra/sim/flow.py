"""Module responsible for flow simulation."""

from Hydra.sim import heightmap
from Hydra.utils import texture, model
from Hydra import common
import bpy.types
import math
from datetime import datetime

# --------------------------------------------------------- Flow

def generate_flow(obj: bpy.types.Image | bpy.types.Object)->bpy.types.Image:
	"""Simulates a flow map on the specified entity.
	
	:param obj: Object or image to simulate on.
	:type obj: :class:`bpy.types.Object` or :class:`bpy.types.Image`
	:return: Flow map.
	:rtype: :class:`bpy.types.Image`"""
	data = common.data
	hyd = obj.hydra_erosion
	if not data.has_map(hyd.map_base):
		heightmap.prepare_heightmap(obj)

	ctx = data.context
	
	size = hyd.get_size()

	if data.has_map(hyd.map_result):
		height = data.get_map(hyd.map_result).texture
	else:
		height = data.get_map(hyd.map_source).texture
	
	amount = texture.create_texture(size)

	subdiv = 8

	prog = data.shaders["flow"]
	height.bind_to_image(1, read=True, write=False)
	prog["height_sampler"].value = 1
	amount.bind_to_image(2, read=True, write=True)
	prog["flow"].value = 2
	prog["squareSize"] = subdiv

	# map to aesthetic range 0.0003-0.2
	prog["strength"] = 0.2*math.exp(-6.61*(hyd.flow_contrast / 100))

	prog["acceleration"] = hyd.part_acceleration / 100
	prog["lifetime"] = hyd.part_lifetime
	prog["drag"] = 1-(hyd.part_drag / 100)	# multiplicative factor

	groups_x = math.ceil(size[0]/(subdiv * 32))
	groups_y = math.ceil(size[1]/(subdiv * 32))

	time = datetime.now()
	for y in range(subdiv):
		for x in range(subdiv):
			prog["off"] = (x,y)
			prog.run(group_x=groups_x, group_y=groups_y)
	ctx.finish()

	final_amount = texture.create_texture(amount.size)
	final_amount.bind_to_image(3, read=True, write=True)
	prog = data.shaders["plug"]
	prog["inMap"].value = 2
	prog["outMap"].value = 3

	groups_x = math.ceil(size[0]/32)
	groups_y = math.ceil(size[1]/32)

	prog.run(group_x=size[0], group_y=size[1])

	print((datetime.now() - time).total_seconds())

	img_name = f"HYD_{obj.name}_Flow"
	ret, _ = texture.write_image(img_name, final_amount)
	amount.release()
	final_amount.release()
	
	return ret
