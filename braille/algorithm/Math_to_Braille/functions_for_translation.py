import re

from . import brf_code
from . import brf_to_indeterminate_letter as bil


# 수식 점역 함수
def translate_to_math_braille(latex_match):
    # Basic Translation
    # 한 글자씩 변환 후에 latex코드 상으로 공백을 뜻하는 '\ '를 삭제한다
    output_of_translate_one_to_one = translate_one_to_one(latex_match).replace(
        r"\ ", ""
    )
    # 벡슬래시와 함께 쓰이는 latex를 변환 후에 공백을 삭제한다
    output_of_translate_latex_with_backslash = translate_latex_with_backslash(
        output_of_translate_one_to_one
    ).replace(" ", "")

    # Translation Function for Specific Latex Symbols
    output_of_fraction = fraction(output_of_translate_latex_with_backslash)
    output_of_power = power(output_of_fraction)
    output_of_root = root(output_of_power)
    output_of_subscript = subscript(output_of_root)
    output_of_trigonometric_function = trigonometric_function(output_of_subscript)
    output_of_log = log(output_of_trigonometric_function)
    restore_whitespace = output_of_log.replace("WSP", " ")

    # Sophisticated Process
    output_of_add_dot_between_number_and_alphabet = add_dot_between_number_and_alphabet(
        restore_whitespace
    )
    output_of_capital_sign = capital_sign(output_of_add_dot_between_number_and_alphabet)
    output_of_delete_number_sign_between_numbers = delete_number_sign_between_numbers(
        output_of_capital_sign
    )
    output_of_delete_number_sign_after_dot = delete_number_sign_after_dot(
        output_of_delete_number_sign_between_numbers
    )
    result_brf = restore_brf_parentheses(
        brf_parentheses(output_of_delete_number_sign_after_dot)
    )
    # brf로 된 결과를 미정의 문자로 변환
    result_il = bil.translate_brf_to_il(result_brf)
    return result_il


# Basic Translation
# brf_code.code를 참조해서 latex를 brf로 변환하는 함수
def translate_latex_to_brf(latex):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    #   그리고 brf_code.code 와 제대로 대응되기 위해서 latex 안에 있는 공백을 제거한다
    if isinstance(latex, re.Match):
        latex_str = latex.group().replace(" ", "")
    else:
        latex_str = latex.replace(" ", "")

    #   brf_code.code 에는 대문자 알파벳에 해당하는 brf가 따로 없으므로 대문자는 별도로 brf로 점역한다.
    if len(latex_str) == 1 and latex_str.isupper():
        return "," + latex_str.lower()

    #   brf_code.code 를 참조해서 latex를 brf로 점역한다.
    if latex_str in brf_code.code:
        result_brf = brf_code.code[latex_str][1]
    else:
        result_brf = latex_str
    return result_brf


# 한 글자씩 순차적으로 점역하는 함수
def translate_one_to_one(latex):
    brf_result = ""  # 추후에 점역된 결과로 채워질 것이다.

    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(latex, re.Match):
        latex_str = latex.group()
    else:
        latex_str = latex

    #   brf_code.code 를 참조해서 한 글자씩 순차적으로 brf로 점역한다.
    for i in latex_str:
        if i in brf_code.code:
            brf_result += translate_latex_to_brf(i)
        #       대문자 알파벳이 brf_code.code에 존재하지 않아서 따로 구별해야 한다.
        elif i.isupper():
            brf_result += translate_latex_to_brf(i)
        #       brf_code.code에 존재하지 않는 latex이면 그대로 반환한다.
        else:
            brf_result += i

    return brf_result


