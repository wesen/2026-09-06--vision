## Cell 0 (markdown)

### Spatial Understanding with Qwen3-VL

This notebook demonstrates Qwen3-VL‘s ability to do more than just see objects. It understands their spatial layout, perceives what actions are possible ('affordances'), and uses this knowledge to reason like an embodied agent, paving the way for smarter interaction with the physical world.

## Cell 1 (markdown)

Prepare the environment

## Cell 2 (code)

!pip install git+https://github.com/huggingface/transformers
!pip install qwen-vl-utils
!pip install openai
!pip install dashscope
!pip install decord

## Cell 3 (markdown)

#### \[Setup\]

Load visualization utils.

## Cell 4 (code)

# @title Plotting Util

# Get Noto JP font to display janapese characters
!apt-get install fonts-noto-cjk  # For Noto Sans CJK JP

#!apt-get install fonts-source-han-sans-jp # For Source Han Sans (Japanese)

import json
import random
import io
import ast
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageColor
import xml.etree.ElementTree as ET

additional_colors = [colorname for (colorname, colorcode) in ImageColor.colormap.items()]

def decode_json_points(text: str):
    """Parse coordinate points from text format"""
    try:
        # 清理markdown标记
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        
        # 解析JSON
        data = json.loads(text)
        points = []
        labels = []
        
        for item in data:
            if "point_2d" in item:
                x, y = item["point_2d"]
                points.append([x, y])
                
                # 获取label，如果没有则使用默认值
                label = item.get("label", f"point_{len(points)}")
                labels.append(label)
        
        return points, labels
        
    except Exception as e:
        print(f"Error: {e}")
        return [], []
        

def plot_points(im, text):
  img = im
  width, height = img.size
  draw = ImageDraw.Draw(img)
  colors = [
    'red', 'green', 'blue', 'yellow', 'orange', 'pink', 'purple', 'brown', 'gray',
    'beige', 'turquoise', 'cyan', 'magenta', 'lime', 'navy', 'maroon', 'teal',
    'olive', 'coral', 'lavender', 'violet', 'gold', 'silver',
  ] + additional_colors

  points, descriptions = decode_json_points(text)
  print("Parsed points: ", points)
  print("Parsed descriptions: ", descriptions)
  if points is None or len(points) == 0:
    img.show()
    return

  font = ImageFont.truetype("NotoSansCJK-Regular.ttc", size=14)

  for i, point in enumerate(points):
    color = colors[i % len(colors)]
    abs_x1 = int(point[0])/1000 * width
    abs_y1 = int(point[1])/1000 * height
    radius = 2
    draw.ellipse([(abs_x1 - radius, abs_y1 - radius), (abs_x1 + radius, abs_y1 + radius)], fill=color)
    draw.text((abs_x1 - 20, abs_y1 + 6), descriptions[i], fill=color, font=font)
  
  img.show()

## Cell 5 (markdown)

inference function with API

## Cell 6 (code)

from openai import OpenAI
import os
import base64
#  base 64 编码格式
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def inference_with_api(image_path, prompt, model_id="qwen3-vl-235b-a22b-instruct"):
    """API-based inference using custom endpoint"""
    base64_image = encode_image(image_path)
    client = OpenAI(
        api_key=os.getenv('DASHSCOPE_API_KEY'),
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )

    image_format = image_path.split(".")[-1].lower()
    if image_format == 'jpg':
        image_format = 'jpeg'
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    # Pass in BASE64 image data. Note that the image format (i.e., image/{format}) must match the Content Type in the list of supported images. "f" is the method for string formatting.
                    # PNG image:  f"data:image/png;base64,{base64_image}"
                    # JPEG image: f"data:image/jpeg;base64,{base64_image}"
                    # WEBP image: f"data:image/webp;base64,{base64_image}"
                    "image_url": {"url": f"data:image/{image_format};base64,{base64_image}"},
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]
    completion = client.chat.completions.create(
        model = model_id,
        messages = messages,
       
    )
    return completion.choices[0].message.content

## Cell 7 (markdown)

#### 1. Understand the Spatial Relationship Between Objects
After identifying objects within an image, a more complex task is to understand their relative spatial positions.

Furthermore, based on this capability, we can prompt the model with specific questions that require spatial reasoning, such as "Is object A above or below object B?" or "Please describe the object closest to object C."

## Cell 8 (code)

image_path = "./assets/spatial_understanding/spatio_case1.jpg"
prompt = "Which object, in relation to your current position, holds the farthest placement in the image?\nAnswer options:\nA.chair\nB.plant\nC.window\nD.tv stand."
response = inference_with_api(image_path, prompt)

print("Prompt:\n"+prompt)
print("\nAnswer:\n"+response)
img = Image.open(image_path)
img.show()

## Cell 9 (markdown)

#### 2. Perceive Object Affordances

Beyond identifying objects, a more granular task is to perceive affordances at a point or region level. This requires a model to understand what actions are enabled by specific parts of an object (e.g., a handle is 'graspable') or even by empty space within the scene (e.g., an open area is 'placeable').

Furthermore, we can prompt the model with questions that require this fine-grained understanding, such as "Identify a graspable point on the cup's handle" or "Show me an area on the floor where I can place this box."

## Cell 10 (markdown)

For spatial pointing tasks, Qwen3-VL now support these formats:

* point-format: JSON

`{"point_2d": [x, y], "label": "object name/description"}`

## Cell 11 (code)

image_path = "./assets/spatial_understanding/spatio_case2_aff.png"
prompt = "Locate the free space on the white table on the right in this image. Output the point coordinates in JSON format."
response = inference_with_api(image_path, prompt)

