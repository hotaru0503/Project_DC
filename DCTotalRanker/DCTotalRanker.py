print("DCRankingMerger\nver 1.0\ncopyright by Firefly(https://gallog.dcinside.com/firefly0517)")

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
            uid = cols[2].get_text(strip=True)
            count = int(cols[3].get_text(strip=True))
            data.append((uid, nick, count))
    return {uid: {"nick": nick, column_name: count} for uid, nick, count in data}


def load_weights():
    default = {"글 가중치": 2.0, "댓글 가중치": 1.0}
    weight_path = os.path.join(os.path.dirname(__file__), "weight.txt")
    if not os.path.exists(weight_path):
        print("⚠️ weight.txt 파일이 없어 모든 가중치에 대해 사용자 입력이 필요합니다.")
        keys = ["글 가중치", "댓글 가중치"]
    else:
        with open(weight_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        keys = []
        for line in lines:
            if ":" in line:
                key, val = map(str.strip, line.split(":"))
                if key in default:
                    try:
                        default[key] = float(val)
                    except ValueError:
                        keys.append(key)
    for key in ["글 가중치", "댓글 가중치"]:
        if key not in default or not isinstance(default[key], float):
            try:
                user_input = float(input(f"[입력 필요] '{key}'의 가중치를 숫자로 입력하세요: "))
                default[key] = user_input
            except:
                print(f"⚠️ '{key}'의 값이 유효하지 않아 기본값 {default.get(key, 0.0)}이 적용됩니다.")
                default[key] = default.get(key, 0.0)
    return default
    with open(weight_path, 'r', encoding='utf-8') as f:
        for line in f:
            if ":" in line:
                key, val = map(str.strip, line.split(":"))
                if key in default:
                    if val.isdigit():
                        default[key] = int(val)
                    else:
                        try:
                            user_input = int(input(f"[입력 필요] '{key}'의 가중치가 잘못되었습니다. 숫자로 입력하세요: "))
                            default[key] = user_input
                        except:
                            print(f"⚠️ '{key}'의 값이 유효하지 않아 기본값 {default[key]}이 적용됩니다.")
    return default
    with open(weight_path, 'r', encoding='utf-8') as f:
        for line in f:
            if ":" in line:
                key, val = map(str.strip, line.split(":"))
                if key.strip() in default and val.isdigit():
                    default[key] = int(val)
    return default


def merge_sources(post_data, reply_data):
    all_keys = set(post_data) | set(reply_data)
    merged = []
    for uid in all_keys:
        nick = post_data.get(uid, {}).get("nick") or reply_data.get(uid, {}).get("nick") or "알 수 없음"
        post = post_data.get(uid, {}).get("글 수", 0)
        reply = reply_data.get(uid, {}).get("댓글 수", 0)
        weights = load_weights()
        score = post * weights["글 가중치"] + reply * weights["댓글 가중치"]
        merged.append({
            "닉네임": nick,
            "아이디/아이피": uid,
            "글 수": post,
            "댓글 수": reply,
            "점수": score
        })
    return sorted(merged, key=lambda x: x["점수"], reverse=True)[:10]

def save_result_html(save_path, top10):
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write("<table width='100%' style='border-collapse:collapse' border='1' bordercolor='black'>\n")
        f.write("<tr align='center'><td colspan='6'>글+댓글 통합 랭킹 (상위 10명)</td></tr>\n")
        f.write("<tr align='center'><td>랭킹</td><td>닉네임</td><td>아이디/아이피</td><td>글 수</td><td>댓글 수</td><td>점수</td></tr>\n")
        for i, row in enumerate(top10, 1):
            f.write(f"<tr align='center'><td>{i}</td><td>{row['닉네임']}</td><td>{row['아이디/아이피']}</td><td>{row['글 수']}</td><td>{row['댓글 수']}</td><td>{row['점수']}</td></tr>\n")
        f.write("</table>\n")

def main():
    root = tk.Tk()
    root.withdraw()

    post_path = filedialog.askopenfilename(title="글 수 .gr.txt 선택", filetypes=[("Result Files", "*.gr.txt")])
    if not post_path:
        return
    reply_path = filedialog.askopenfilename(title="댓글 수 .cr.txt 선택", filetypes=[("Result Files", "*.cr.txt")])
    if not reply_path:
        return

    try:
        post_data = load_html_table(post_path, "글 수", "갤창랭킹")
        reply_data = load_html_table(reply_path, "댓글 수", "댓글랭킹")
    except ValueError as e:
        messagebox.showerror("파일 오류", str(e))
        return

    top10 = merge_sources(post_data, reply_data)

    save_path = filedialog.asksaveasfilename(
        title="통합 랭킹 저장",
        defaultextension=".tr.txt",
        filetypes=[("통합 랭킹 파일", "*.tr.txt")]
    )

    if save_path:
        save_result_html(save_path, top10)
        messagebox.showinfo("완료", "통합 랭킹 결과가 저장되었습니다!")

if __name__ == "__main__":
    main()
