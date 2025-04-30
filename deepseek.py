# python deepseek.py --dst_lang ${dst_lang} --obj 0 --k ${test_case_num}
# python deepseek.py --src_lang python --obj 0 --k 10
# python deepseek.py --src_lang cpp --obj 0 --k 10
# python deepseek.py --src_lang java --obj 0 --k 10

# python deepseek.py --src_lang ${src_lang} --dst_lang ${dst_lang} --obj 3 --k ${sample_k} --test_case_num ${test_case_num}
# python deepseek.py --src_lang python --dst_lang cpp --obj 3 --test_case_num 10 
# python deepseek.py --src_lang cpp --dst_lang python --obj 3 --test_case_num 10 
# 因为 FileNotFoundError: [Errno 2] No such file or directory: './cleaned_data/deepseek/test_cases/test_cases_cpp.jsonl'，
# 把 144 with open(f"./cleaned_data/deepseek/test_cases/test_cases_{dst_lang}.jsonl", encoding="utf-8") as fr:
# 改成 with open(f"./cleaned_data/deepseek/test_cases/test_cases_{src_lang}.jsonl", encoding="utf-8") as fr:

import re
import os
import openai
from openai import OpenAI
from openai import APIError, RateLimitError
import json
import jsonlines
from tqdm import tqdm
from cleaned_data.templates.examples_inp import example_cpp, valid_inputs_cpp, \
    example_java, valid_inputs_java, example_python, valid_inputs_python
from cleaned_data.templates.examples_trans import \
    example_code_java, example_code_cpp, example_code_python, \
    example_test_cases_java, example_test_cases_cpp, example_test_cases_python
from cleaned_data.templates.example_refine import python_refine_example2_1, python_refine_example2_2, \
    cpp_refine_example2_1, cpp_refine_example2_2, java_refine_example2_1, java_refine_example2_2
from tenacity import (
    retry,
    retry_if_exception_type,
    wait_random_exponential,
)  # for exponential backoff
import argparse
from config import Paths, Obj, API_KEY, ensure_dir_exists


# DeepSeek API client initialization
client = OpenAI(api_key="API_Key", base_url="https://api.deepseek.com")

# 最少等待1秒，最多60秒
@retry(
    wait=wait_random_exponential(min=1, max=60),
    retry=retry_if_exception_type((RateLimitError, APIError))  # 直接使用新错误类型
)
def collect_one(prompt, api_key):
    # Set the API key for DeepSeek
    client.api_key = api_key

    # Call DeepSeek API
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=prompt,
        stream=False
    )

    # Process the response
    candidates = []
    # DeepSeek API 返回单个结果
    content = response.choices[0].message.content.strip()
    candi_lst = content.split("\n")
    candi = ""
    for snippet in candi_lst:
        if snippet.endswith("END_OF_CASE"):
            break
        else:
            candi += snippet + "\n"
    candi = candi.strip()
    if candi != "":
        candidates.append(candi)

    return candidates

def prompt_trans(src_lang, dst_lang, item):
    return {"role": "user", "content": f"Given the {src_lang} code:\n{item}\nPlease translate the above {src_lang} code to {dst_lang} code, and use END_OF_CASE to finish your answer."}

def prompt_trans_one_shot(src_lang, dst_lang, item):
    example_dst_code = eval(f"example_code_{dst_lang}")
    example_src_code = eval(f"example_code_{src_lang}")
    content = f"Given {src_lang} code:\n{example_src_code}\nTranslate given {src_lang} code to {dst_lang} code, " \
              f"and use END_OF_CASE to finish your answer.\n{example_dst_code}\nEND_OF_CASE\n"
    target = f"Given {src_lang} code:\n{item}\nTranslate given {src_lang} code to {dst_lang} code, " \
              f"and use END_OF_CASE to finish your answer.\n"
    content = content + target
    return {"role": "user", "content": content}
def prompt_trans_w_case(src_lang, dst_lang, item, test_cases, test_case_num):
    example_dst_code = eval(f"example_code_{dst_lang}")
    example_src_code = eval(f"example_code_{src_lang}")
    example_test_cases = "\n".join(eval(f"example_test_cases_{dst_lang}")[: test_case_num])

    content = f"Given {src_lang} code:\n{example_src_code}\nGiven test cases:\n{example_test_cases}\n" \
              f"Translate given {src_lang} code to {dst_lang} code, and ensure the translated {dst_lang} code can pass all given test cases." \
              f"Use END_OF_CASE to finish your answer.\n{example_dst_code}\nEND_OF_CASE\n"
    target = f"Given {src_lang} code:\n{item}\nGiven test cases:\n{test_cases}\n" \
             f"Translate given {src_lang} code to {dst_lang} code, and ensure the translated {dst_lang} code can pass all given test cases." \
             f"Use END_OF_CASE to finish your answer.\n"
    content = content + target
    # print("TRANS W CASES:", content)
    return {"role": "user", "content": content}

