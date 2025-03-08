import json
from io import BytesIO

import requests
from PIL import Image, ImageDraw

# 下载图片
url = ''
response = requests.get(url, stream=True)
response.raise_for_status()  # 确保请求成功

# 打开图片并转换为RGBA模式
img = Image.open(BytesIO(response.content)).convert('RGBA')
width, height = img.size

# 解析相对坐标
coords_src = '[{"1":"[0.512, 0.000]","2":"[0.678, 0.000]","3":"[0.678, 0.204]","4":"[0.512, 0.204]"},{"1":"[0.690, 0.000]","2":"[0.846, 0.000]","3":"[0.846, 0.136]","4":"[0.690, 0.136]"},{"1":"[0.858, 0.000]","2":"[1.000, 0.000]","3":"[1.000, 0.136]","4":"[0.858, 0.136]"}]'
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
    abs_points = [(x * width, y * height) for (x, y) in points]
    # 创建透明图层绘制半透明四边形
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fill_color = (255, 0, 0, 128)  # 红色半透明（RGBA）
    draw.polygon(abs_points, fill=fill_color)
    # 合并图层并保存55(
    img = Image.alpha_composite(img, overlay)
img.save('output27597'
            '.png', 'PNG')

print("处理完成，图片已保存为output.png")