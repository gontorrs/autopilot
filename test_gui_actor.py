import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import pyautogui
import re

model_id = "microsoft/GUI-Actor-2B-Qwen2-VL"
model = Qwen2VLForConditionalGeneration.from_pretrained(
    model_id, torch_dtype=torch.bfloat16, device_map="auto", trust_remote_code=True
)
processor = AutoProcessor.from_pretrained(model_id)

def localizar_icono_1000():
    screen_w, screen_h = pyautogui.size()
    
    pyautogui.moveTo(0, 0)
    screenshot = pyautogui.screenshot()
    screenshot.save("capture.png")

    english_prompt = (
        "Treat the image as a coordinate grid from 0 to 1000 for both width and height. "
        "Find the File Explorer icon (yellow folder) on the taskbar. "
        "Provide the center point in the format [x, y] using the 1000x1000 scale. "
        "If not visible, return [-1, -1]."
    )

    messages = [{"role": "user", "content": [
        {
            "type": "image", 
            "image": "capture.png", 
            "min_pixels": 256*28*28, 
            "max_pixels": 1344*28*28
        },
        {"type": "text", "text": english_prompt}
    ]}]

    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, _ = process_vision_info(messages)
    inputs = processor(text=[text], images=image_inputs, return_tensors="pt").to("cuda")
    
    print("Analizando con escala 1000x1000...")
    generated_ids = model.generate(**inputs, max_new_tokens=64)
    output = processor.batch_decode(generated_ids[:, inputs.input_ids.shape[1]:], skip_special_tokens=True)[0]

    print(f"Respuesta del modelo: {output}")

    if "-1" in output:
        return [-1, -1]

    match = re.search(r"\[(\d+),\s*(\d+)\]", output)
    if match:
        x_norm = int(match.group(1))
        y_norm = int(match.group(2))
        
        x_real = int((x_norm * screen_w) / 1000)
        y_real = int((y_norm * screen_h) / 1000)
        
        return [x_real, y_real]

    return [-1, -1]

if __name__ == "__main__":
    coords = localizar_icono_1000()
    if coords != [-1, -1]:
        print(f"Coordenadas reescaladas para tu monitor: {coords}")
        pyautogui.moveTo(coords[0], coords[1], duration=1.2)
    else:
        print("El modelo no devolvió coordenadas válidas.")