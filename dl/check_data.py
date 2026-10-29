import sys

import numpy as np


# 從編碼後的盤面還原出：自己的棋子、對手的棋子、打劫點、氣數層（oneplane 沒有後兩項）
def decode(x):
    n = x.shape[0]
    if n == 1:
        return x[0] == 1, x[0] == -1, None, None
    if n == 7:  # sevenplane：0-2 自己、3-5 對手、6 打劫
        me_l, opp_l = x[0:3], x[3:6]
        return me_l.sum(0) > 0, opp_l.sum(0) > 0, x[6] > 0, (me_l, opp_l, 3)
    if n == 11:  # simple：0-3 黑、4-7 白、8/9 輪到黑/白、10 打劫
        black_l, white_l = x[0:4], x[4:8]
        black_to_move = x[8].min() == 1
        me_l, opp_l = (black_l, white_l) if black_to_move else (white_l, black_l)
        return me_l.sum(0) > 0, opp_l.sum(0) > 0, x[10] > 0, (me_l, opp_l, 4)
    if n == 10:  # tenplane：0 黑、1 白、2 不能下、3 輪到黑、4 全 1、5 空點、6-9 最近 4 手
        black, white = x[0] > 0, x[1] > 0
        black_to_move = x[3].min() == 1
        me, opp = (black, white) if black_to_move else (white, black)
        return me, opp, None, None
    raise ValueError('不認得的層數：%d' % n)


COMMON = ['題目和答案數量不同', '題目出現不該有的數值', '答案不是每列剛好一個 1 的 one-hot',
          '同一格同時有自己和對手的棋子', '空棋盤（可能是假樣本）', '答案下在已經有棋子的位置']
LIBERTY = ['一顆棋子出現在多個氣數層', '答案下在打劫不能下的位置', '打劫層標在有棋子的位置',
           '氣數層跟實際算出來的氣數不一致']
TENPLANE = ['不能下的層沒有涵蓋所有棋子', '答案下在不能下的位置', '空點層跟棋子位置不一致',
            '全 1 的層不是每格都是 1', '輪到誰的層不是整層一樣', '最近一手的層不只一個 1']
CHECKS = {
    1: COMMON,
    7: COMMON + LIBERTY,
    11: COMMON + LIBERTY + ['輪到誰的兩層（8、9）不正確'],
    10: COMMON + TENPLANE,
}


# 每顆棋子所屬那串棋的氣數
def liberties(stones, empty):
    h, w = stones.shape
    out = np.zeros((h, w), int)
    seen = np.zeros((h, w), bool)
    for r in range(h):
        for c in range(w):
            if not stones[r, c] or seen[r, c]:
                continue
            group, libs, stack = [], set(), [(r, c)]
            seen[r, c] = True
            while stack:
                a, b = stack.pop()
                group.append((a, b))
                for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    na, nb = a + da, b + db
                    if 0 <= na < h and 0 <= nb < w:
                        if empty[na, nb]:
                            libs.add((na, nb))
                        elif stones[na, nb] and not seen[na, nb]:
                            seen[na, nb] = True
                            stack.append((na, nb))
            for a, b in group:
                out[a, b] = len(libs)
    return out


def main(feature_path, label_path):
    X, Y = np.load(feature_path), np.load(label_path)
    print('features', X.shape, X.dtype, ' labels', Y.shape, Y.dtype)
    N, planes, H, W = X.shape
    fails = {}

    def fail(name, i):
        fails.setdefault(name, []).append(i)

    # 格式
    if len(Y) != N:
        fail('題目和答案數量不同', -1)
    allowed = {-1.0, 0.0, 1.0} if planes == 1 else {0.0, 1.0}
    if not set(np.unique(X).tolist()) <= allowed:
        fail('題目出現不該有的數值', -1)
    if Y.ndim != 2 or Y.shape[1] != H * W or not np.all(Y.sum(1) == 1) \
            or not set(np.unique(Y).tolist()) <= {0.0, 1.0}:
        fail('答案不是每列剛好一個 1 的 one-hot', -1)
    answers = Y.argmax(1)

    prev = None
    continuity_ok = continuity_total = 0
    recent_ok = recent_total = 0
    for i in range(N):
        x = X[i]
        me, opp, ko, lib = decode(x)
        r, c = divmod(int(answers[i]), W)
        if (me & opp).any():
            fail('同一格同時有自己和對手的棋子', i)
        if lib is not None and ((lib[0].sum(0) > 1) | (lib[1].sum(0) > 1)).any():
            fail('一顆棋子出現在多個氣數層', i)
        if planes == 11:
            t8, t9 = x[8], x[9]
            if not ((t8.min() == 1 and t9.max() == 0) or (t9.min() == 1 and t8.max() == 0)):
                fail('輪到誰的兩層（8、9）不正確', i)
        if not (me | opp).any():
            fail('空棋盤（可能是假樣本）', i)
        if me[r, c] or opp[r, c]:
            fail('答案下在已經有棋子的位置', i)
        if ko is not None:
            if ko[r, c]:
                fail('答案下在打劫不能下的位置', i)
            if (ko & (me | opp)).any():
                fail('打劫層標在有棋子的位置', i)
        # 從棋子位置重新算氣數，跟氣數層比對
        if lib is not None:
            me_l, opp_l, top = lib
            empty = ~(me | opp)
            for stones, layers in ((me, me_l), (opp, opp_l)):
                real = np.minimum(liberties(stones, empty), top)
                coded = np.zeros((H, W), int)
                for k in range(top):
                    coded[layers[k] > 0] = k + 1
                if (real[stones] != coded[stones]).any():
                    fail('氣數層跟實際算出來的氣數不一致', i)
                    break
        if planes == 10:
            stones = me | opp
            if (stones & ~(x[2] > 0)).any():
                fail('不能下的層沒有涵蓋所有棋子', i)
            if x[2][r, c]:
                fail('答案下在不能下的位置', i)
            if ((x[5] > 0) != ~stones).any():
                fail('空點層跟棋子位置不一致', i)
            if x[4].min() != 1:
                fail('全 1 的層不是每格都是 1', i)
            if x[3].min() != x[3].max():
                fail('輪到誰的層不是整層一樣', i)
            if (x[6:10].reshape(4, -1).sum(1) > 1).any():
                fail('最近一手的層不只一個 1', i)
        # 連續性：上一手的落子，在這一個盤面上應該是「對手」的棋子
        if prev is not None:
            p_r, p_c = prev
            continuity_total += 1
            if opp[p_r, p_c]:
                continuity_ok += 1
            if planes == 10:
                recent_total += 1
                if x[6][p_r, p_c] == 1 and x[6].sum() == 1:
                    recent_ok += 1
        prev = (r, c)

    print()
    for name in CHECKS[planes]:
        bad = fails.get(name, [])
        print(('OK  ' if not bad else 'FAIL') + '  ' + name
              + ('' if not bad else '：%d 個，例如第 %s 個' % (len(bad), bad[:5])))
    print('連續性：%d / %d 個盤面，上一手的落子有出現在下一個盤面上'
          '（對不上的通常是換到下一盤棋，或中間有 pass）' % (continuity_ok, continuity_total))
    if planes == 10:
        print('最近一手：%d / %d 個盤面，「最近一手」層剛好標在上一個答案的位置'
              '（對不上的原因同上）' % (recent_ok, recent_total))
    return 1 if fails else 0


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('用法：uv run python check_data.py <features.npy> <labels.npy>')
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
