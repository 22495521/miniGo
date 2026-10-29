import random

from dlgo.gotypes import Player, Point

# 產生 dlgo/zobrist.py：每個 (點, 顏色) 對應一個隨機 64-bit 雜湊值
MAX63 = 0x7fffffffffffffff
MAX_BOARD_SIZE = 19


def main():
    lines = [
        'from dlgo.gotypes import Player, Point',
        '',
        "__all__ = ['HASH_CODE', 'EMPTY_BOARD']",
        '',
        'HASH_CODE = {',
    ]
    for row in range(1, MAX_BOARD_SIZE + 1):
        for col in range(1, MAX_BOARD_SIZE + 1):
            # None 是空點，goboard_fast.py 會用到
            for state in (None, Player.black, Player.white):
                code = random.randint(0, MAX63)
                lines.append('    (%r, %s): %r,' % (Point(row, col), state, code))
    lines.append('}')
    lines.append('')
    lines.append('EMPTY_BOARD = 0')

    with open('dlgo/zobrist.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