def prompt_case(src_lang, item):
    if src_lang == "cpp":
        return {"role": "user", "content": f"{example_cpp}\n{valid_inputs_cpp}\n{item}\nplease generate three groups of differentiated valid inputs for the above focal method of {src_lang} language, in the format of [Input_1]\n[Input_2]\n...[Input_10]. Finally, use END_OF_CASE to finish your answer."}
    elif src_lang == "java":
        return {"role": "user", "content": f"{example_java}\n{valid_inputs_java}\n{item}\nplease generate three groups of differentiated valid inputs for the above focal method of {src_lang} language, in the format of [Input_1]\n[Input_2]\n...[Input_10]. Finally, use END_OF_CASE to finish your answer."}
    elif src_lang == "python":
        return {"role": "user", "content": f"{example_python}\n{valid_inputs_python}\n{item}\nplease generate three groups of differentiated valid inputs for the above focal method of {src_lang} language, in the format of [Input_1]\n[Input_2]\n...[Input_10]. Finally, use END_OF_CASE to finish your answer."}
    else:
        assert False, "unknown lang!"

def prompt_refine(dst_lang, org_sol, feedback):
    if dst_lang == "python":
        dst_lang_comm = "#"
    elif dst_lang == "java" or dst_lang == "cpp":
        dst_lang_comm = "//"
    else:
        assert False, "unknown lang!"

    if feedback['marked_code']:
        code = feedback['marked_code'].strip()
        content = f"Given buggy {dst_lang} code:\n{code}\n" \
                  f"Given test case:\n{feedback['case']}\n" \
                  f"Error message:{feedback['err_msg']}\n" \
                  f"Fix the buggy line (marked {dst_lang_comm}<Buggy Line>) in the buggy {dst_lang} code according to the given error message. " \
                  f"Use END_OF_CASE to finish your answer:\n"
        prompt = eval(f"{dst_lang}_refine_example2_1") + "\n" + content
    else:
        code = org_sol.strip()
        content = f"Given buggy {dst_lang} code:\n{code}\n" \
                  f"Given test case:\n{feedback['case']}\n" \
                  f"Error message:{feedback['err_msg']}\n" \
                  f"Fix the buggy {dst_lang} code according to the error message. Use END_OF_CASE to finish your answer:\n"
        prompt = eval(f"{dst_lang}_refine_example2_2") + "\n\n" + content
    # print("REFINE: ", prompt)
    return {"role": "user", "content": prompt}

