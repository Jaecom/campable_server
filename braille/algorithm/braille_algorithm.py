import re
from copy import copy

from .Math_to_Braille import functions_for_translation as fft


def convert_file_to_braille(problem):
    PATTERN_OF_MATH_PART = re.compile(r"\\[(].+?\\[)]|\\[[].+?\\[]]", re.DOTALL)
    math_list = []  # 수식 부분을 저장할 리스트
    only_variable_list = []  # 미지수(알파벳)로만 구성된 단항식 부분을 저장할 리스트

    ## 콤마 처리하기
    preprocessed_problem = PATTERN_OF_MATH_PART.sub(fft.comma, problem)
    preprocessed_problem_copy = copy(preprocessed_problem)

    # 미지수로만 구성된 단항식을 문제 텍스트에서 분리한다
    PATTERN_OF_VARIABLE_PART = re.compile(
        r"\\[(][a-zA-Z]+?,?\\[)]|\\[[][a-zA-Z]+?,?\\[]]", re.DOTALL
    )
    variable_part_matches = PATTERN_OF_VARIABLE_PART.finditer(preprocessed_problem)
    for i, j in enumerate(variable_part_matches):
        starting, ending = j.span()
        only_variable_list.append(preprocessed_problem[(starting + 2) : (ending - 2)])
        preprocessed_problem_copy = PATTERN_OF_VARIABLE_PART.sub(
            f"variable{i}", preprocessed_problem_copy, 1
        )

    twice_preprocessed_problem = preprocessed_problem_copy
    twice_preprocessed_problem_copy = copy(twice_preprocessed_problem)

    # 수식 부분 분리하기
    math_part_matches = PATTERN_OF_MATH_PART.finditer(twice_preprocessed_problem)
    for i, j in enumerate(math_part_matches):
        starting, ending = j.span()
        math_list.append(twice_preprocessed_problem[(starting + 2) : (ending - 2)])
        twice_preprocessed_problem_copy = PATTERN_OF_MATH_PART.sub(
            f"math{i}", twice_preprocessed_problem_copy, 1
        )

    text_part = twice_preprocessed_problem_copy
    ## step2 수식 부분 점역하기
    translated_only_variable = ["0" + fft.variable(i) for i in only_variable_list]
    translated_math = [fft.translate_to_math_braille(i) for i in math_list]

    # step2 점역된 수식과 텍스트 부분 합치기
    PATTERN_OF_MATH_NUMBERING = re.compile("math[0-9]+?")
    PATTERN_OF_VARIABLE_NUMBERING = re.compile("variable[0-9]+?")

    for i in translated_math:
        text_part = PATTERN_OF_MATH_NUMBERING.sub(i, text_part, 1)

    for i in translated_only_variable:
        text_part = PATTERN_OF_VARIABLE_NUMBERING.sub(i, text_part, 1)

    result = text_part
    return result
