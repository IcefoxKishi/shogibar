import math
import sys
import traceback

from cshogi import *
from cshogi import KI2
import threading
import subprocess
import tkinter as tk
import numpy as np

# エンジン名・フォント・文字色・背景色
engine = "水匠５"  # 水匠5
barfont = "Noto Sans JP"  # BIZ UDGothic
percentfont = "Noto Sans JP SemiBold"  # BIZ UDGothic
bgcolor = "#ffffff"  # white
fgcolor = "black"
dangercolor = "#f02626"  # black
turnfgcolor = "#00007f"  # #00007f
leftgraphbg = "#000000"  # #000000
rightgraphbg = "#ffffff"  # #ffffff
strlastmove = ""
evals = [0, 0, 0, 0, 0]
piece_points = [0, 1, 1, 1, 1, 5, 5, 1, 0, 1, 1, 1, 1, 5, 5, 0, 0, 1, 1, 1, 1, 5, 5, 1, 0, 1, 1, 1, 1, 5, 5]
piece_in_hand_value = [1, 1, 1, 1, 1, 5, 5]
gote_points = 0
sente_points = 0
sente_camp = []
gote_camp = []
pvs = ["", "", "", "", ""]
current_board_turn = 1
values = []


def cook(c):
    eval = int(c[1])
    if c[2] == 1:
        skibidi = board.copy()
        tolabel = ""
        for move in c[3]:
            tolabel += KI2.move_to_ki2(skibidi.move_from_usi(move), skibidi)
            skibidi.push_usi(move)
        suggestionlabel["text"] = tolabel
    if c[0] == "mate":
        moves = eval * current_board_turn
        if moves < 0:
            if c[2] == 1:
                if abs(eval) % 2 == 0:
                    test = board.copy()
                    test.push_usi(c[3][0])
                    if test.mate_move_in_1ply() != 0 or test.mate_move(abs(eval)-1) != 0:
                        bestpc1["text"] = "(" + str(abs(eval)) + "手詰)"
                    else:
                        bestpc1["text"] = "(必至)"
                else:
                    test = board.copy()
                    if test.mate_move_in_1ply() != 0 or test.mate_move(abs(eval)) != 0:
                        bestpc1["text"] = "(" + str(abs(eval)) + "手詰)"
                    else:
                        bestpc1["text"] = "(必至)"
            return 1
        else:
            if c[2] == 1:
                if abs(eval) % 2 == 0:
                    test = board.copy()
                    test.push_usi(c[3][0])
                    if test.mate_move_in_1ply() != 0 or test.mate_move(abs(eval) - 1) != 0:
                        bestpc1["text"] = "(" + str(abs(eval)) + "手詰)"
                    else:
                        bestpc1["text"] = "(必至)"
                else:
                    test = board.copy()
                    if test.mate_move_in_1ply() != 0 or test.mate_move(abs(eval)) != 0:
                        bestpc1["text"] = "(" + str(abs(eval)) + "手詰)"
                    else:
                        bestpc1["text"] = "(必至)"
            return 99
    else:
        cureval = 100 / (1 + math.exp(eval * current_board_turn / -1200))
        if cureval < 1:
            return 1
        if cureval > 99:
            return 99
        else:
            return cureval


bestpercent = ""
bestpercent2 = ""

# 外部エンジン起動
shogi = subprocess.Popen("./Suisho5.exe", stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         encoding="UTF-8")
board = Board()
scrap = Board()


def king_check():
    if 8 in gote_camp and 24 in sente_camp:
        return True
    else:
        return False


def get_turn(c):
    if c == 0:
        return 1
    if c == 1:
        return -1


