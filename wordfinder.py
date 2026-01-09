import os
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext


def search_text():
    keyword = keyword_entry.get().strip()

    if not keyword:
        messagebox.showwarning("提示", "请输入搜索内容")
        return

    result_box.delete(1.0, tk.END)
    keyword_lower = keyword.lower()

    # 用字典按文件分组
    results = {}

    for root, _, files in os.walk(search_root):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, start=1):
                        if keyword_lower in line.lower():
                            results.setdefault(file_path, []).append(
                                (line_num, line.strip())
                            )
            except UnicodeDecodeError:
                continue
            except Exception as e:
                results.setdefault(file_path, []).append(
                    ("错误", str(e))
                )

    if not results:
        result_box.insert(tk.END, "未找到匹配内容\n")
        return

    # 按文件输出
    for file_path, matches in results.items():
        result_box.insert(tk.END, f"{file_path}\n")
        for line_num, content in matches:
            result_box.insert(
                tk.END,
                f"  行{line_num:<5} {content}\n"
            )
        result_box.insert(tk.END, "-" * 60 + "\n")


# ================= 程序入口 =================

# exe 所在目录（模式 2）
search_root = os.path.dirname(os.path.abspath(sys.argv[0]))

root = tk.Tk()
root.title("文本搜索工具（自动搜索当前目录）")
root.geometry("900x600")

# 当前搜索目录显示
tk.Label(root, text="当前搜索目录：").pack(anchor="w", padx=10, pady=5)
tk.Label(root, text=search_root, fg="blue").pack(anchor="w", padx=20)

# 搜索关键字
tk.Label(root, text="搜索内容（忽略大小写）：").pack(anchor="w", padx=10, pady=10)
keyword_entry = tk.Entry(root, width=50)
keyword_entry.pack(padx=10)

# 搜索按钮
tk.Button(root, text="开始搜索", command=search_text).pack(pady=10)

# 结果显示区
result_box = scrolledtext.ScrolledText(root, wrap=tk.WORD)
result_box.pack(expand=True, fill="both", padx=10, pady=10)

root.mainloop()