print("Prompt:\n"+prompt)
print("\nAnswer:\n"+response)
plot_points(Image.open(image_path), response)

## Cell 12 (code)

image_path = "./assets/spatial_understanding/spatio_case2_aff2.png"
prompt = "Can the speaker fit behind the guitar?"
response = inference_with_api(image_path, prompt)

print("Prompt:\n"+prompt)
print("\nAnswer:\n"+response)
img = Image.open(image_path)
img = img.resize((img.width//4, img.height//4))
img.show()

## Cell 13 (markdown)

#### 3. Integrate Spatial Reasoning and Action Planning

This advanced task integrates the understanding of spatial relationships and affordances. The model must synthesize these capabilities to select the correct action that achieves a goal, effectively reasoning like an embodied agent.

## Cell 14 (code)

image_path = "./assets/spatial_understanding/spatio_case2_plan.png"
prompt = "What color arrow should the robot follow to move the apple in between the green can and the orange? Choices: A. Red. B. Blue. C. Green. D. Orange."
response = inference_with_api(image_path, prompt)

print("Prompt:\n"+prompt)
print("\nAnswer:\n"+response)
img = Image.open(image_path)
img.show()

## Cell 15 (code)

image_path = "./assets/spatial_understanding/spatio_case2_plan2.png"
prompt = "Which motion can help change the coffee pod? Choices: A. A. B. B. C. C. D. D."
response = inference_with_api(image_path, prompt)

print("Prompt:\n"+prompt)
print("\nAnswer:\n"+response)
img = Image.open(image_path)
img.show()

## Cell 16 (code)

import os
import math
import hashlib
import requests

from IPython.display import Markdown, display
import numpy as np
from PIL import Image
import decord
from decord import VideoReader, cpu


def download_video(url, dest_path):
    response = requests.get(url, stream=True)
    with open(dest_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8096):
            f.write(chunk)
    print(f"Video downloaded to {dest_path}")


def get_video_frames(video_path, num_frames=128, cache_dir='./assets/spatial_understanding/'):
    os.makedirs(cache_dir, exist_ok=True)

    video_hash = hashlib.md5(video_path.encode('utf-8')).hexdigest()
    if video_path.startswith('http://') or video_path.startswith('https://'):
        video_file_path = os.path.join(cache_dir, f'{video_hash}.mp4')
        if not os.path.exists(video_file_path):
            download_video(video_path, video_file_path)
    else:
        video_file_path = video_path

    frames_cache_file = os.path.join(cache_dir, f'{video_hash}_{num_frames}_frames.npy')
    timestamps_cache_file = os.path.join(cache_dir, f'{video_hash}_{num_frames}_timestamps.npy')

    if os.path.exists(frames_cache_file) and os.path.exists(timestamps_cache_file):
        frames = np.load(frames_cache_file)
        timestamps = np.load(timestamps_cache_file)
        return video_file_path, frames, timestamps

    vr = VideoReader(video_file_path, ctx=cpu(0))
    total_frames = len(vr)

    indices = np.linspace(0, total_frames - 1, num=num_frames, dtype=int)
    frames = vr.get_batch(indices).asnumpy()
    timestamps = np.array([vr.get_frame_timestamp(idx) for idx in indices])

    np.save(frames_cache_file, frames)
    np.save(timestamps_cache_file, timestamps)
    
    return video_file_path, frames, timestamps


def create_image_grid(images, num_columns=8):
    pil_images = [Image.fromarray(image) for image in images]
    num_rows = math.ceil(len(images) / num_columns)

    img_width, img_height = pil_images[0].size
    grid_width = num_columns * img_width
    grid_height = num_rows * img_height
    grid_image = Image.new('RGB', (grid_width, grid_height))

    for idx, image in enumerate(pil_images):
        row_idx = idx // num_columns
        col_idx = idx % num_columns
        position = (col_idx * img_width, row_idx * img_height)
        grid_image.paste(image, position)

    return grid_image


## Cell 17 (code)

import dashscope
def inference_video_with_dashscope_api(video, prompt, model_id, video_type='url'):
    if video_type=='url':
        video_msg = {"video": video, 'fps': 2}
    elif video_type=='frame_list':
        video_msg = {"video": video['frame_list'], 'fps': video['fps'] }
    
    messages = [
        {
            "role": "user",
            "content": [
                video_msg,
                {"text": prompt},
            ]
        }
    ]
    completion = dashscope.MultiModalConversation.call(
        api_key= os.getenv("DASHSCOPE_API_KEY"),
        model=model_id, 
        messages=messages
    )
    return completion["output"]["choices"][0]["message"].content[0]["text"]


## Cell 18 (code)

model_id = "qwen3-vl-235b-a22b-instruct"
video_url = "https://xxxxx/42446167.mp4"
prompt = "These are frames of a video.\nYou are a robot beginning at the bed facing the tv. You want to navigate to the toilet. You will perform the following actions (Note: for each [please fill in], choose either 'turn back,' 'turn left,' or 'turn right.'): 1. Go forward until the TV 2. [please fill in] 3. Go forward until the shower 4. [please fill in] 5. Go forward until the toilet. You have reached the final destination.\nOptions:\nA. Turn Back, Turn Left\nB. Turn Left, Turn Left\nC. Turn Left, Turn Right\nD. Turn Right, Turn Right"

video_path, frames, timestamps = get_video_frames(video_url, num_frames=64)
image_grid = create_image_grid(frames, num_columns=8)

response = inference_video_with_dashscope_api(video_url, prompt=prompt, model_id=model_id)

print("Prompt:\n"+prompt)
print("\nAnswer:\n"+response)
display(image_grid.resize((640, 640)))

