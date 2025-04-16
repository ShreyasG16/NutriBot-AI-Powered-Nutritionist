import base64

def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

base64_string = encode_image("neuron5.png")

with open("neuron5_base64.txt", "w") as f:
    f.write(f"data:image/png;base64,{base64_string}")

print("Base64 string saved to neuron5_base64.txt")