def command():
    while True:
        cmdline = input()
        # 局面設定
        if cmdline[:8] == "position":
            saizen.config(font=(barfont, 20))
            global board, last_move
            board.set_position(cmdline[9:])
            global sente_camp
            sente_camp = [board.piece(G1), board.piece(G2), board.piece(G3), board.piece(G4), board.piece(G5),
                          board.piece(G6), board.piece(G7), board.piece(G8), board.piece(G9), board.piece(H1),
                          board.piece(H2), board.piece(H3), board.piece(H4), board.piece(H5), board.piece(H6),
                          board.piece(H7), board.piece(H8), board.piece(H9), board.piece(I1), board.piece(I2),
                          board.piece(I3), board.piece(I4), board.piece(I5), board.piece(I6), board.piece(I7),
                          board.piece(I8), board.piece(I9)]
            global gote_camp
            gote_camp = [board.piece(A1), board.piece(A2), board.piece(A3), board.piece(A4), board.piece(A5),
                         board.piece(A6), board.piece(A7), board.piece(A8), board.piece(A9), board.piece(B1),
                         board.piece(B2), board.piece(B3), board.piece(B4), board.piece(B5), board.piece(B6),
                         board.piece(B7), board.piece(B8), board.piece(B9), board.piece(C1), board.piece(C2),
                         board.piece(C3), board.piece(C4), board.piece(C5), board.piece(C6), board.piece(C7),
                         board.piece(C8), board.piece(C9)]
            global scrap
            if board.history:
                scrap.set_position(cmdline[9:][:-5])
                last_move = board.history[-1]
            global strlastmove
            if board.history:
                strlastmove = KI2.move_to_ki2(last_move, scrap)
            prev = cmdline.split()
            prev.pop(0)
            best1["text"] = "１. "
            best2["text"] = "２. "
            best3["text"] = "３. "
            best4["text"] = "４. "
            best5["text"] = "５. "
            bestpc1["text"] = "-"
            bestpc2["text"] = ""
            bestpc3["text"] = ""
            bestpc4["text"] = ""
            bestpc5["text"] = ""
            global evals
            global gote_points
            global sente_points
            gote_points = 0
            sente_points = 0
            for piece in board.pieces:
                if piece >= 17:
                    gote_points += piece_points[piece]
                else:
                    sente_points += piece_points[piece]
            sente_hand = board.pieces_in_hand[0]
            gote_hand = board.pieces_in_hand[1]
            sente_points += sente_hand[0] + sente_hand[1] + sente_hand[2] + sente_hand[3] + sente_hand[4]
            sente_points += (sente_hand[5] + sente_hand[6]) * 5
            gote_points += gote_hand[0] + gote_hand[1] + gote_hand[2] + gote_hand[3] + gote_hand[4]
            gote_points += (gote_hand[5] + gote_hand[6]) * 5
            global pvs
            pvs = ["", "", "", "", ""]
            global current_board_turn
            current_board_turn = get_turn(board.turn)
            bestpc3["fg"] = "#000000"
            bestpc2["fg"] = "#000000"
            bestpc4["fg"] = "#000000"
            bestpc5["fg"] = "#000000"
            bestpc1["fg"] = "#000000"
        usi(cmdline)


# コマンド入力処理
def usi(c):
    # 終了処理
    if c == "quit":
        root.destroy()
        sys.exit()
    shogi.stdin.write(c + "\n")
    shogi.stdin.flush()


# コマンド出力処理
def output():
    while True:
        # エンジンからの出力を受け取る
        line = shogi.stdout.readline()
        shogibar(line)
        # 標準出力
        sys.stdout.write(line)
        sys.stdout.flush()


