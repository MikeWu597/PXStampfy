import os
import argparse
from PIL import Image


def convert_yolo_to_bbox(yolo_box, img_width, img_height):
    """将YOLO格式的归一化坐标转换为实际像素坐标"""
    _, x_center_norm, y_center_norm, width_norm, height_norm = yolo_box
    x_center = float(x_center_norm) * img_width
    y_center = float(y_center_norm) * img_height
    width = float(width_norm) * img_width
    height = float(height_norm) * img_height

    # 计算实际坐标
    x_min = int(round(x_center - width / 2))
    y_min = int(round(y_center - height / 2))
    x_max = int(round(x_center + width / 2))
    y_max = int(round(y_center + height / 2))

    # 确保坐标不越界
    x_min = max(0, x_min)
    y_min = max(0, y_min)
    x_max = min(img_width, x_max)
    y_max = min(img_height, y_max)

    return (x_min, y_min, x_max, y_max)


def process_images(image_dir, label_dir, output_dir):
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 支持的图片格式
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tif')

    # 遍历图片目录
    for img_file in os.listdir(image_dir):
        img_path = os.path.join(image_dir, img_file)

        # 跳过非图片文件
        if not img_file.lower().endswith(valid_extensions):
            continue

        # 获取对应标签文件路径
        base_name = os.path.splitext(img_file)[0]
        label_file = os.path.join(label_dir, f"{base_name}.txt")

        if not os.path.exists(label_file):
            print(f"警告：未找到标签文件 {label_file}，跳过")
            continue

        # 打开图片并获取尺寸
        try:
            with Image.open(img_path) as img:
                img_width, img_height = img.size

                # 读取标签文件
                with open(label_file, 'r') as f:
                    for idx, line in enumerate(f):
                        line = line.strip()
                        if not line:
                            continue

                        # 解析YOLO格式
                        parts = line.split()
                        if len(parts) != 5:
                            print(f"无效行格式：{label_file} 第{idx + 1}行，跳过")
                            continue

                        # 转换坐标
                        try:
                            bbox = convert_yolo_to_bbox(parts, img_width, img_height)
                        except ValueError as e:
                            print(f"坐标转换错误：{label_file} 第{idx + 1}行 - {e}，跳过")
                            continue

                        # 检查有效区域
                        if bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
                            print(f"无效边界框：{label_file} 第{idx + 1}行，跳过")
                            continue

                        # 裁剪图片
                        try:
                            crop = img.crop(bbox)
                        except Exception as e:
                            print(f"裁剪失败：{img_file} 第{idx}个框 - {e}，跳过")
                            continue

                        # 保存结果
                        output_file = f"{base_name}_{idx}.png"
                        output_path = os.path.join(output_dir, output_file)
                        crop.save(output_path, 'PNG')
                        print(f"已保存：{output_file}")

        except Exception as e:
            print(f"处理图片 {img_file} 时出错：{e}")
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='从YOLO标注中提取边界框图片')
    parser.add_argument('--image_dir', required=True, help='包含原始图片的目录')
    parser.add_argument('--label_dir', required=True, help='包含YOLO标签文件的目录')
    parser.add_argument('--output_dir', required=True, help='保存裁剪图片的输出目录')

    args = parser.parse_args()

    process_images(
        image_dir=args.image_dir,
        label_dir=args.label_dir,
        output_dir=args.output_dir
    )
