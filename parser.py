import argparse
import pickle

from ags_save_parser import (
    cursor as cursor_module,
    saved_game)


def main():
    parser = argparse.ArgumentParser(description='Parse Save File')
    parser.add_argument(
        '--file',
        dest='file',
        default='/home/krieghan/hq_saves/agssave.000.hqthor')
    parser.add_argument(
        '--file2',
        dest='file2',
        default='/home/krieghan/hq_saves/agssave.001.hqthor')

    args = parser.parse_args()
    save_game_1 = saved_game.get_save_game(
            args.file,
            num_characters=69)
    breakpoint()
    print()



if __name__ == '__main__':
    main()