# 評価値バー情報更新
def shogibar(line):
    global winrate, bestpercent2, bestpercent, winrate4, winrate5, winrate3, winrate2
    if line[:10] == "info depth":
        if king_check():
            leftgraph["bg"] = "#FFFFFF"
            rightgraph["bg"] = "#FFFFFF"
            leftgraph["bd"] = 0
            rightgraph["bd"] = 0
        sfen = line.split()
        # 左右反転チェックを受け取る
        if bln.get():
            reverse = -1
        else:
            reverse = 1
        # データ処理
        if reverse == 1:
            rightgraph["bg"] = rightgraphbg
            leftgraph["bg"] = leftgraphbg
            lwinratelabel.place(x=25, y=23, anchor=tk.W)
            rwinratelabel.place(x=1225, y=23, anchor=tk.E)
            ltebanlabel.place(x=25, y=100, anchor=tk.W)
            rtebanlabel.place(x=1225, y=100, anchor=tk.E)
        else:
            rightgraph["bg"] = leftgraphbg
            leftgraph["bg"] = rightgraphbg
            rwinratelabel.place(x=25, y=23, anchor=tk.W)
            lwinratelabel.place(x=1225, y=23, anchor=tk.E)
            rtebanlabel.place(x=25, y=100, anchor=tk.W)
            ltebanlabel.place(x=1225, y=100, anchor=tk.E)
        turn = -(board.turn * 2 - 1) * reverse
        move_count = board.move_number
        depth = int(sfen[sfen.index("depth") + 1])
        nodes = int(sfen[sfen.index("nodes") + 1])
        if nodes < 10000:
            nodes = str(nodes)
        elif nodes < 100000000:
            nodes = str(int(nodes / 10000)) + "万"
        else:
            nodes = str(int(nodes / 100000000)) + "億"
        if king_check():
            if reverse == 1:
                lwinratelabel["text"] = str(sente_points) + "点"
                rwinratelabel["text"] = str(gote_points) + "点"
                rightgraph["bd"] = 0
                leftgraph["bd"] = 0
                rightgraph["bg"] = "#FFFFFF"
                leftgraph["bg"] = "#FFFFFF"
            else:
                rwinratelabel["text"] = str(sente_points) + "点"
                lwinratelabel["text"] = str(gote_points) + "点"
                rightgraph["bd"] = 0
                leftgraph["bd"] = 0
                rightgraph["bg"] = "#FFFFFF"
                leftgraph["bg"] = "#FFFFFF"
        else:
            lwinratelabel["text"] = str(round(evals[0])) + "%"
            rwinratelabel["text"] = str(100 - round(evals[0])) + "%"
        try:
            j = [sfen[sfen.index("score") + 1], sfen[sfen.index("score") + 2], int(sfen[sfen.index("multipv") + 1]),
                 sfen[sfen.index("pv") + 1:]]
            pvs[int(sfen[sfen.index("multipv") + 1]) - 1] = sfen[sfen.index("pv") + 1]
            evals[int(sfen[sfen.index("multipv") + 1]) - 1] = cook(j)
        except Exception:
            if "multipv" not in sfen:
                j = [sfen[sfen.index("score") + 1], sfen[sfen.index("score") + 2], 1, sfen[sfen.index("pv") + 1:]]
                pvs[0] = sfen[sfen.index("pv") + 1]
                evals[0] = cook(j)
        if pvs and pvs[0] != "":
            best1["text"] = "１. " + KI2.move_to_ki2(board.move_from_usi(pvs[0]), board)
        if len(pvs) >= 2 and pvs[1] != "":
            best2["text"] = "２. " + KI2.move_to_ki2(board.move_from_usi(pvs[1]), board)
        if len(pvs) >= 3 and pvs[2] != "":
            best3["text"] = "３. " + KI2.move_to_ki2(board.move_from_usi(pvs[2]), board)
        if len(pvs) >= 4 and pvs[3] != "":
            best4["text"] = "４. " + KI2.move_to_ki2(board.move_from_usi(pvs[3]), board)
        if len(pvs) >= 5 and pvs[4] != "":
            best5["text"] = "５. " + KI2.move_to_ki2(board.move_from_usi(pvs[4]), board)
        if len(evals) >= 2 and evals[1] is not None and pvs[1]:
            if current_board_turn == -1:
                bestpc2["text"] = str(math.floor(evals[1]) - math.floor(evals[0])) + "%"
            else:
                bestpc2["text"] = str(math.floor(evals[1]) - math.floor(evals[0])) + "%"
            if math.floor(evals[1]) <= 10 and current_board_turn == 1:
                bestpc2["fg"] = dangercolor
            elif math.floor(evals[1]) >= 90 and current_board_turn == -1:
                bestpc2["fg"] = dangercolor
            else:
                bestpc2["fg"] = leftgraphbg
        if len(evals) >= 3 and evals[2] is not None and pvs[2]:
            if current_board_turn == -1:
                bestpc3["text"] = str(math.floor(evals[2]) - math.floor(evals[0])) + "%"
            else:
                bestpc3["text"] = str(math.floor(evals[2]) - math.floor(evals[0])) + "%"
            if math.floor(evals[2]) <= 10 and current_board_turn == 1:
                bestpc3["fg"] = dangercolor
            elif math.floor(evals[2]) >= 90 and current_board_turn == -1:
                bestpc3["fg"] = dangercolor
            else:
                bestpc3["fg"] = leftgraphbg
        if len(evals) >= 4 and evals[3] is not None and pvs[3]:
            if current_board_turn == -1:
                bestpc4["text"] = str(math.floor(evals[3]) - math.floor(evals[0])) + "%"
            else:
                bestpc4["text"] = str(math.floor(evals[3]) - math.floor(evals[0])) + "%"
            if math.floor(evals[3]) <= 10 and current_board_turn == 1:
                bestpc4["fg"] = dangercolor
            elif math.floor(evals[3]) >= 90 and current_board_turn == -1:
                bestpc4["fg"] = dangercolor
            else:
                bestpc4["fg"] = leftgraphbg
        if len(evals) >= 5 and evals[4] is not None and pvs[4]:
            if current_board_turn == -1:
                bestpc5["text"] = str(math.floor(evals[4]) - math.floor(evals[0])) + "%"
            else:
                bestpc5["text"] = str(math.floor(evals[4]) - math.floor(evals[0])) + "%"
            if math.floor(evals[4]) <= 10 and current_board_turn == 1:
                bestpc5["fg"] = dangercolor
            if math.floor(evals[4]) >= 90 and current_board_turn == -1:
                bestpc5["fg"] = dangercolor
            else:
                bestpc4["fg"] = leftgraphbg
        if len(pvs) > 0 and move_count == 1 and pvs[0] != "":
            saizen["text"] = "最善手: " + KI2.move_to_ki2(board.move_from_usi(pvs[0]), board)
        elif len(pvs) > 0 and pvs[0] != "":
            saizen["text"] = str(
                move_count - 1) + "手目" + strlastmove + "｜" + str(
                move_count) + "手目｜最善手：" + KI2.move_to_ki2(
                board.move_from_usi(pvs[0]), board)
        if evals and evals[0] is not None:
            if reverse == -1:
                leftgraph.place(x=25, y=65, width=1200 - round(evals[0]) * 12, height=20)
            elif reverse == 1:
                leftgraph.place(x=25, y=65, width=round(evals[0]) * 12, height=20)
        tansaku["text"] = engine + "｜深さ：" + str(depth) + "手｜" + nodes + "局面考慮中"
        if turn * reverse == 1:
            ltebanlabel["text"] = "手番"
            ltebanlabel["bg"] = "#C1272D"
            rtebanlabel["text"] = ""
            rtebanlabel["bg"] = bgcolor
        else:
            rtebanlabel["text"] = "手番"
            rtebanlabel["bg"] = "#C1272D"
            ltebanlabel["text"] = ""
            ltebanlabel["bg"] = bgcolor
        if king_check():
            leftgraph["bg"] = "#FFFFFF"
            rightgraph["bg"] = "#FFFFFF"
            leftgraph["bd"] = 0
            rightgraph["bd"] = 0


