from flask import Flask, request, jsonify, render_template
import json
from datetime import datetime
import subprocess

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def process():
    data = request.get_json()
    step = data.get("step")
    try:
        if step == "source_code_preservation":
            print("step1: source_code_preservation")
            result = handle_source_code_preservation(data)
            return jsonify({"success": True, "output": result})
        elif step == "test_case_generation":
            print("step2: test_case_generation")
            if data.get("test_cases"):
                return jsonify({"success": update_test_cases(data)})
            result = handle_test_case_generation(data)
            return jsonify(
                {"success": True, "id": result["id"], "test_cases": result["test_case"]}
            )
        elif step == "translation_augmentation":
            print("step3: translation_augmentation")
            result = handle_translation_augmentation(data)
            return jsonify(result)
        elif step == "translation_repair":
            print("step4: translation_repair")
            result = handle_translation_repair(data)
            return jsonify(
                {
                    "success": True,
                    "translated_code": result["translated_code"],
                    "test_results": result["test_results"],
                    "fetch_feedbacks_results": result["fetch_feedbacks_results"],
                }
            )
        else:
            return jsonify({"success": False, "error": "未知的处理步骤"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


def handle_source_code_preservation(data):
    source_lang = data.get("sourceLang")
    input_text = data.get("inputText")
    save_data = {"id": 0, source_lang: input_text}
    data_path = "cleaned_data/testable_samples.jsonl"
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f)
        f.write("\n")
    return input_text


def update_test_cases(data):
    test_cases = data["test_cases"]
    target_lang = data.get("targetLang", "").lower()
    jsonl_path = f"cleaned_data/deepseek/test_cases/test_cases_{target_lang}.jsonl"
    with open(jsonl_path, "r") as f:
        original_data = json.loads(f.readline())
    original_data["test_case"] = test_cases
    with open(jsonl_path, "w") as f:
        json.dump(original_data, f)
    return True


def handle_test_case_generation(data):
    source_lang = data.get("sourceLang").lower()
    target_lang = data.get("targetLang").lower()
    cmd1 = f"python deepseek.py --src_lang {source_lang} --obj 0 --k 10"
    cmd2 = f"python process_valid_inputs.py --model deepseek --src_lang {source_lang} --dst_lang {target_lang}"
    subprocess.run(cmd1, shell=True, check=True, capture_output=True, text=True)
    subprocess.run(cmd2, shell=True, check=True, capture_output=True, text=True)
    jsonl_path = f"cleaned_data/deepseek/test_cases/test_cases_{target_lang}.jsonl"
    with open(jsonl_path, "r") as f:
        test_cases = json.loads(f.readline())
    return test_cases


def handle_translation_augmentation(data):
    source_lang = data.get("sourceLang").lower()
    target_lang = data.get("targetLang").lower()
    model_name = data.get("model", "deepseek")

    cmd1 = (
        f"python deepseek.py --src_lang {source_lang} --dst_lang {target_lang} --obj 3"
    )
    cmd2 = f"python process_translation.py --src_lang {source_lang} --dst_lang {target_lang} --suffix _w_10cases_2round"
    cmd3 = f"python fetch_feedbacks.py --model {model_name} --src_lang {source_lang} --dst_lang {target_lang}"
    subprocess.run(cmd1, shell=True, check=True, capture_output=True, text=True)
    subprocess.run(cmd2, shell=True, check=True, capture_output=True, text=True)
    subprocess.run(cmd3, shell=True, check=True, capture_output=True, text=True)
    with open(
        f"cleaned_data/{model_name}/post_processed/testable_{source_lang}_{target_lang}_w_10cases_2round.jsonl",
        "r",
    ) as f:
        data = json.loads(f.readline())
        translated_code = (
            data[target_lang][0] if len(data[target_lang]) > 0 else "翻译失败"
        )
    with open(
        f"cleaned_data/{model_name}/feedbacks/raw/testable_{source_lang}_{target_lang}_w_10cases_2round_raw.jsonl",
        "r",
    ) as f:
        data = json.loads(f.readline())
        test_results = data["feedbacks"]
    return {
        "success": True,
        "translated_code": translated_code,
        "test_results": test_results,
    }


def handle_translation_repair(data):
    source_lang = data.get("sourceLang").lower()
    target_lang = data.get("targetLang").lower()
    sample_k = data.get("sampleK", 5)
    test_case_num = data.get("testCaseNum", 10)
    model_name = data.get("model", "deepseek")
    round_num = data.get("round", 2)
    cmd1 = f"python process_feedbacks.py --src_lang {source_lang} --dst_lang {target_lang} --round {round_num} --test_case_num {test_case_num}"
    cmd2 = f"python deepseek.py --src_lang {source_lang} --dst_lang {target_lang} --obj 4 --k {sample_k} --test_case_num {test_case_num}"
    cmd3 = f"python process_translation.py --src_lang {source_lang} --dst_lang {target_lang} --suffix _w_10cases_2round"
    cmd4 = f"python fetch_feedbacks.py --model {model_name} --src_lang {source_lang} --dst_lang {target_lang} --test_case_num {test_case_num} --round {round_num}"
    print("running cmd1")
    subprocess.run(cmd1, shell=True, check=True, capture_output=True, text=True)
    print("running cmd2")
    subprocess.run(cmd2, shell=True, check=True, capture_output=True, text=True)
    print("running cmd3")
    subprocess.run(cmd3, shell=True, check=True, capture_output=True, text=True)
    print("running cmd4")
    subprocess.run(cmd4, shell=True, check=True, capture_output=True, text=True)
    post_processed_path = f"cleaned_data/{model_name}/post_processed/testable_{source_lang}_{target_lang}_w_10cases_2round.jsonl"
    fetch_feedbacks_path = f"cleaned_data/{model_name}/feedbacks/raw/testable_{source_lang}_{target_lang}_w_10cases_2round_raw.jsonl"
    feedbacks_path = f"cleaned_data/{model_name}/feedbacks/testable_{source_lang}_{target_lang}_w_{test_case_num}cases_{round_num}round.jsonl"
    with open(post_processed_path, "r") as f:
        data_post = json.loads(f.readline())
        translated_code = (
            data_post[target_lang][0]
            if len(data_post[target_lang]) > 0
            else "翻译修复失败"
        )
    with open(fetch_feedbacks_path, "r") as f:
        data_feedbacks = json.loads(f.readline())
        fetch_feedbacks_results = data_feedbacks["feedbacks"]
    with open(feedbacks_path, "r") as f:
        data_feedbacks = json.loads(f.readline())
        test_results = data_feedbacks["feedbacks"]
    return {
        "success": True,
        "translated_code": translated_code,
        "fetch_feedbacks_results": fetch_feedbacks_results,
        "test_results": test_results,
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    # app.run(debug=True, use_reloader=False)
