import cshogi
from cshogi import Board, KIF, move_to, move_cap, move_from, move_is_drop, move_is_promotion, move_from_piece_type, move_drop_hand_piece, hand_piece_to_piece_type

KTKW_PIECES = ["", "歩", "香", "桂", "銀", "角", "飛", "金", "玉", "と", "+香", "+桂", "+銀", "馬", "竜"]
KTKW_HAND_PIECES = ["歩", "香", "桂", "銀", "金", "角", "飛"]

def move_to_ktkw(move: int, board: Board) -> str:
    kifu_turn = '☗' if board.turn == cshogi.BLACK else '☖'
    to_square_str = KIF.KIFU_FROM_SQUARE_NAMES[move_to(move)]
    move_marker = ""
    is_same_square = False
    if board.peek() != cshogi.MOVE_NONE:
        if move_to(board.peek()) == move_to(move):
            is_same_square = True
    if move_is_drop(move):
        move_marker = "*"
        piece_type_str = KTKW_PIECES[hand_piece_to_piece_type(move_drop_hand_piece(move))]
        move_str = "{}{}{}{}".format(
            kifu_turn,
            piece_type_str,
            move_marker,
            to_square_str
        )
    else:
        if move_cap(move) != 0:
            move_marker = "x"
        else:
            move_marker = "-"
        from_square = move_from(move)
        from_square_str = KIF.KIFU_FROM_SQUARE_NAMES[from_square]
        piece_type = move_from_piece_type(move)
        piece_type_str = KTKW_PIECES[piece_type]
        candidates = []
        promotion = {}
        for move2 in board.pseudo_legal_moves:
            if move_to(move2) == move_to(move) and not move_is_drop(move2) and move_from_piece_type(move2) == piece_type:
                from_square2 = move_from(move2)
                if from_square2 in promotion:
                    promotion[from_square2] += 1
                    continue
                promotion[from_square2] = 1
                candidates.append(move2)
        if len(candidates) > 1:
            move_str = '{}{}({}){}{}{}'.format(
                kifu_turn,
                piece_type_str,
                from_square_str,
                move_marker,
                to_square_str if not is_same_square else "",
                "+" if move_is_promotion(move) else ("=" if promotion[from_square] == 2 else "")
            )
        else:
            move_str = '{}{}{}{}{}'.format(
                kifu_turn,
                piece_type_str,
                move_marker,
                to_square_str if not is_same_square else "",
                "+" if move_is_promotion(move) else ("=" if promotion[from_square] == 2 else "")
            )
    return move_str