# コマンド受付と出力は並列処理(Tkinterとは別に動かす必要があるため)
t = threading.Thread(target=output, daemon=True)
t.start()

# 初期設定(isreadyまで)
while True:
    cmdline = input()
    if cmdline[:7] == "isready":
        usi(cmdline)
        break
    elif cmdline[:4] == "quit":
        sys.exit()
    usi(cmdline)

# isready後は並列処理
t2 = threading.Thread(target=command, daemon=True)
t2.start()

# Tkinter表示
root = tk.Tk()
root.configure(bg=bgcolor)
bar = tk.Toplevel(root)
bar.wm_attributes("-topmost", 1)
bar.geometry("1250x120")
bar.minsize(width=1250, height=120)
bar.configure(bg=bgcolor)
bar.title("Bar")
suggestionwindow = tk.Toplevel(root)
suggestionwindow.wm_attributes("-topmost", 1)
suggestionwindow.configure(bg=bgcolor)
suggestionwindow.geometry("900x106")
suggestionwindow.title("Best line")
suggestionlabel = tk.Label(suggestionwindow, text="", font=(barfont, 20), bg=bgcolor, fg="#000000")
suggestionlabel.place(x=25, y=25)
# 勝率ラベル
lwinratelabel = tk.Label(bar, text="50%", font=(barfont, 45), bg=bgcolor, fg=fgcolor)
lwinratelabel.place(x=25, y=27, anchor=tk.W)
rwinratelabel = tk.Label(bar, text="50%", font=(barfont, 45), bg=bgcolor, fg=fgcolor)
rwinratelabel.place(x=1225, y=27, anchor=tk.E)

