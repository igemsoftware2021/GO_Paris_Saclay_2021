import itertools
import multiprocessing
from math import factorial

from arn import Arn, arn_to_str
from log import Log


def compare_strict_arn(arn1: Arn, arn2: Arn, logger: Log):
    sequence_1 = arn1.get_sequence_str()
    sequence_2 = arn2.get_sequence_str()

    size_sequence_1 = len(sequence_1)
    size_sequence_2 = len(sequence_2)

    nb_error = 0
    for i in range(0, size_sequence_1):
        if size_sequence_1 != size_sequence_2 and (i in (size_sequence_1, size_sequence_2)):
            logger.warning(f'{sequence_1:26} | {sequence_2:26} ===> '
                           f'Error: {"Bad size sequences":30} => sequence val 1 : {sequence_1[i]:1} vs '
                           f'sequence val 2 : {" ":1} ==> at position {i:10d}')
            nb_error = nb_error + 1
            break

        if sequence_1[i] != sequence_2[i]:
            logger.warning(f'{sequence_1:26} | {sequence_2:26} ===> '
                           f'Error: {"Bad value":30} => sequence val 1 : {sequence_1[i]:1} vs '
                           f'sequence val 2 : {sequence_2[i]:1} ==> at position {i:10d}')
            nb_error = nb_error + 1

    if nb_error > 0:
        logger.warning(f'{sequence_1:26} | {sequence_2:26} ===> '
                       f'Number of errors while analyse sequences =>  {nb_error:1d}')


def compare_line_arn(
        arn1: Arn, arn2: Arn,
        logger: Log, add_space_sequence_1: bool = False,
        error_percent: int = 30
):
    copy_sequence_1 = arn1.get_sequence_str()
    copy_sequence_2 = arn2.get_sequence_str()

    original_size_sequence_1 = len(copy_sequence_1)
    original_size_sequence_2 = len(copy_sequence_2)

    min_size_sequence = original_size_sequence_2
    if original_size_sequence_2 > original_size_sequence_1:
        min_size_sequence = original_size_sequence_1

    for j in range(0, original_size_sequence_1):
        if j > 0:
            if add_space_sequence_1:
                copy_sequence_1 = " " + copy_sequence_1
            else:
                copy_sequence_2 = " " + copy_sequence_2

        size_sequence_1 = len(copy_sequence_1)
        size_sequence_2 = len(copy_sequence_2)

        nb_error_imbricate = 0
        for i in range(0, size_sequence_2):
            if size_sequence_1 != size_sequence_2 and \
                    (i + 1 == size_sequence_1 or i + 1 == size_sequence_2):
                break
            if is_can_be_imbriquate(copy_sequence_1[i], copy_sequence_2[i]):
                logger.warning(f'{copy_sequence_1:26} | {copy_sequence_2:26} ===> '
                               f'Error: {"Bad value":30} => sequence val 1 : {copy_sequence_1[i]:1} vs '
                               f'sequence val 2 : {copy_sequence_2[i]:1} ==> at position {i:10d}')
                nb_error_imbricate = nb_error_imbricate + 1

        percent = nb_error_imbricate / min_size_sequence * 100

        if percent > error_percent:
            logger.error(f'{copy_sequence_1:26} | {copy_sequence_2:26} ===> '
                         f'Bad combination : {percent:1.02f}%')


def compare_loop_arn(
        arn1: Arn, arn2: Arn,
        logger: Log, error_percent: int = 30,
        nb_process=2
):
    copy_sequence_1 = arn1.get_sequence_list()
    copy_sequence_2 = arn2.get_sequence_list()

    size_sequence1 = len(copy_sequence_1)
    size_sequence2 = len(copy_sequence_1)

    min_size_sequence = size_sequence2
    if size_sequence2 > size_sequence1:
        min_size_sequence = size_sequence1

    if nb_process == 1:
        for sequence1 in __permutations__(copy_sequence_1):
            for sequence2 in __permutations__(copy_sequence_2):
                _compare_loop_arn_sequence_(
                    sequence1, sequence2,
                    min_size_sequence, logger, error_percent
                )
    else:
        nb_stock = 100000
        # print(factorial(size_sequence1))
        # 25 factorielle
        # 25 852 016 738 884 976 640 000
        for sequence1 in __permutations__(copy_sequence_1):
            tab_sequence2 = []
            for sequence2 in __permutations__(copy_sequence_2):
                tab_sequence2.append(sequence2)
                if len(tab_sequence2) >= nb_stock:
                    __compare_sequence_by_list_on_async__(
                        sequence1, tab_sequence2,
                        min_size_sequence, logger, error_percent,
                        nb_process, nb_stock
                    )
                    tab_sequence2 = []
            if len(tab_sequence2) > 0:
                __compare_sequence_by_list_on_async__(
                    sequence1, tab_sequence2,
                    min_size_sequence, logger, error_percent,
                    nb_process, nb_stock
                )


def __compare_sequence_by_list_on_async__(
        sequence1, tab_sequence2,
        min_size_sequence, logger,
        error_percent, nb_process,
        nb_stock
):
    with multiprocessing.Pool(processes=nb_process, maxtasksperchild=nb_stock) as pool_process:
        for seq_tmp in tab_sequence2:
            pool_process.apply_async(
                _compare_loop_arn_sequence_,
                [sequence1, seq_tmp, min_size_sequence, logger, error_percent]
            )
        pool_process.close()
        pool_process.join()


def _compare_loop_arn_sequence_(sequence1, sequence2, min_size_sequence, logger, error_percent):
    seq_1_position_history = []

    seq1_str = arn_to_str(sequence1)
    seq2_str = arn_to_str(sequence2)

    for k in range(0, len(sequence1)):
        seq_1_position_history.append(sequence1[k].original_position)
        nb_imbricate = 0
        seq_2_position_history = []
        for l in range(0, len(sequence2)):
            logger.debug(f'Process {seq1_str:26} | {seq2_str:26}')
            seq_2_position_history.append(sequence2[l].original_position)

            if is_can_be_imbriquate(sequence1[k].value, sequence2[l].value):
                if max(seq_2_position_history) > sequence2[l].original_position or \
                        max(seq_1_position_history) > sequence1[k].original_position:
                    return
                nb_imbricate = nb_imbricate + 1

        percent = nb_imbricate / min_size_sequence * 100

        if percent > error_percent:
            logger.debug(f'{seq1_str:26} | {seq2_str:26} ===> Bad combination : {percent:1.02f}%')


def is_can_be_imbriquate(val1: str, val2: str):
    if val1 == "A" and val2 == "U":
        is_imbricate = True
    elif val1 == "C" and val2 == "G":
        is_imbricate = True
    else:
        is_imbricate = False
    return is_imbricate


def __permutations__(list_to_permute: list):
    return itertools.permutations(list_to_permute, len(list_to_permute))
