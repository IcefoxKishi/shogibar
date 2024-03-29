import math
import sys
from cshogi import *
from cshogi import KI2
import threading
import subprocess
import tkinter as tk
from PIL import ImageTk, Image

# エンジン名・フォント・文字色・背景色
engine = "Suisho 5"  # 水匠5
barfont = "Noto Sans JP"  # BIZ UDGothic
percentfont = "Noto Sans JP"  # BIZ UDGothic
bgcolor = "white"  # white
fgcolor = "black"
dangercolor = "#990000"  # black
turnfgcolor = "#00007f"  # #00007f
leftgraphbg = "#000000"  # #000000
rightgraphbg = "#ffffff"  # #ffffff
warutecolor = "#ff00ff"
strlastmove = ""
sente_image = Image.open("sente.png")
gote_image = Image.open("gote.png")
evals = [0, 0, 0, 0, 0]
piece_points = [0, 1, 1, 1, 1, 5, 5, 1, 0, 1, 1, 1, 1, 5, 5, 0, 0, 1, 1, 1, 1, 5, 5, 1, 0, 1, 1, 1, 1, 5, 5]
gote_points = 0
sente_points = 0
sente_camp = []
gote_camp = []
pvs = ["", "", "", "", ""]
current_board_turn = 1
values = []


def cook(c):
    eval = int(c[1])
    if c[0] == "mate":
        if eval * current_board_turn < 0:
            if c[2] == 1:
                tsumelabel["text"] = "Gote victory - Checkmate in " + str(abs(eval)) + " moves"
            return 1
        else:
            if c[2] == 1:
                tsumelabel["text"] = "Sente victory - Checkmate in " + str(abs(eval)) + " moves"
            return 99
    else:
        cureval = 100 / (1 + math.exp(eval * current_board_turn / -600))
        if cureval < 1:
            return 1
        if cureval > 99:
            return 99
        else:
            return cureval


def update():
    snamel['text'] = sente_name.get()
    srankl['text'] = sente_rank.get()
    grankl['text'] = gote_rank.get()
    gnamel['text'] = gote_name.get()


bestpercent = ""
bestpercent2 = ""

# 外部エンジン起動
shogi = subprocess.Popen("./Suisho5.exe", stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         encoding="UTF-8")
board = Board()
scrap = Board()

piece_in_hand_value = [1, 1, 1, 1, 1, 5, 5]


def king_check():
    if 8 in gote_camp and 24 in sente_camp:
        return True
    else:
        return False


def board_turn(c):
    if c == 0:
        return 1
    if c == 1:
        return -1