# 手番ラベル
ltebanlabel = tk.Label(bar, text="", font=(barfont, 14), bg="#ffffff", fg="#ffffff")
ltebanlabel.place(x=25, y=100, anchor=tk.W)
rtebanlabel = tk.Label(bar, text="", font=(barfont, 14), bg="#ffffff", fg="#ffffff")
rtebanlabel.place(x=1225, y=100, anchor=tk.E)

# 最善手ラベル
saizen = tk.Label(bar, text="０手目｜最善手： ", font=(barfont, 20), bg=bgcolor, fg=fgcolor)
saizen.place(x=600, y=24, anchor=tk.CENTER)
# 探索ラベル
tansaku = tk.Label(bar, text="水匠５｜深さ：０手｜０局面考慮中", font=(percentfont, 12), bg=bgcolor, fg=fgcolor)
tansaku.place(x=600, y=100, anchor=tk.CENTER)

# 評価値バー描画
rightgraph = tk.Label(bar, text="", bg=rightgraphbg, relief=tk.SOLID, bd=3)
rightgraph.place(x=25, y=65, width=1200, height=20)
leftgraph = tk.Label(bar, text="", bg=leftgraphbg, relief=tk.SOLID, bd=3)
leftgraph.place(x=25, y=65, width=600, height=20)
bln = tk.BooleanVar()
bln.set(False)
check = tk.Checkbutton(bar, variable=bln, text="Reverse", font=(barfont, 15), bg=bgcolor, fg=fgcolor,
                       activeforeground=fgcolor)
check.place(x=50, y=150)
# 左右反転チェック
root.geometry("395x220")
root.wm_attributes("-topmost", 1)
root.minsize(width=380, height=220)
root.configure(bg=bgcolor)
root.title("Other moves")
best1 = tk.Label(root, text="１.", font=(percentfont, 20), bg=bgcolor, fg="#000000")
best2 = tk.Label(root, text="２.", font=(percentfont, 20), bg=bgcolor, fg="#000000")
best3 = tk.Label(root, text="３.", font=(percentfont, 20), bg=bgcolor, fg="#000000")
best4 = tk.Label(root, text="４.", font=(percentfont, 20), bg=bgcolor, fg="#000000")
best5 = tk.Label(root, text="５.", font=(percentfont, 20), bg=bgcolor, fg="#000000")
bestpc1 = tk.Label(root, text="-", font=(percentfont, 20), bg=bgcolor, fg="#000000")
bestpc2 = tk.Label(root, text="0%", font=(percentfont, 20), bg=bgcolor, fg="#000000")
bestpc3 = tk.Label(root, text="0%", font=(percentfont, 20), bg=bgcolor, fg="#000000")
bestpc4 = tk.Label(root, text="0%", font=(percentfont, 20), bg=bgcolor, fg="#000000")
bestpc5 = tk.Label(root, text="0%", font=(percentfont, 20), bg=bgcolor, fg="#000000")
best1.place(x=30, y=33, anchor=tk.W)
best2.place(x=30, y=73, anchor=tk.W)
best3.place(x=30, y=113, anchor=tk.W)
best4.place(x=30, y=153, anchor=tk.W)
best5.place(x=30, y=193, anchor=tk.W)
bestpc1.place(x=370, y=33, anchor=tk.E)
bestpc2.place(x=370, y=73, anchor=tk.E)
bestpc3.place(x=370, y=113, anchor=tk.E)
bestpc4.place(x=370, y=153, anchor=tk.E)
bestpc5.place(x=370, y=193, anchor=tk.E)

root.mainloop()
