#version 430

layout(local_size_x = 32, local_size_y = 32, local_size_z = 1) in;

layout (r32f) uniform image2D d_map;
layout (r32f) uniform image2D water_src;

uniform float dt = 0.25;
uniform float Ke = 0.3;
uniform float Kr = 0.1;

uniform bool use_water_src = false;

void main(void) {
	ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
	vec4 d = imageLoad(d_map, pos);

	float kr = Kr;
	
	if (use_water_src) {
		kr *= imageLoad(water_src, pos).x;
	}

	d.x = d.x * (1 - dt * Ke) + dt * kr;
	
	imageStore(d_map, pos, d);
}//main
