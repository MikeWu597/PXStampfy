import os
import json


def convert_to_json(image_folder, output_json):
    data = []
    # 支持的图片扩展名
    image_exts = ('.jpg', '.jpeg', '.png', '.gif')

    for filename in os.listdir(image_folder):
        # 检查是否为图片文件
        if filename.lower().endswith(image_exts):
            image_path = os.path.join(image_folder, filename)
            base_name = os.path.splitext(filename)[0]
            txt_file = f"{base_name}.txt"
            txt_path = os.path.join(image_folder, txt_file)

            # 检查对应的txt文件是否存在
            if not os.path.exists(txt_path):
                continue

            # 读取并处理国家代码
            with open(txt_path, 'r', encoding='utf-8') as f:
                country_code = f.read().strip().upper()

            # 验证代码是否为2位字母或ZZ
            if country_code == 'ZZ':
                pass  # 合法
            elif len(country_code) != 2 or not country_code.isalpha():
                continue  # 非法代码，跳过

            # 构造JSON条目
            entry = {
                "messages": [
                    {
                        "role": "user",
                        "content": "<image>请用ISO标准中的2位大写英文字母描述这张邮票所属的国家/地区，如果不是邮票或无法识别，输出ZZ"
                    },
                    {
                        "role": "assistant",
                        "content": country_code
                    }
                ],
                "images": [image_path]
            }
            data.append(entry)

    # 写入JSON文件
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# 示例用法
convert_to_json(image_folder='images', output_json='output.json')