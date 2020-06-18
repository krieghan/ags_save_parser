import argparse

from ags_save_parser import saved_game
import compare_saves

def report_honor(save_game):
    return save_game['scripts']['modules'][1][1][3076]


def main():
    parser = argparse.ArgumentParser(description='Parse Save File')
    parser.add_argument(
        '--file',
        dest='file',
        default='/home/krieghan/hq_saves/agssave.000.hqthor')

    args = parser.parse_args()

    save_game = saved_game.get_save_game(
            args.file,
            num_characters=69)
    honor = report_honor(save_game)
    print ("Honor is {}".format(honor))



if __name__ == '__main__':
    main()
