# -*- coding: utf-8 -*-
print("DC_CommentMerger\nver 1.0\ncopyright by Firefly(https://gallog.dcinside.com/firefly0517)")

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

def save_as_html_table(save_path, sorted_data, total_count):
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write("<table width='100%' style='border-collapse:collapse' border='1' bordercolor='purple'>\n")
        f.write(f"<tr align='center'> <td colspan='5'>총 댓글 수: {total_count}</td></tr>\n")
        f.write(f"<tr align='center'> <td colspan='5'>댓글랭킹</td></tr>\n")
        f.write("<tr align='center'><td>랭킹</td><td>닉</td><td>아이디/아이피</td><td>댓글 수</td><td>갤 지분(%)</td></tr>\n")

        for rank, row in enumerate(sorted_data, 1):
            f.write(f"<tr align='center'><td>{rank}</td><td>{row['닉네임']}</td><td>{row['아이디/아이피']}</td><td>{row['댓글 수']}</td><td>{row['갤 지분(%)']}</td></tr>\n")

        f.write("</table>\n")

def merge_comment_data_to_html():
    root = tk.Tk()
    root.withdraw()

    # JSON 파일 선택
    file_paths = filedialog.askopenfilenames(title="댓글 JSON 파일 선택", filetypes=[("JSON Files", "*.json")])
    if not file_paths:
        return

    # 병합 리스트 자동 감지
    default_merge_path = os.path.join(os.path.dirname(__file__), "id_merge.txt")
    ID_MERGE_MAP, ID_DISPLAY_MAP = load_id_merge_map(default_merge_path)

    id_based = defaultdict(lambda: {"Nicknames": set(), "replyCount": 0})
    nick_based = defaultdict(lambda: {"replyCount": 0})

    for path in file_paths:
        with open(path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for user in data:
                    raw_uid = user.get("uid", "").strip()
                    uid = ID_MERGE_MAP.get(raw_uid, raw_uid) if raw_uid else ""
                    raw_nick = user.get("name", "").strip()
                    reply_count = user.get("replyCount", 0)

                    if uid:
                        id_based[uid]["Nicknames"].add(raw_nick)
                        id_based[uid]["replyCount"] += reply_count
                        ID_DISPLAY_MAP[uid].add(raw_uid)
                    else:
                        clean_nick = clean_nickname(raw_nick)
                        key = f"(닉:{clean_nick})"
                        nick_based[key]["replyCount"] += reply_count
            except Exception as e:
                print(f"⚠️ 오류 발생: {e}")

    total_count = sum(v["replyCount"] for v in id_based.values()) + sum(v["replyCount"] for v in nick_based.values())
    rows = []

    for uid, data in sorted(id_based.items(), key=lambda x: x[1]["replyCount"], reverse=True):
        display_uid = "<br>".join(sorted(ID_DISPLAY_MAP.get(uid, {uid})))
        display_nick = "<br>".join(sorted(data["Nicknames"]))
        share = round(data["replyCount"] / total_count * 100, 2) if total_count else 0
        rows.append({"닉네임": display_nick, "아이디/아이피": display_uid, "댓글 수": data["replyCount"], "갤 지분(%)": share})

    for nick, data in sorted(nick_based.items(), key=lambda x: x[1]["replyCount"], reverse=True):
        share = round(data["replyCount"] / total_count * 100, 2) if total_count else 0
        rows.append({"닉네임": nick[5:-1], "아이디/아이피": "(닉네임기준)", "댓글 수": data["replyCount"], "갤 지분(%)": share})

    # 저장
    save_path = filedialog.asksaveasfilename(
        title="HTML 댓글 랭킹 저장",
        defaultextension=".result.txt",
        filetypes=[("디시 댓글 결과 파일", "*.result.txt")]
    )
    if save_path:
        save_as_html_table(save_path, rows, total_count)
        messagebox.showinfo("완료", f"댓글 합산 결과가 저장되었습니다!\n{save_path}")

if __name__ == "__main__":
    merge_comment_data_to_html()
