print("DC_CommentMerger v1.1.0")
print("MIT License. Copyright (c) 2025 hotaru0503")

import json
import tkinter as tk
from tkinter import filedialog, messagebox
import re
import os
from collections import defaultdict

def load_id_merge_map(path):
    merge_map = {}
    display_map = defaultdict(set)
    if not os.path.exists(path):
        return merge_map, display_map
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if '->' in line:
                src, dst = map(str.strip, line.split('->'))
                merge_map[src] = dst
                display_map[dst].update([src, dst])
    return merge_map, display_map

def clean_nickname(nick):
    return re.sub(r'\(\d{1,3}(?:\.\d{1,3}){1,3}\)', '', nick).strip()

def load_filter_config(filename='filter_config.txt'):
    config = {'min_posts': 1, 'min_comments': 1}
    if not os.path.exists(filename):
        return config
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=')
            config[key.strip()] = int(value.strip())
    return config

def save_as_html_table(save_path, ranked_data, total_count):
    def wrap(val, color):
        return f'<font color="{color}">{val}</font>' if color else val

    with open(save_path, 'w', encoding='utf-8') as f:
        f.write("<table width='100%' style='border-collapse:collapse' border='1' bordercolor='purple'>\n")
        f.write(f"<tr align='center'> <td colspan='5'>총 댓글 수: {total_count} (전월대비 nn.nn%p 증가/감소)</td></tr>\n")
        f.write(f"<tr align='center'> <td colspan='5'>댓글랭킹</td></tr>\n")
        f.write("<tr align='center'><td>랭킹</td><td>닉</td><td>아이디/아이피</td><td>댓글 수</td><td>갤 지분(%)</td></tr>\n")

        for rank, row in ranked_data:
            color = None
            if rank == 1:
                color = "#FFD700"  # gold
            elif rank == 2:
                color = "#9c9c94"  # silver
            elif rank == 3:
                color = "#CD7F32"  # bronze

            f.write(f"<tr align='center'><td>{wrap(rank, color)}</td><td>{wrap(row['닉네임'], color)}</td><td>{wrap(row['아이디/아이피'], color)}</td><td>{wrap(row['댓글 수'], color)}</td><td>{wrap(row['갤 지분(%)'], color)}</td></tr>\n")

        f.write("</table>\n")

def merge_comment_data_to_html():
    root = tk.Tk()
    root.withdraw()

    file_paths = filedialog.askopenfilenames(title="댓글 JSON 파일 선택", filetypes=[("JSON Files", "*.json")])
    if not file_paths:
        return

    default_merge_path = os.path.join(os.path.dirname(__file__), "id_merge.txt")
    ID_MERGE_MAP, ID_DISPLAY_MAP = load_id_merge_map(default_merge_path)

    id_based = defaultdict(lambda: {"Nicknames": set(), "replyCount": 0})
    for path in file_paths:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for user in data:
                uid = ID_MERGE_MAP.get(user.get("uid", "").strip(), user.get("uid", "").strip())
                raw_nick = user.get("name", "").strip()
                reply_count = user.get("replyCount", 0)
                if uid:
                    id_based[uid]["Nicknames"].add(raw_nick)
                    id_based[uid]["replyCount"] += reply_count

    config = load_filter_config()
    min_comments = config['min_comments']
    total_count = sum(v["replyCount"] for v in id_based.values())
    filtered_sorted_data = sorted([(uid, data) for uid, data in id_based.items() if data["replyCount"] >= min_comments],
                                  key=lambda x: (-x[1]["replyCount"], x[0]))

    ranked_results = []
    rank, prev_count, same_rank_count = 0, None, 0
    for uid, data in filtered_sorted_data:
        current_count = data["replyCount"]
        if current_count != prev_count:
            rank += same_rank_count + 1
            same_rank_count = 0
        else:
            same_rank_count += 1
        prev_count = current_count
        ranked_results.append((rank, {
            "닉네임": "<br>".join(sorted(data["Nicknames"])),
            "아이디/아이피": "<br>".join(sorted(ID_DISPLAY_MAP.get(uid, {uid}))),
            "댓글 수": data["replyCount"],
            "갤 지분(%)": round(data["replyCount"] / total_count * 100, 2) if total_count else 0
        }))

    save_path = filedialog.asksaveasfilename(title="HTML 댓글 랭킹 저장", defaultextension=".cr.txt",
                                             filetypes=[("HTML 댓글 랭킹", "*.cr.txt")])
    if save_path:
        save_as_html_table(save_path, ranked_results, total_count)
        messagebox.showinfo("완료", f"댓글 합산 결과가 저장되었습니다!\n{save_path}")

if __name__ == "__main__":
    merge_comment_data_to_html()
    print("Done!")
