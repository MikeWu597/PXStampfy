# PXStampfy
这是一个基于YOLOv11的深度学习模型，专门用于识别明信片上的邮票。该模型能够自动检测并定位明信片上的邮票位置。

## 模型概述
模型架构: YOLOv11n

输入: 明信片图像

输出: 邮票的边界框 (Bounding Box) 、置信度分数

训练数据: 使用了明信片图片，移动设备拍摄，包含多种背景。

模型格式: .pt (PyTorch 模型文件)、.onnx（Onnx部署）

## 备注
dataset文件夹：使用其他大语言模型进行标注的Python代码

## 鸣谢
训练数据支持：Instagram lydia_swap mikewu597 hanas_postcards my_postcard_swaps

## 联系方式
如有任何问题，请联系 i@hyp.ink。

Happy Stamping! 🎉
