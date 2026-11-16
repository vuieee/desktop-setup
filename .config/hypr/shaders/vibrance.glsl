#version 300 es
precision highp float;
in vec2 v_texcoord;
uniform sampler2D tex;
out vec4 fragColor;
void main() {
    vec4 pix = texture(tex, v_texcoord);
    float luma = dot(pix.rgb, vec3(0.2126, 0.7152, 0.0722));
    float max_c = max(pix.r, max(pix.g, pix.b));
    float min_c = min(pix.r, min(pix.g, pix.b));
    float sat = max_c - min_c;
    float vibrance = 0.45;
    vec3 boosted = mix(vec3(luma), pix.rgb, 1.0 + vibrance * (1.0 - sat));
    fragColor = vec4(clamp(boosted, 0.0, 1.0), pix.a);
}
