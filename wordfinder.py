import os
import sys
import tkinter as tk
from tkinter import messagebox
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

NOTEPAD_PP_PATHS = [
    r"C:\Program Files\Notepad++\notepad++.exe",
    r"C:\Program Files (x86)\Notepad++\notepad++.exe",
]

def find_notepad_pp():
    for p in NOTEPAD_PP_PATHS:
        if os.path.exists(p):
            return p
    return None


class WordFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文本搜索工具（自动搜索当前目录）")
        self.root.geometry("1000x700")

        self.search_var = tk.StringVar()
        self.result_map = {}  # file_path -> [(line_no, line_text, hit_positions)]

        self._build_ui()

    # ---------------- UI ----------------

    def _build_ui(self):
        # 顶部
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=10, pady=5)

        tk.Label(top, text="当前搜索目录：").grid(row=0, column=0, sticky="w")
        tk.Label(top, text=BASE_DIR, fg="blue").grid(row=0, column=1, sticky="w")

        tk.Label(top, text="搜索内容（忽略大小写）：").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(top, textvariable=self.search_var, width=40).grid(row=1, column=1, sticky="w")
        tk.Button(top, text="开始搜索", command=self.search).grid(row=1, column=2, padx=10)

        # 文件按钮区（横向）
        self.file_bar = tk.Frame(self.root)
        self.file_bar.pack(fill="x", padx=10, pady=5)

        # 内容区
        self.text = tk.Text(self.root, wrap="none")
        self.text.pack(fill="both", expand=True, padx=10, pady=5)

        self.text.tag_config("line_no", foreground="blue")
        self.text.tag_config("keyword", foreground="red")

    # ---------------- 搜索逻辑 ----------------

    def search(self):
        keyword = self.search_var.get().strip()
        if not keyword:
            messagebox.showwarning("提示", "请输入搜索内容")
            return

        self.result_map.clear()
        self._clear_file_bar()
        self.text.config(state="normal")
        self.text.delete("1.0", "end")

        for root_dir, _, files in os.walk(BASE_DIR):
            for fname in files:
                path = os.path.join(root_dir, fname)
                self._scan_file(path, keyword)

        if not self.result_map:
            self.text.insert("end", "未搜索到匹配内容")
            self.text.config(state="disabled")
            return

        # 生成文件按钮
        for path, records in self.result_map.items():
            count = sum(len(r[2]) for r in records)
            btn = tk.Label(
                self.file_bar,
                text=f"{os.path.basename(path)} ({count})",
                relief="groove",
                padx=6,
                pady=2,
                cursor="hand2",
            )
            btn.pack(side="left", padx=4)

            btn.bind("<Button-1>", lambda e, p=path: self.show_file(p))
            btn.bind("<Double-Button-1>", lambda e, p=path: self.open_file(p))

        # 默认显示第一个
        first = next(iter(self.result_map))
        self.show_file(first)

    def _scan_file(self, path, keyword):
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            return

        keyword_lower = keyword.lower()
        records = []

        for idx, line in enumerate(lines, 1):
            line_lower = line.lower()
            positions = []
            start = 0
            while True:
                pos = line_lower.find(keyword_lower, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + len(keyword)

            if positions:
                records.append((idx, line.rstrip("\n"), positions))

        if records:
            self.result_map[path] = records

    # ---------------- 显示 ----------------

    def show_file(self, path):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")

        self.text.insert("end", f"{path}\n\n")

        for line_no, content, positions in self.result_map[path]:
            line_start = self.text.index("end")
            prefix = f"行{line_no}   "
            self.text.insert("end", prefix + content + "\n")

            # 行号蓝色
            self.text.tag_add(
                "line_no",
                line_start,
                f"{line_start}+{len(prefix)-3}c",
            )

            # 关键词红色
            base = f"{line_start}+{len(prefix)}c"
            for pos in positions:
                self.text.tag_add(
                    "keyword",
                    f"{base}+{pos}c",
                    f"{base}+{pos + len(self.search_var.get())}c",
                )

        self.text.config(state="disabled")

    # ---------------- 文件操作 ----------------

    def open_file(self, path):
        npp = find_notepad_pp()
        try:
            if npp:
                subprocess.Popen([npp, path])
            else:
                subprocess.Popen(["notepad.exe", path])
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _clear_file_bar(self):
        for w in self.file_bar.winfo_children():
            w.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = WordFinderApp(root)
    root.mainloop()
