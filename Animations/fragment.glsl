#version 330 core
out vec4 FragColor;

uniform vec3 fogColor;

void main()
{
    FragColor = vec4(fogColor, 1.0);
}