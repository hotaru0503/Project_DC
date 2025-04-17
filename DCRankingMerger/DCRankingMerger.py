print("DC_RankingMerger\nver 1.0\ncopyright by Firefly(https://gallog.dcinside.com/firefly0517)")

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

def save_as_html_table(save_path, id_sorted, nick_sorted, total_post_count, id_display_map):
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write("<table width='100%' style='border-collapse:collapse' border='1' bordercolor='purple'>\n")
        f.write(f"<tr align='center'> <td colspan='5'>총 글 수: {total_post_count}</td></tr>\n")
        f.write(f"<tr align='center'> <td colspan='5'>갤창랭킹</td></tr>\n")
        f.write("<tr align='center'><td>랭킹</td><td>닉</td><td>아이디/아이피</td><td>글 수</td><td>갤 지분(%)</td></tr>\n")

        rank = 1
        for uid, stats in id_sorted:
            nicknames = "<br>".join(sorted(stats["Nicknames"]))
            id_display = "<br>".join(sorted(id_display_map.get(uid, {uid})))
            share = round(stats["count"] / total_post_count * 100, 2) if total_post_count else 0
            f.write(f"<tr align='center'><td>{rank}</td><td>{nicknames}</td><td>{id_display}</td><td>{stats['count']}</td><td>{share}</td></tr>\n")
            rank += 1

        for nick, stats in nick_sorted:
            share = round(stats["count"] / total_post_count * 100, 2) if total_post_count else 0
            f.write(f"<tr align='center'><td>{rank}</td><td>{nick}</td><td>(닉네임기준)</td><td>{stats['count']}</td><td>{share}</td></tr>\n")
            rank += 1

        f.write("</table>\n")

def merge_user_data_with_id_merge():
    root = tk.Tk()
    root.withdraw()

    file_paths = filedialog.askopenfilenames(title="JSON 파일 선택", filetypes=[("JSON Files", "*.json")])
    if not file_paths:
        return

    default_merge_path = os.path.join(os.path.dirname(__file__), "id_merge.txt")
    merge_path = default_merge_path if os.path.exists(default_merge_path) else filedialog.askopenfilename(
        title="ID 병합 리스트 선택 (예: id_merge.txt)", filetypes=[("텍스트 파일", "*.txt")]
    )
    if not merge_path:
        return

    ID_MERGE_MAP, ID_DISPLAY_MAP = load_id_merge_map(merge_path)

    id_based = defaultdict(lambda: {
        "Nicknames": set(),
        "count": 0,
        "recommend": 0  # 추가: 추천 수 누적용
    })
    nick_based = defaultdict(lambda: {
        "count": 0,
        "recommend": 0
    })

    for path in file_paths:
        with open(path, 'r', encoding='utf-8') as f:
            try:
                json_data = json.load(f)
                for entry in json_data:
                    for user in entry.get("userInfos", []):
                        uid = user.get("IdorIp", "").strip()
                        uid = ID_MERGE_MAP.get(uid, uid)
                        raw_nick = user.get("Nick", "").strip()
                        count = user.get("count", 0)
                        recommend = user.get("gallRecommend", 0)  # 추천 수 포함

                        if uid:
                            id_based[uid]["Nicknames"].add(raw_nick)
                            id_based[uid]["count"] += count
                            id_based[uid]["recommend"] += recommend
                        elif raw_nick:
                            clean_nick = clean_nickname(raw_nick)
                            nick_based[clean_nick]["count"] += count
                            nick_based[clean_nick]["recommend"] += recommend
            except Exception as e:
                print(f"⚠️ 오류 발생: {e}")

    total_count = sum(v["count"] for v in id_based.values()) + sum(v["count"] for v in nick_based.values())
    id_sorted = sorted(id_based.items(), key=lambda x: x[1]["count"], reverse=True)
    nick_sorted = sorted(nick_based.items(), key=lambda x: x[1]["count"], reverse=True)

    save_path = filedialog.asksaveasfilename(
        title="HTML 표로 저장",
        defaultextension=".gr.txt",
        filetypes=[("디시 갤창 결과 파일", "*.gr.txt")]
    )

    if save_path:
        save_as_html_table(save_path, id_sorted, nick_sorted, total_count, ID_DISPLAY_MAP)
        messagebox.showinfo("완료", f"HTML 갤창 표 저장 완료!\n{save_path}")

if __name__ == "__main__":
    merge_user_data_with_id_merge()
