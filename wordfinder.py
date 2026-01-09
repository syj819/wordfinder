import os
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext


def search_text():
    keyword = keyword_entry.get()

    if not keyword:
        messagebox.showwarning("提示", "请输入搜索内容")
        return

    result_box.delete(1.0, tk.END)
    keyword_lower = keyword.lower()
    match_count = 0

    for root, _, files in os.walk(search_root):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, start=1):
                        if keyword_lower in line.lower():
                            match_count += 1
                            result_box.insert(
                                tk.END,
                                f"[文件] {file_path}\n"
                                f"[行号] {line_num}\n"
                                f"[内容] {line.strip()}\n"
                                + "-" * 60 + "\n"
                            )
            except UnicodeDecodeError:
                # 非 UTF-8 文件直接跳过
                continue
            except Exception as e:
                result_box.insert(tk.END, f"[错误] {file_path}: {e}\n")

    if match_count == 0:
        result_box.insert(tk.END, "未找到匹配内容\n")
    else:
        result_box.insert(tk.END, f"\n共找到 {match_count} 处匹配\n")


# ================= 程序入口 =================

# exe / 脚本所在目录
search_root = os.path.dirname(os.path.abspath(sys.argv[0]))

root = tk.Tk()
root.title("文本搜索工具（自动搜索当前目录）")
root.geometry("900x600")

# 当前搜索目录显示（只读）
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