# 벡슬래시가 앞에 붙는 latex 기호를 점역하는 함수
def translate_latex_with_backslash(mixed_latex_brf):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    BACKSLASH_ALPHABETS = r" ?\\[a-zA-Z]+ ?"
    BACKSLASH_LEFT_OR_RIGHT_PUCTUATION = r"\\left.|\\right."
    BACKSLASH_SINGLE_LETTER = r" ?\\. ?"
    PATTERN_OF_ALPHABETS = re.compile(BACKSLASH_ALPHABETS)
    PATTERN_OF_LEFT_OR_RIGHT_PUCTUATION = re.compile(BACKSLASH_LEFT_OR_RIGHT_PUCTUATION)
    PATTERN_OF_SINGLE_LETTER = re.compile(BACKSLASH_SINGLE_LETTER)
    PATTERNS = [
        PATTERN_OF_ALPHABETS,
        PATTERN_OF_LEFT_OR_RIGHT_PUCTUATION,
        PATTERN_OF_SINGLE_LETTER,
    ]

    brf_result = latex_str
    for i in enumerate(PATTERNS):
        brf_result = i[1].sub(translate_latex_to_brf, brf_result)

    return brf_result


# Translation Function for Specific Latex Symbols
# 분수를 점역하는 함수
def fraction(
    mixed_latex_brf, add_numerator_parentheses=0, add_denominator_parentheses=0
):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 fraction의 형태를 정규표현식으로 나타낸 것이다. 기본 형태는 r"\\frac{.*?}{.*?}" 이다.
    pattern_of_fraction = re.compile(
        r"\\frac{("
        + ".*?}" * add_numerator_parentheses
        + ".*?)}{("
        + ".*?}" * add_denominator_parentheses
        + ".*?)}"
    )
    PATTERN_OF_BASIC_FORM = re.compile(r"\\frac{.*?}{.*?}")

    #   fraction이 문자열에 있는지 확인한다.
    has_fraction = list(pattern_of_fraction.finditer(latex_str))
    if has_fraction:
        numerator, denominator = has_fraction[0].group(1), has_fraction[0].group(2)
        #       아래의 변수는 분자와 분모 안에 '{', '}' 기호의 개수가 같은지 판별하기 위한 변수이다.
        (
            numerator_difference_of_left_and_right,
            denominator_difference_of_left_and_right,
        ) = (
            numerator.count("{") - numerator.count("}"),
            denominator.count("{") - denominator.count("}"),
        )
    else:
        return latex_str

    # 분자와 분모 안에 '{', '}'의 개수가 일치하는지 판별해서 점역을 할지 결정한다.
    if (
        numerator_difference_of_left_and_right,
        denominator_difference_of_left_and_right,
    ) == (0, 0):
        brf_result = pattern_of_fraction.sub("(\g<2>)/(\g<1>)", latex_str, 1)
        # 한 번 점역된 결과값에fraction이 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return fraction(brf_result)
        else:
            return brf_result

    else:
        if numerator_difference_of_left_and_right:
            add_numerator_parentheses += 1
        elif denominator_difference_of_left_and_right:
            add_denominator_parentheses += 1
        return fraction(
            latex_str, add_numerator_parentheses, add_denominator_parentheses
        )