def command():
    while True:
        cmdline = input()
        # 局面設定
        if cmdline[:8] == "position":
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
            tsumelabel["text"] = ""
            global scrap
            if board.history:
                scrap.set_position(cmdline[9:][:-5])
                last_move = board.history[-1]
            global strlastmove
            if board.history:
                strlastmove = KI2.move_to_ki2(last_move, scrap)
            prev = cmdline.split()
            prev.pop(0)
            best1["text"] = "1. "
            best2["text"] = "2. "
            best3["text"] = "3. "
            best4["text"] = "4. "
            best5["text"] = "5. "
            bestpc1["text"] = ""
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
            current_board_turn = board_turn(board.turn)
            bestpc3["fg"] = "#000000"
            bestpc2["fg"] = "#000000"
            bestpc4["fg"] = "#000000"
            bestpc5["fg"] = "#000000"
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
        else:
            rightgraph["bg"] = leftgraphbg
            leftgraph["bg"] = rightgraphbg
        turn = -(board.turn * 2 - 1) * reverse
        move_count = board.move_number
        depth = int(sfen[sfen.index("depth") + 1])
        nodes = int(sfen[sfen.index("nodes") + 1])
        if nodes < 1000000:
            nodes = str(nodes)
        elif nodes < 1000000000:
            nodes = str(int(nodes / 1000000)) + " million"
        else:
            nodes = str(int(nodes / 1000000000)) + " billion"
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
            j = [sfen[sfen.index("score") + 1], sfen[sfen.index("score") + 2], int(sfen[sfen.index("multipv") + 1])]
            pvs[int(sfen[sfen.index("multipv") + 1]) - 1] = sfen[sfen.index("pv") + 1]
            evals[int(sfen[sfen.index("multipv") + 1]) - 1] = cook(j)
        except Exception as error:
            print(error)
            if "multipv" not in sfen:
                j = [sfen[sfen.index("score") + 1], sfen[sfen.index("score") + 2], 1]
                pvs[0] = sfen[sfen.index("pv") + 1]
                evals[0] = cook(j)
        if pvs and pvs[0] != "":
            best1["text"] = "1. " + KI2.move_to_ki2(board.move_from_usi(pvs[0]), board)
        if len(pvs) >= 2 and pvs[1] != "":
            best2["text"] = "2. " + KI2.move_to_ki2(board.move_from_usi(pvs[1]), board)
        if len(pvs) >= 3 and pvs[2] != "":
            best3["text"] = "3. " + KI2.move_to_ki2(board.move_from_usi(pvs[2]), board)
        if len(pvs) >= 4 and pvs[3] != "":
            best4["text"] = "4. " + KI2.move_to_ki2(board.move_from_usi(pvs[3]), board)
        if len(pvs) >= 5 and pvs[4] != "":
            best5["text"] = "5. " + KI2.move_to_ki2(board.move_from_usi(pvs[4]), board)
        if evals and evals[0] is not None:
            if current_board_turn == 1:
                bestpc1["text"] = str(round(evals[0])) + "%"
            else:
                bestpc1["text"] = str(100 - round(evals[0])) + "%"
        if len(evals) >= 2 and evals[1] is not None and pvs[1]:
            if current_board_turn == -1:
                bestpc2["text"] = "-" + str(math.floor(evals[1]) - math.floor(evals[0])) + "%"
            else:
                bestpc2["text"] = str(math.floor(evals[1]) - math.floor(evals[0])) + "%"
        if len(evals) >= 3 and evals[2] is not None and pvs[2]:
            if current_board_turn == -1:
                bestpc3["text"] = "-" + str(math.floor(evals[2]) - math.floor(evals[0])) + "%"
            else:
                bestpc3["text"] = str(math.floor(evals[2]) - math.floor(evals[0])) + "%"
        if len(evals) >= 4 and evals[3] is not None and pvs[3]:
            if current_board_turn == -1:
                bestpc4["text"] = "-" + str(math.floor(evals[3]) - math.floor(evals[0])) + "%"
            else:
                bestpc4["text"] = str(math.floor(evals[3]) - math.floor(evals[0])) + "%"
        if len(evals) >= 5 and evals[4] is not None and pvs[4]:
            if current_board_turn == -1:
                bestpc5["text"] = "-" + str(math.floor(evals[4]) - math.floor(evals[0])) + "%"
            else:
                bestpc5["text"] = str(math.floor(evals[4]) - math.floor(evals[0])) + "%"
        if len(pvs) > 0 and move_count == 1 and pvs[0] != "":
            saizen["text"] = "Move " + str(move_count) + " | Best move: " + KI2.move_to_ki2(
                board.move_from_usi(pvs[0]), board)
        elif len(pvs) > 0 and pvs[0] != "":
            saizen["text"] = "Last move: " + strlastmove + " | Move " + str(
                move_count) + " | Best move: " + KI2.move_to_ki2(board.move_from_usi(pvs[0]), board)
        if evals and evals[0] is not None:
            leftgraph.place(x=300, y=65, width=round(evals[0]) * 12, height=20)
        tansaku["text"] = engine + " | Depth: " + str(depth) + " moves | " + nodes + " nodes"
        if turn == 1 and ltebanlabel["text"] != "Turn":
            ltebanlabel["text"] = "Turn"
            ltebanlabel["bg"] = "#C1272D"
            rtebanlabel["text"] = ""
            rtebanlabel["bg"] = "#ffffff"
        elif turn == -1 and rtebanlabel["text"] != "Turn":
            rtebanlabel["text"] = "Turn"
            rtebanlabel["bg"] = "#C1272D"
            ltebanlabel["text"] = ""
            ltebanlabel["bg"] = "#ffffff"
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
root.title("configure names")
root.configure(bg=bgcolor)
bar = tk.Toplevel(root)
bar.wm_attributes("-topmost", 1)
bar.geometry("1800x120")
bar.minsize(width=1800, height=120)
bar.configure(bg=bgcolor)
bar.title("Thanh đánh giá")
# 勝率ラベル
lwinratelabel = tk.Label(bar, text="50%", font=(percentfont, 45), bg=bgcolor, fg=fgcolor)
lwinratelabel.place(x=300, y=33, anchor=tk.W)
rwinratelabel = tk.Label(bar, text="50%", font=(percentfont, 45), bg=bgcolor, fg=fgcolor)
rwinratelabel.place(x=1495, y=33, anchor=tk.E)

# mate label
tsumelabel = tk.Label(bar, text="", font=(barfont, 14), bg=bgcolor, fg=fgcolor)
tsumelabel.place(x=605, y=50, anchor=tk.CENTER)

# 手番ラベル
ltebanlabel = tk.Label(bar, text="", font=(barfont, 14), bg="#ffffff", fg="#ffffff")
ltebanlabel.place(x=300, y=100, anchor=tk.W)
rtebanlabel = tk.Label(bar, text="", font=(barfont, 14), bg="#ffffff", fg="#ffffff")
rtebanlabel.place(x=1495, y=100, anchor=tk.E)

# 最善手ラベル
saizen = tk.Label(bar, text="Move 0 | Best move: ", font=(barfont, 15), bg=bgcolor, fg=fgcolor)
saizen.place(x=870, y=24, anchor=tk.CENTER)
# 探索ラベル
tansaku = tk.Label(bar, text="Suisho 5 | Depth: 0 moves | 0 nodes", font=(barfont, 12), bg=bgcolor, fg=fgcolor)
tansaku.place(x=905, y=100, anchor=tk.CENTER)

