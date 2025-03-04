import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from urllib.parse import urlparse
from io import BytesIO
import requests
from PIL import Image, ImageDraw
url = ''
load_dotenv('.env')
client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen2.5-vl-72b-instruct",  # 此处以qwen-vl-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=[{"role": "user","content": [
            {"type": "text","text": "定位这张图片中的邮票，以左上角为原点，将邮票的四角像素的坐标输出，适当扩大框选范围。注意，邮票可能是倾斜的或者非矩形，此时输出你认为的四角，不一定要水平。不同邮票的坐标之间没有关联。如果有多个邮票，那么分别输出各个邮票，并放置到json数组中，无需其他说明，且不需要使用Markdown格式，例如：[{\"1\":\"[654, 37]\",\"2\":\"[982, 38]\",\"3\":\"[978, 178]\",\"4\":\"[657, 176]\"},{\"1\":\"[1329, 113]\",\"2\":\"[1442, 124]\",\"3\":\"[1432, 230]\",\"4\":\"[1327, 234]\"}]"},
            {"type": "image_url",
             "image_url": {"url": url}}
            ]}]
    )
pdata = json.loads(completion.model_dump_json())
coords_src = pdata["choices"][0]["message"]["content"]

# 下载图片

response = requests.get(url, stream=True)
response.raise_for_status()  # 确保请求成功

# 打开图片并转换为RGBA模式
img = Image.open(BytesIO(response.content)).convert('RGBA')

# 解析相对坐标
#coords_src = '[{"1":"[0.512, 0.000]","2":"[0.678, 0.000]","3":"[0.678, 0.204]","4":"[0.512, 0.204]"},{"1":"[0.690, 0.000]","2":"[0.846, 0.000]","3":"[0.846, 0.136]","4":"[0.690, 0.136]"},{"1":"[0.858, 0.000]","2":"[1.000, 0.000]","3":"[1.000, 0.136]","4":"[0.858, 0.136]"}]'
coords_data = json.loads(coords_src)

for i in range(0, len(coords_data)):
    points = []
    for key in ['1', '2', '3', '4']:
        coord_str = coords_data[i][key]
        x_str, y_str = coord_str.strip('[]').split(',')
        x = float(x_str.strip())
        y = float(y_str.strip())
        points.append((x, y))
        # 转换为绝对坐标
    abs_points = [(x, y) for (x, y) in points]
    # 创建透明图层绘制半透明四边形
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fill_color = (255, 0, 0, 128)  # 红色半透明（RGBA）
    draw.polygon(abs_points, fill=fill_color)
    # 合并图层并保存55(
    img = Image.alpha_composite(img, overlay)
parsed_url = urlparse(url)
path = parsed_url.path
filename, ext =  os.path.splitext(os.path.basename(path))
img.save('output_abs/' + filename + '.png', 'PNG')

print("处理完成，图片已保存")