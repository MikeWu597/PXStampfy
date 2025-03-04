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
            {"type": "text","text": "请用bounding box json格式输出所有的邮票位置，图片宽为1280像素，Label设置为这张邮票所属国家名称，按照ISO 3166-1二位字母代码大写输出。"},
            {"type": "image_url",
             "image_url": {"url": url}}
            ]}]
    )
print(completion.model_dump_json())
s = json.loads(completion.model_dump_json())["choices"][0]["message"]["content"]

# 步骤1：处理转义字符（将 \n、\t、\" 等转换为实际字符）
unescaped = s.encode("utf-8").decode("unicode_escape")
# 步骤2：去除包裹的反引号和前缀
# 分割出有效 JSON 部分（假设格式为 ```json\n[...]```）
json_str = unescaped.strip("` \n\t")  # 去掉首尾反引号、空格、换行符
json_str = json_str.split("json\n", 1)[-1]  # 去掉开头的 "json\n"
bboxes = json.loads(json_str)
print(json.dumps(bboxes))
# 解析 JSON 字符串
# 下载图片

response = requests.get(url, stream=True)
response.raise_for_status()  # 确保请求成功

# 打开图片并转换为RGBA模式
image = Image.open(BytesIO(response.content)).convert('RGBA')

# 创建一个可以在图像上绘制的对象
draw = ImageDraw.Draw(image)

# 定义框的颜色和宽度
bbox_color = "red"
bbox_width = 3

# 遍历每个边界框并绘制
for bbox in bboxes:
    x1, y1, x2, y2 = bbox['bbox_2d']
    draw.rectangle([x1, y1, x2, y2], outline=bbox_color, width=bbox_width)

    # 可选：在框的旁边绘制标签
    label = bbox['label']
    draw.text((x1, y1 - 20), label, fill=bbox_color)

# 保存图像
parsed_url = urlparse(url)
path = parsed_url.path
filename, ext =  os.path.splitext(os.path.basename(path))

image.save('output_bbox/' + filename + '.png', 'PNG')

print("处理完成，图片已保存")