# 지수를 점역하는 함수
def power(mixed_latex_brf, add_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 지수(윗첨자)의 형태를 정규표현식으로 나타낸 것이다. 기본 형태는 "\^{.*?}" 이다.
    pattern_of_power = re.compile("\^{(" + ".*?}" * add_parentheses + ".*?)}")
    PATTERN_OF_BASIC_FORM = re.compile("\^{.*?}")

    #   power가 문자열에 있는지 확인한다.
    has_power = list(pattern_of_power.finditer(latex_str))
    if has_power:
        content_of_power = has_power[0].group(1)
    else:
        return latex_str

    # power 안의 '{', '}' 의 개수가 일치하는지 판별해서 점역을 할지 결정한다.
    if content_of_power.count("{") - content_of_power.count("}") == 0:
        brf_result = pattern_of_power.sub("^(\g<1>)", latex_str, 1)
        # 한 번 점역된 결과값에 power가 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return power(brf_result)
        else:
            return brf_result
    else:
        add_parentheses += 1
        return power(latex_str, add_parentheses)


# 루트를 점역하는 함수
def root(mixed_latex_brf, add_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 root의 형태를 정규표현식으로 작성한 것이다. root의 기본 형태는
    pattern_of_root = re.compile(r"\\sqrt{(" + ".*?}" * add_parentheses + ".*?)}")
    PATTERN_OF_BASIC_FORM = re.compile(r"\\sqrt{.*?}")

    #   root가 문자열에 있는지 확인한다.
    has_root = list(pattern_of_root.finditer(latex_str))
    if has_root:
        content_of_root = has_root[0].group(1)
    else:
        return latex_str

    #   root 안의 '{', '}' 개수가 일치하는지 판별해서 점을 할지 결정한다.
    if content_of_root.count("{") - content_of_root.count("}") == 0:
        brf_result = pattern_of_root.sub(">(\g<1>)", latex_str, 1)
        #   한번 점역된 결과물에 root가 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return root(brf_result)
        else:
            return brf_result
    else:
        add_parentheses += 1
        return root(latex_str, add_parentheses)


# 아랫첨자(수열)를 점역하는 함수
def subscript(mixed_latex_brf, add_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 아랫첨자(수열)의 형태를 정규표현식으로 나타낸 것이다. 기본 형태는 "_{.*?}" 이다.
    pattern_of_subscript = re.compile("_{(" + ".*?}" * add_parentheses + ".*?)}")
    PATTERN_OF_BASIC_FORM = re.compile("_{.*?}")

    #   subscript 가 문자열에 있는지 확인한다.
    has_subscript = list(pattern_of_subscript.finditer(latex_str))
    if has_subscript:
        content_of_subscript = has_subscript[0].group(1)
    else:
        return latex_str

    # subscript 안의 '{', '}' 의 개수가 일치하는지 판별해서 점역을 할지 결정한다.
    if content_of_subscript.count("{") - content_of_subscript.count("}") == 0:
        brf_result = pattern_of_subscript.sub(";(\g<1>)", latex_str, 1)
        # 한 번 점역된 결과값에 subscript 가 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return subscript(brf_result)
        else:
            return brf_result
    else:
        add_parentheses += 1
        return subscript(latex_str, add_parentheses)


# 삼각함수를 점역하는 함수
def trigonometric_function(mixed_latex_brf, add_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 삼각함수의 형태를 정규표현식으로 나타낸 것이다. 기본 형태는 PATTERN_OF_BASIC_FORM 이다.
    pattern_of_trigonometric_function = re.compile(
        r"\\(?P<kind>sin|cos|tan|csc|sec|cot){(?P<content>"
        + ".*?}" * add_parentheses
        + ".*?)}"
    )
    PATTERN_OF_BASIC_FORM = re.compile("(sin|cos|tan|csc|sec|cot){.*?}")
    #   Key is latex, Value is brf.
    KIND_OF_TRIGONOMETRIC = {
        "sin": "6s",
        "cos": "6c",
        "tan": "6t",
        "csc": "6<",
        "sec": "6-",
        "cot": "6|",
    }

    #   trigonometric_function 가 문자열에 있는지 확인한다.
    has_trigonometric_function = list(
        pattern_of_trigonometric_function.finditer(latex_str)
    )
    if has_trigonometric_function:
        content_of_trigonometric_function = has_trigonometric_function[0].group(
            "content"
        )
        kind = has_trigonometric_function[0].group("kind")
    else:
        return latex_str

    # trigonometric_function안의 '{', '}' 의 개수가 일치하는지 판별해서 점역을 할지 결정한다.
    if (
        content_of_trigonometric_function.count("{")
        - content_of_trigonometric_function.count("}")
        == 0
    ):
        brf_result = pattern_of_trigonometric_function.sub(
            KIND_OF_TRIGONOMETRIC[kind] + "(\g<content>)", latex_str, 1
        )
        # 한 번 점역된 결과값에         trigonometric_function 가 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return trigonometric_function(brf_result)
        else:
            return brf_result
    else:
        add_parentheses += 1
        return trigonometric_function(latex_str, add_parentheses)


# 로그를 점역하는 함수
def log(mixed_latex_brf, add_base_parentheses=0, add_antilogarithm_parentheses=0):
    #   sub 메서드의 첫 번째 인수로 사용될 경우를 대비해서 Match를 문자열로 바꾼다.
    if isinstance(mixed_latex_brf, re.Match):
        latex_str = mixed_latex_brf.group()
    else:
        latex_str = mixed_latex_brf

    #   아래는 log의 형태를 정규표현식으로 나타낸 것이다. 기본 형태는 PATTERN_OF_BASIC_FORM 이다.
    pattern_of_log = re.compile(
        r"\\log_{("
        + ".*?}" * add_base_parentheses
        + ".*?)}{("
        + ".*?}" * add_antilogarithm_parentheses
        + ".*?)}"
    )
    PATTERN_OF_BASIC_FORM = re.compile(r"\\log_{.*?}{.*?}")

    #   log 가 문자열에 있는지 확인한다.
    has_log = list(pattern_of_log.finditer(latex_str))
    if has_log:
        base, antilogarithm = has_log[0].group(1), has_log[0].group(2)
        #       아래의 변수는 밑과 분모 안에 '{', '}' 기호의 개수가 같은지 판별하기 위한 변수이다.
        (
            base_difference_of_left_and_right,
            antilogarithm_difference_of_left_and_right,
        ) = (
            base.count("{") - base.count("}"),
            antilogarithm.count("{") - antilogarithm.count("}"),
        )
    else:
        return latex_str

    # 밑과 진수 안에 '{', '}'의 개수가 일치하는지 판별해서 점역을 할지 결정한다.
    if (
        base_difference_of_left_and_right,
        antilogarithm_difference_of_left_and_right,
    ) == (0, 0):
        brf_result = pattern_of_log.sub("_;(\g<1>)(\g<2>)", latex_str, 1)
        # 한 번 점역된 결과값에log이 또 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(brf_result):
            return log(brf_result)
        else:
            return brf_result
    else:
        if base_difference_of_left_and_right:
            add_base_parentheses += 1
        elif antilogarithm_difference_of_left_and_right:
            add_antilogarithm_parentheses += 1
        return log(latex_str, add_base_parentheses, add_antilogarithm_parentheses)


# Sophisticated Process
# 알파벳 a-j 앞에 숫자가 있으면 5점(")를 붙인다.
def add_dot_between_number_and_alphabet(brf):
    PATTERN_OF_NUMBER_ALPHABET = re.compile("#[a-j][a-j]")
    brf_result = PATTERN_OF_NUMBER_ALPHABET.sub(
        lambda x: x.group()[0:2] + '"' + x.group()[2], brf
    )
    return brf_result


# 대문자가 연속해서 나오면 첫 글자에 6점 두 개를 붙인다
def capital_sign(brf):
    PATTERN_OF_CAPITAL_ALPHABETS = re.compile(",[a-z](,[a-z])+")
    brf_result = PATTERN_OF_CAPITAL_ALPHABETS.sub(
        lambda x: ",," + x.group().replace(",", ""), brf
    )
    return brf_result


# 숫자가 연속해서 나올 때 처음에만 수표를 붙인다
def delete_number_sign_between_numbers(brf):
    PATTERN_OF_NUMBER_SIGN_BETWEEN_NUMBERS = re.compile("#[a-j](#[a-j])+")
    brf_result = PATTERN_OF_NUMBER_SIGN_BETWEEN_NUMBERS.sub(
        lambda x: "#" + x.group().replace("#", ""), brf
    )
    return brf_result


# 소수점 뒤에 수표를 붙이지 않는다
def delete_number_sign_after_dot(brf):
    PATTERN_OF_NUMBER_SIGN_AFTER_DOT = re.compile("#[a-j]+?4#[a-j]")
    brf_result = PATTERN_OF_NUMBER_SIGN_AFTER_DOT.sub(
        lambda x: x.group().replace("4#", "4"), brf
    )
    return brf_result


# 묶음괄호를 처리하는 함수
#  brf_parentheses 함수는 묶음괄호를 사용하는 경우 '(', ')' 기호를 '"LEFT, "RIGHT"로 바꾸고, 묶음괄호를 사용하지 않는 경우 '(', ')' 기호를 삭제하는 함수이다.
def brf_parentheses(brf, move_in=0):
    #   grouping 는 가장 바깥쪽의 '(' (여는 묶음괄호)와 가장 안쪽의 '(' 사이의 수식들을 그룹핑해서 보호하는 역할을 한다.
    if move_in == 0:
        grouping = 0
    else:
        grouping = 1
    #   pattern_of_brf_parentheses 은 묶음괄호가 사용된 부분을 정규표현식으로 나타낸 것이다.
    #   "(?!')", "(?!,)"는 대괄호("('", ",)")와 겹치지 않고 묶음괄호만을 탐색할 수 있도록 하는 역할이다.
    pattern_of_brf_parentheses = re.compile(
        "(" * grouping
        + "[(](?!').*?" * move_in
        + ")" * grouping
        + "[(](?!')(?P<content>.*?)(?!,)[)]"
    )
    PATTERN_OF_BASIC_FORM = re.compile("[(](?!').*?(?!,)[)]")
    #   아래는 묶음괄호가 사용되지 않는 경우들이다.
    CASE_OF_NOT_USING = re.compile(
        """^(
    [59]?>?,?[a-z]  # '부호' + '루트' + '대문자여부' + '알파벳'
   |[59]?>?[#][a-j]+  # '부호' + '루트' + '숫자'
)$""",
        re.VERBOSE,
    )

    #   묶음괄호가 문자열에 있는지 확인한다.
    has_brf_parentheses = list(pattern_of_brf_parentheses.finditer(brf))
    if has_brf_parentheses:
        content_between_brf_parentheses = has_brf_parentheses[0].group("content")
    else:
        return brf

    #   가장 안쪽의 묶음괄호까지 이동했는지 판별한다.
    if (
        content_between_brf_parentheses.count("(")
        - content_between_brf_parentheses.count(")")
        == 0
    ):
        #       묶음괄호를 사용하지 않는 겨우인지 사용하는 경우인지를 판별해서 묶음괄호를 제거하거나 "LEFT"/"RIGHT"으로 대체한다.
        if CASE_OF_NOT_USING.match(content_between_brf_parentheses):
            result_brf = pattern_of_brf_parentheses.sub(
                "\g<1>" * grouping + "\g<content>", brf, 1
            )
        else:
            result_brf = pattern_of_brf_parentheses.sub(
                "\g<1>" * grouping + "LEFT\g<content>RIGHT", brf, 1
            )

        #       한 번 점역된 결과값에 묶음괄호가 사용된 부분이 있는지 확인한다.
        if PATTERN_OF_BASIC_FORM.search(result_brf):
            return brf_parentheses(result_brf)
        else:
            return result_brf
    else:
        move_in += 1
        return brf_parentheses(brf, move_in)


# restore_brf_parentheses 함수는 "LEFT", "RIGHT" 을 묶음괄호 '(', ')'로 복원한다.
def restore_brf_parentheses(output_of_brf_parentheses, n=0):
    result_brf = output_of_brf_parentheses.replace("LEFT", "(").replace("RIGHT", ")")
    return result_brf


#  기타 함수


# 미지수로 된 단항식만을 별도로 점역하기 위한 함수
def variable(only_variable):
    empty_str = ""
    for i in only_variable:
        empty_str += translate_latex_to_brf(i)
    result = capital_sign(empty_str)
    return result


# 콤마로 나열된 단항식을 낱개별로 쪼개서 구분하는 함수
### 콤마 처리
def comma(str):
    if isinstance(str, re.Match):
        v = str.group()
    else:
        v = str

    result = ""
    p1 = re.compile(".+?,")
    p2 = re.compile(".+?, ")

    ## 콤마가 없으면 통과
    if not "," in v:
        return v

    ###  type2 띄어쓰기 없는 콤마
    elif not ", " in v and "," in v:
        v = v[2:-2] + ","
        l = p1.findall(v)
        for i in l:
            result += f"\\({i}\\) "
        return result[:-4] + r"\)"

    ## type2 콤마 + 공백
    elif ", " in v:
        v = v[2:-2] + ", "
        l = p2.findall(v)
        for i in l:
            result += f"\\({i[:-2]}\\), "
        return result[:-2]
