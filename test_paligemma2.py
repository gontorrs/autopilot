import torch
import pyautogui
pyautogui.FAILSAFE = False
from transformers import PaliGemmaProcessor, PaliGemmaForConditionalGeneration
import re

model_id = "google/paligemma2-3b-mix-448"
model = PaliGemmaForConditionalGeneration.from_pretrained(model_id, dtype=torch.bfloat16, device_map="auto").eval()
processor = PaliGemmaProcessor.from_pretrained(model_id)

def detect(prompt="detect yellow folder icon on taskbar"):

    screen_w, screen_h = pyautogui.size()
    screenshot = pyautogui.screenshot()
    
    inputs = processor(text=prompt, images=screenshot, return_tensors="pt").to(model.device, torch.bfloat16)
    out = model.generate(**inputs, max_new_tokens=64)
    tokens = processor.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=False)
    
    locs = re.findall(r"<loc(\d{4})>", tokens)
    if len(locs) < 4: return [-1, -1]
    
    coords = [int(l)/1024 for l in locs[:4]]
    if (coords[2]-coords[0]) > 0.8 or (coords[3]-coords[1]) > 0.8: return [-1, -1]
    
    x = int(((coords[1]+coords[3])/2) * screen_w)
    y = int(((coords[0]+coords[2])/2) * screen_h)
    return [x, y]

if __name__ == "__main__":
    coords = detect()
    if coords != [-1, -1]:
        pyautogui.moveTo(*coords, duration=0.5)
        pyautogui.click()