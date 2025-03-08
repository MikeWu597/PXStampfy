import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import json


class BBoxAnnotator:
    def __init__(self, root):
        self.root = root
        self.root.title("BBox Annotation Tool")

        # 初始化变量
        self.image_list = []
        self.current_index = 0
        self.bbox_data = {}
        self.start_x = None
        self.start_y = None
        self.current_bboxes = []
        self.scale = 1.0
        self.original_size = (0, 0)

        # 创建界面组件
        self.create_widgets()

        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

    def create_widgets(self):
        # 按钮面板
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X)

        self.select_btn = tk.Button(control_frame, text="打开文件夹", command=self.select_folder)
        self.select_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.next_btn = tk.Button(control_frame, text="下一张", command=self.next_image, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # 状态标签
        self.status_label = tk.Label(self.root, text="请选择包含图片的文件夹")
        self.status_label.pack()

        # 画布
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="gray")
        self.canvas.pack()

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        # 获取支持的图片格式
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        self.image_list = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.splitext(f)[1].lower() in image_extensions
        ]

        if not self.image_list:
            self.status_label.config(text="文件夹中没有找到图片")
            return

        self.current_index = 0
        self.next_btn.config(state=tk.NORMAL)
        self.load_image(self.image_list[self.current_index])

    def load_image(self, image_path):
        try:
            # 打开并调整图片大小
            image = Image.open(image_path)
            self.original_size = image.size
            img_width, img_height = self.original_size

            # 计算缩放比例
            max_width, max_height = 800, 600
            self.scale = min(max_width / img_width, max_height / img_height)

            new_size = (
                int(img_width * self.scale),
                int(img_height * self.scale)
            )
            image = image.resize(new_size, Image.Resampling.LANCZOS)

            # 更新画布
            self.canvas.config(width=new_size[0], height=new_size[1])
            self.tk_image = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

            # 重置当前标注
            self.current_bboxes = []
            self.update_status(
                f"正在标注：{os.path.basename(image_path)} ({self.current_index + 1}/{len(self.image_list)})")

        except Exception as e:
            self.update_status(f"无法加载图片：{str(e)}")

    def on_mouse_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            self.start_x, self.start_y,
            outline="red", width=2)

    def on_mouse_drag(self, event):
        if self.current_rect:
            self.canvas.coords(
                self.current_rect,
                self.start_x, self.start_y,
                event.x, event.y)

    def on_mouse_release(self, event):
        end_x = event.x
        end_y = event.y

        # 转换坐标到原始尺寸
        x1 = int(self.start_x / self.scale)
        y1 = int(self.start_y / self.scale)
        x2 = int(end_x / self.scale)
        y2 = int(end_y / self.scale)

        # 确保坐标顺序正确
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])

        # 添加标注
        self.current_bboxes.append({
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        })

        # 绘制永久矩形
        self.canvas.create_rectangle(
            self.start_x, self.start_y,
            end_x, end_y,
            outline="green", width=2)

        self.current_rect = None

    def next_image(self):
        # 保存当前标注
        if self.current_index < len(self.image_list):
            current_path = self.image_list[self.current_index]
            self.bbox_data[current_path] = self.current_bboxes.copy()

            self.current_index += 1
            if self.current_index < len(self.image_list):
                self.load_image(self.image_list[self.current_index])
            else:
                self.save_data()
                self.update_status("标注完成！数据已保存到bbox.json")
                self.next_btn.config(state=tk.DISABLED)

    def save_data(self):
        # 转换数据格式
        output = {}
        for path, bboxes in self.bbox_data.items():
            output[os.path.basename(path)] = {
                "width": self.original_size[0],
                "height": self.original_size[1],
                "bboxes": bboxes
            }

        with open("bbox.json", "w") as f:
            json.dump(output, f, indent=4)

    def update_status(self, text):
        self.status_label.config(text=text)


if __name__ == "__main__":
    root = tk.Tk()
    app = BBoxAnnotator(root)
    root.mainloop()
