print("DC_TotalRanker v1.1.0")
print("MIT License. Copyright (c) 2025 hotaru0503")

import json
import tkinter as tk
from tkinter import filedialog, messagebox
from bs4 import BeautifulSoup
import os
import re
from collections import defaultdict

def clean_nickname(nick):
    return re.sub(r'\(\d{1,3}(?:\.\d{1,3}){1,3}\)', '', nick).strip()

def load_html_table(filepath, column_name, expected_label):
    with open(filepath, encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    headers = soup.find_all("td", colspan="5")
    if not any(expected_label in h.get_text() for h in headers):
        raise ValueError(f"선택한 파일이 '{expected_label}'이 아닙니다: {filepath}")
    rows = soup.find_all("tr")[3:]
    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 5:
            nick = cols[1].get_text(separator=", ", strip=True)
            uid = cols[2].get_text(separator=", ", strip=True)
            count = int(cols[3].get_text(strip=True))
            data.append((uid, nick, count))
    return {uid: {"nick": nick, column_name: count} for uid, nick, count in data}

def load_weights():
    default = {"글 가중치": 2.5, "댓글 가중치": 1.0}
    weight_path = os.path.join(os.path.dirname(__file__), "weight.txt")
    if os.path.exists(weight_path):
        with open(weight_path, 'r', encoding='utf-8') as f:
            for line in f:
                if ":" in line:
                    key, val = map(str.strip, line.split(":"))
                    if key in default:
                        try:
                            default[key] = float(val)
                        except ValueError:
                            continue
    return default

def merge_sources(post_data, reply_data):
    all_keys = set(post_data) | set(reply_data)
    merged = []
    weights = load_weights()
    for uid in all_keys:
        nick = post_data.get(uid, {}).get("nick") or reply_data.get(uid, {}).get("nick") or "알 수 없음"
        post = post_data.get(uid, {}).get("글 수", 0)
        reply = reply_data.get(uid, {}).get("댓글 수", 0)
        score = post * weights["글 가중치"] + reply * weights["댓글 가중치"]
        merged.append({
            "닉네임": nick,
            "아이디/아이피": uid,
            "글 수": post,
            "댓글 수": reply,
            "점수": score
        })
    # 동석차 정렬
    merged.sort(key=lambda x: (-x["점수"], x["아이디/아이피"]))
    ranked_results = []
    rank = 0
    prev_score = None
    same_rank_count = 0
    for user in merged:
        current_score = user["점수"]
        if current_score != prev_score:
            rank += same_rank_count + 1
            same_rank_count = 0
        else:
            same_rank_count += 1
        prev_score = current_score
        ranked_results.append((rank, user))
    return ranked_results[:10], weights

def save_result_html(save_path, ranked_list, weights):
    def wrap(val, color):
        return f'<font color="{color}">{val}</font>' if color else val

    with open(save_path, 'w', encoding='utf-8') as f:
        f.write("<table width='100%' style='border-collapse:collapse' border='1' bordercolor='black'>\n")
        f.write("<tr align='center'><td colspan='6'>글+댓글 통합 랭킹 TOP 10</td></tr>\n")
        f.write("<tr align='center'><td>랭킹</td><td>닉네임</td><td>아이디/아이피</td><td>글 수</td><td>댓글 수</td><td>점수</td></tr>\n")

        for rank, row in ranked_list:
            color = None
            if rank == 1:
                color = "#FFD700"
            elif rank == 2:
                color = "#9c9c94"
            elif rank == 3:
                color = "#CD7F32"
            nick_html = "<br>".join(row["닉네임"].split(", "))
            uid_html = "<br>".join(row["아이디/아이피"].split(", "))
            f.write(f"<tr align='center'><td>{wrap(rank, color)}</td><td>{wrap(nick_html, color)}</td><td>{wrap(uid_html, color)}</td><td>{wrap(row['글 수'], color)}</td><td>{wrap(row['댓글 수'], color)}</td><td>{wrap(row['점수'], color)}</td></tr>\n")

        f.write(f"<tr align='left'><td colspan='6'>* 점수 가중치: 글={weights['글 가중치']}점, 댓글={weights['댓글 가중치']}점</td></tr>\n")
        f.write("</table>\n")

def main():
    root = tk.Tk()
    root.withdraw()

    post_path = filedialog.askopenfilename(title="HTML 갤창 랭킹.gr.txt 선택", filetypes=[("HTML 갤창 랭킹", "*.gr.txt")])
    if not post_path:
        return
    reply_path = filedialog.askopenfilename(title="HTML 댓글 랭킹.cr.txt 선택", filetypes=[("HTML 댓글 랭킹", "*.cr.txt")])
    if not reply_path:
        return

    try:
        post_data = load_html_table(post_path, "글 수", "갤창랭킹")
        reply_data = load_html_table(reply_path, "댓글 수", "댓글랭킹")
    except ValueError as e:
        messagebox.showerror("파일 오류", str(e))
        return

    top10, weights = merge_sources(post_data, reply_data)

    save_path = filedialog.asksaveasfilename(
        title="통합 랭킹 저장",
        defaultextension=".tr.txt",
        filetypes=[("통합 랭킹 파일", "*.tr.txt")]
    )

    if save_path:
        save_result_html(save_path, top10, weights)
        messagebox.showinfo("완료", "통합 랭킹 결과가 저장되었습니다!\n{save_path}")

if __name__ == "__main__":
    main()
    print("Done!")