# 評価値バー描画
rightgraph = tk.Label(bar, text="", bg=rightgraphbg, relief=tk.SOLID, bd=3)
rightgraph.place(x=300, y=65, width=1200, height=20)
leftgraph = tk.Label(bar, text="", bg=leftgraphbg, relief=tk.SOLID, bd=3)
leftgraph.place(x=300, y=65, width=600, height=20)
bln = tk.BooleanVar()
bln.set(False)
check = tk.Checkbutton(bar, variable=bln, text="Reverse", font=(barfont, 15), bg=bgcolor, fg=fgcolor,
                       activeforeground=fgcolor)
check.place(x=50, y=150)
# 左右反転チェック

sframe = tk.Frame(bar, width=65, height=75)
sframe.configure(bg='white', borderwidth=0, highlightthickness=0)
gframe = tk.Frame(bar, width=65, height=75)
gframe.configure(bg='white', borderwidth=0, highlightthickness=0)
sframe.pack()
gframe.pack()
sframe.place(x=0, y=0)
gframe.place(x=1720, y=0)
simg = ImageTk.PhotoImage(sente_image.resize((80, 120)))
gimg = ImageTk.PhotoImage(gote_image.resize((80, 120)))
slabel = tk.Label(sframe, image=simg)
slabel.pack()
glabel = tk.Label(gframe, image=gimg)
glabel.pack()
sente_name = tk.Entry(root)
gote_name = tk.Entry(root)
sente_rank = tk.Entry(root)
gote_rank = tk.Entry(root)
srankl = tk.Label(bar, text="", font=(percentfont, 12), bg=bgcolor, fg=fgcolor, justify='left')
snamel = tk.Label(bar, text="", font=(percentfont, 15), bg=bgcolor, fg=fgcolor, justify='left')
grankl = tk.Label(bar, text="", font=(percentfont, 12), bg=bgcolor, fg=fgcolor, justify='right')
gnamel = tk.Label(bar, text="", font=(percentfont, 15), bg=bgcolor, fg=fgcolor, justify="right")
snamel.place(x=85, y=35)
srankl.place(x=85, y=70)
gnamel.place(x=1520, y=35)
grankl.place(x=1520, y=70)
tk.Label(root, text='Sente name (max 5 char)').grid(row=0)
tk.Label(root, text='Gote name (max 5 char)').grid(row=1)
tk.Label(root, text='Sente rank (max 2 char)').grid(row=2)
tk.Label(root, text='Gote rank (max 2 char)').grid(row=3)
tk.Button(root, text='Update', command=update).grid(row=4)
sente_name.grid(row=0, column=1)
gote_name.grid(row=1, column=1)
sente_rank.grid(row=2, column=1)
gote_rank.grid(row=3, column=1)
bestmoves = tk.Toplevel(root)
bestmoves.geometry("380x220")
bestmoves.wm_attributes("-topmost", 1)
bestmoves.minsize(width=380, height=220)
bestmoves.configure(bg=bgcolor)
bestmoves.title("Các nước đi khác")
best1 = tk.Label(bestmoves, text="1.", font=(percentfont, 20), bg=bgcolor, fg=fgcolor)
best2 = tk.Label(bestmoves, text="2.", font=(percentfont, 20), bg=bgcolor, fg=fgcolor)
best3 = tk.Label(bestmoves, text="3.", font=(percentfont, 20), bg=bgcolor, fg=fgcolor)
best4 = tk.Label(bestmoves, text="4.", font=(percentfont, 20), bg=bgcolor, fg=fgcolor)
best5 = tk.Label(bestmoves, text="5.", font=(percentfont, 20), bg=bgcolor, fg=fgcolor)
bestpc1 = tk.Label(bestmoves, text="", font=(percentfont, 20), bg=bgcolor, fg=fgcolor)
bestpc2 = tk.Label(bestmoves, text="0%", font=(percentfont, 20), bg=bgcolor, fg=fgcolor)
bestpc3 = tk.Label(bestmoves, text="0%", font=(percentfont, 20), bg=bgcolor, fg=fgcolor)
bestpc4 = tk.Label(bestmoves, text="0%", font=(percentfont, 20), bg=bgcolor, fg=fgcolor)
bestpc5 = tk.Label(bestmoves, text="0%", font=(percentfont, 20), bg=bgcolor, fg=fgcolor)
best1.place(x=50, y=33, anchor=tk.W)
best2.place(x=50, y=73, anchor=tk.W)
best3.place(x=50, y=113, anchor=tk.W)
best4.place(x=50, y=153, anchor=tk.W)
best5.place(x=50, y=193, anchor=tk.W)
bestpc1.place(x=350, y=33, anchor=tk.E)
bestpc2.place(x=350, y=73, anchor=tk.E)
bestpc3.place(x=350, y=113, anchor=tk.E)
bestpc4.place(x=350, y=153, anchor=tk.E)
bestpc5.place(x=350, y=193, anchor=tk.E)

root.mainloop()
