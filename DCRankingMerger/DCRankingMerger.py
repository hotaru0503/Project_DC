print("DC_RankingMerger v1.1.0")
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

def save_as_html_table(save_path, ranked_data, total_post_count, id_display_map):
    def wrap(val, color):
        return f'<font color="{color}">{val}</font>' if color else val

    with open(save_path, 'w', encoding='utf-8') as f:
        f.write("<table width='100%' style='border-collapse:collapse' border='1' bordercolor='purple'>\n")
        f.write(f"<tr align='center'> <td colspan='5'>총 글 수: {total_post_count} (전월대비 nn.nn%p 증가/감소)</td></tr>\n")
        f.write(f"<tr align='center'> <td colspan='5'>갤창랭킹</td></tr>\n")
        f.write("<tr align='center'><td>랭킹</td><td>닉</td><td>아이디/아이피</td><td>글 수</td><td>갤 지분(%)</td></tr>\n")

        for rank, (uid, stats) in ranked_data:
            color = None
            if rank == 1:
                color = "#FFD700"  # gold
            elif rank == 2:
                color = "#9c9c94"  # silver
            elif rank == 3:
                color = "#CD7F32"  # bronze

            nicknames = "<br>".join(sorted(stats["Nicknames"]))
            id_display = "<br>".join(sorted(id_display_map.get(uid, {uid})))
            share = round(stats["count"] / total_post_count * 100, 2) if total_post_count else 0

            f.write(f"<tr align='center'><td>{wrap(rank, color)}</td><td>{wrap(nicknames, color)}</td><td>{wrap(id_display, color)}</td><td>{wrap(stats['count'], color)}</td><td>{wrap(share, color)}</td></tr>\n")

        f.write("</table>\n")

def merge_user_data_with_id_merge():
    root = tk.Tk()
    root.withdraw()

    file_paths = filedialog.askopenfilenames(title="JSON 파일 선택", filetypes=[("JSON Files", "*.json")])
    if not file_paths:
        return

    merge_path = os.path.join(os.path.dirname(__file__), "id_merge.txt")
    ID_MERGE_MAP, ID_DISPLAY_MAP = load_id_merge_map(merge_path)

    id_based = defaultdict(lambda: {"Nicknames": set(), "count": 0})
    for path in file_paths:
        with open(path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            for entry in json_data:
                for user in entry.get("userInfos", []):
                    uid = ID_MERGE_MAP.get(user.get("IdorIp", "").strip(), user.get("IdorIp", "").strip())
                    raw_nick = user.get("Nick", "").strip()
                    count = user.get("count", 0)
                    if uid:
                        id_based[uid]["Nicknames"].add(raw_nick)
                        id_based[uid]["count"] += count

    config = load_filter_config()
    min_posts = config['min_posts']
    total_count = sum(v["count"] for v in id_based.values())
    filtered_sorted_data = sorted([(uid, data) for uid, data in id_based.items() if data["count"] >= min_posts],
                                  key=lambda x: (-x[1]["count"], x[0]))

    ranked_results = []
    rank, prev_count, same_rank_count = 0, None, 0
    for uid, data in filtered_sorted_data:
        current_count = data["count"]
        if current_count != prev_count:
            rank += same_rank_count + 1
            same_rank_count = 0
        else:
            same_rank_count += 1
        prev_count = current_count
        ranked_results.append((rank, (uid, data)))

    save_path = filedialog.asksaveasfilename(title="HTML 갤창 랭킹 저장", defaultextension=".gr.txt",
                                             filetypes=[("HTML 갤창 랭킹", "*.gr.txt")])
    if save_path:
        save_as_html_table(save_path, ranked_results, total_count, ID_DISPLAY_MAP)
        messagebox.showinfo("완료", f"글 합산 결과가 저장되었습니다!\n{save_path}")

if __name__ == "__main__":
    merge_user_data_with_id_merge()
    print("Done!")