def deepseek(data_path, src_lang, dst_lang, obj, sample_num, api_key, out_path, test_case_num, feedback_file, org_sol_file, start):
    data = []
    sample_ids = []
    with open(data_path, encoding="utf-8") as fr:
        for line in fr.readlines():
            line = json.loads(line)
            data.append(line[src_lang])
            sample_ids.append(line['id'])

    if obj == Obj.TRANS_W_CASES:
        test_case_lst = {}
        with open(f"./cleaned_data/deepseek/test_cases/test_cases_{dst_lang}.jsonl", encoding="utf-8") as fr:
            for line in fr.readlines():
                line = json.loads(line)
                test_case_lst.update({line['id']: list(line['test_case'])[:test_case_num]})
    if obj == Obj.REFINE:
        test_case_lst = {}
        with open(f"./cleaned_data/gpt3_5/test_cases/test_cases_{dst_lang}.jsonl", encoding="utf-8") as fr:
            for line in fr.readlines():
                line = json.loads(line)
                test_case_lst.update({line['id']: list(line['test_case'])[:test_case_num]})
        feedbacks = {}
        with open(feedback_file, encoding="utf-8") as fr:
            for line in fr.readlines():
                line = json.loads(line)
                feedbacks.update({line['id']: line['feedbacks']})
        org_sols = {}
        with open(org_sol_file, encoding="utf-8") as fr:
            for line in fr.readlines():
                line = json.loads(line)
                org_sols.update({line['id']: line[dst_lang]})


    prefix = [{"role": "system", "content": "You are a professional developer proficient in java, python, and cpp.\n"}]
    count = 0
    for id, item in tqdm(zip(sample_ids, data), total=len(sample_ids)):
        count += 1
        if count < start:
            continue
        if obj == Obj.TRANS:
            target = [prompt_trans(src_lang, dst_lang, item)]
        elif obj == Obj.GEN_VAL_INP:
            target = [prompt_case(src_lang, item)]
        elif obj == Obj.TRANS_ONE_SHOT:
            target = [prompt_trans_one_shot(src_lang, dst_lang, item)]
        elif obj == Obj.TRANS_W_CASES:
            test_cases = "\n".join(test_case_lst[id])
            if test_cases.strip() == "":
                target = [prompt_trans_one_shot(src_lang, dst_lang, item)]
            else:
                target = [prompt_trans_w_case(src_lang, dst_lang, item, test_cases, test_case_num)]
        elif obj == Obj.REFINE:
            flag = True
            feedback = feedbacks[id] if id in feedbacks else []
            err_fd = []
            for i in feedback:
                if i['err_type'] != "PASS":
                    flag = False
                    err_fd.append(i)
            if flag is True:
                with jsonlines.open(out_path, "w") as fw:
                    fw.write({"id": id, dst_lang: org_sols[id]})
                continue
            else:
                feedback0 = err_fd[0]
                if feedback0['err_type'] == "REDO":
                    test_cases = "\n".join(test_case_lst[id])
                    if test_cases.strip() == "":
                        target = [prompt_trans_one_shot(src_lang, dst_lang, item)]
                        # print("REDO W/O CASE: ", target)
                    else:
                        target = [prompt_trans_w_case(src_lang, dst_lang, item, test_cases, test_case_num)]
                        # print("REDO W CASES: ", prompt)
                else:
                    target = [prompt_refine(dst_lang, org_sols[id][0].strip(), feedback0)]
        else:
            assert False, "no such objective!"
        prompt = prefix + target
        with jsonlines.open(out_path, "w") as fw:
            if obj == Obj.GEN_VAL_INP:
                fw.write({"id": id, src_lang: collect_one(prompt, api_key)})
            else:
                fw.write({"id": id, dst_lang: collect_one(prompt, api_key)})


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--apikey", type=str, help="enter your api key", default=API_KEY)
    parser.add_argument("--src_lang", type=str, help="source language", default="java")
    parser.add_argument("--dst_lang", type=str, help="target language", default="python")
    parser.add_argument("--k", type=int, help="sampling number", default=10)
    parser.add_argument("--start", type=int, help="start index", default=1)
    parser.add_argument("--shots", type=int, help="one shot or not", default=1)
    parser.add_argument("--round", type=int, help="number of round", default=2)
    parser.add_argument("--test_case_num", type=int, help="num of test cases", default=3)
    parser.add_argument("--obj", type=int, help="select an objective - 0: gen_val_inp, 2: trans, 3: trans_w_cases, 4: refine", default=0)
    args = parser.parse_args()

    api_key = args.apikey
    src_lang = args.src_lang
    dst_lang = args.dst_lang
    obj = args.obj
    sample_num = args.k
    _round = args.round
    test_case_num = args.test_case_num  # todo only be activated when obj == TRANS_W_CASES

    test_file = os.path.join(Paths.TEST_DIR, "testable_samples.jsonl")
    feedback_file = os.path.join(Paths.FEEDBACK_DIR, f"testable_{src_lang}_{dst_lang}_w_{test_case_num}cases_{_round}round.jsonl")
    org_sol_file = os.path.join(Paths.ORG_SOL_DIR, f"testable_{src_lang}_{dst_lang}_w_{test_case_num}cases_{_round}round.jsonl")
    test_cases_file = os.path.join(Paths.TEST_CASES_DIR, f"test_cases_{dst_lang}.jsonl")
    valid_inputs_file = os.path.join(Paths.VALID_INPUTS_DIR, f"valid_inputs_{src_lang}.jsonl")
    if obj == Obj.GEN_VAL_INP:
        out_path = valid_inputs_file
    elif obj == Obj.TRANS_W_CASES:
        out_path = org_sol_file
    # Ensure directories exist before writing files
    ensure_dir_exists(test_file)
    ensure_dir_exists(feedback_file)
    ensure_dir_exists(org_sol_file)
    ensure_dir_exists(out_path)
    ensure_dir_exists(test_cases_file)

    # TODO: init: start=1, restart: start=stop_count+1
    deepseek(test_file, src_lang, dst_lang, obj, sample_num, api_key, out_path, test_case_num, feedback_file, org_sol_file, start=1)


