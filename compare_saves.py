import argparse

from ags_save_parser import saved_game

def report_mismatch(compare_result_list):
    report = []
    for i in range(len(compare_result_list)):
        value = compare_result_list[i]
        if value != '_':
            report.append((i, value))
    return report

def report_mismatch_for_module(
        modules_1,
        modules_2,
        index):
    module_1 = modules_1[index]
    module_2 = modules_2[index]
    if len(module_1) != 2 or len(module_2) != 2:
        raise AssertionError(
            "Module {}, value {}, has length {}".format(
                index,
                module_1,
                len(module_1)))
    print('Module {}\n'.format(index))
    print(report_mismatch(modules_1[index][1]))
    print(report_mismatch(modules_2[index][1]))
    print()

def report_mismatch_all_modules(result):
    scripts_1 = result[0]['scripts']
    scripts_2 = result[1]['scripts']
    modules_1 = scripts_1['modules']
    modules_2 = scripts_2['modules']
    
    print('Global Data:\n')
    print(report_mismatch(scripts_1['global_data']))
    print(report_mismatch(scripts_2['global_data']))
    print()

    for i in range(len(scripts_1['modules'])):
        try:
            report_mismatch_for_module(
                modules_1,
                modules_2,
                i)
        except AssertionError:
            print('Module {} was a match'.format(i))

def report_honor(save_game_1, save_game_2):
    print("Honor is 1 is {}".format(
        save_game_1['scripts']['modules'][1][1][3076]))
    print("Honor is 2 is {}".format(
        save_game_2['scripts']['modules'][1][1][3076]))
    


def main():
    parser = argparse.ArgumentParser(description='Parse Save File')
    parser.add_argument(
        '--file1',
        dest='file1',
        default='/home/krieghan/hq_saves/agssave.000.hqthor')
    parser.add_argument(
        '--file2',
        dest='file2',
        default='/home/krieghan/hq_saves/agssave.001.hqthor')
    parser.add_argument(
        '--full',
        dest='full',
        action='store_true',
        default=False)
    parser.add_argument(
        '--catch-transition',
        default=None)
    parser.add_argument(
        '--honor',
        action='store_true',
        default=False)

    args = parser.parse_args()
    save_game_1 = saved_game.get_save_game(args.file1, num_characters=69)
    save_game_2 = saved_game.get_save_game(args.file2, num_characters=69)
    
    from kobold import compare

    result = compare.compare(save_game_1, save_game_2, type_compare='full')
    modules_1 = result[0]['scripts']['modules']
    modules_2 = result[1]['scripts']['modules']
    stat_module_1 = modules_1[1][1]
    stat_module_2 = modules_2[1][1]

    if args.honor:
        report_honor(save_game_1, save_game_2)
    elif args.catch_transition is not None:
        pass
    elif args.full:
        report_mismatch_all_modules(result)
    else:
        report_mismatch_for_module(1)


if __name__ == '__main__':
    main()

