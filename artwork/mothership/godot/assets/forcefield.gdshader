shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled;

uniform vec4 field_color : source_color = vec4(0.025, 0.35, 1.0, 1.0);
uniform float energy : hint_range(0.0, 3.0) = 1.0;
uniform float opacity : hint_range(0.0, 1.0) = 0.23;

void fragment() {
    vec2 p = UV * vec2(2.56, 1.0);
    vec2 cell = abs(fract(p * 38.0) - 0.5);
    float grid = smoothstep(0.45, 0.495, max(cell.x, cell.y));
    float edge = pow(1.0 - min(min(UV.x, 1.0 - UV.x) * 8.0,
                               min(UV.y, 1.0 - UV.y) * 8.0), 3.0);
    edge = clamp(edge, 0.0, 1.0);
    float wave = sin(UV.y * 90.0 - TIME * 2.5 + sin(UV.x * 12.0 + TIME) * 0.9);
    float scan = pow(0.5 + 0.5 * wave, 16.0);
    float pulse = 0.94 + 0.06 * sin(TIME * 1.7);
    ALBEDO = field_color.rgb;
    EMISSION = field_color.rgb * (0.4 + edge * 1.6 + scan * 0.6) * energy;
    ALPHA = clamp((opacity + grid * 0.10 + edge * 0.38 + scan * 0.09) * pulse * energy, 0.0, 0.9);
}
