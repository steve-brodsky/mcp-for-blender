// One-time 2D bake pass, not a combat material. Inputs and output are SDR sRGB values.
shader_type canvas_item;
render_mode unshaded, blend_disabled;

uniform sampler2D source_albedo : filter_nearest, repeat_disable;
uniform sampler2D paint_mask : filter_nearest, repeat_disable;
// Vector4 uniforms deliberately have no source_color hint: Python uses sRGB byte math.
uniform vec4 hull_srgb;
uniform vec4 detail_srgb;
uniform vec2 normalization;

void fragment() {
    vec4 source = texture(source_albedo, UV);
    vec2 weights = texture(paint_mask, UV).rg;
    float luminance = dot(source.rgb, vec3(0.2126, 0.7152, 0.0722));
    vec3 hull = min(vec3(1.0), hull_srgb.rgb * luminance / normalization.x);
    vec3 detail = min(vec3(1.0), detail_srgb.rgb * luminance / normalization.y);
    vec3 result = source.rgb * (1.0 - weights.r - weights.g) + hull * weights.r + detail * weights.g;
    COLOR = vec4(clamp(result, vec3(0.0), vec3(1.0)), source.a);
}
