from flask import Flask, request, jsonify, render_template
import time
import json
from datetime import datetime
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def process():
    data = request.get_json()
    step = data.get('step')
    
    try:
        if step == 'source_code_preservation':
            print("开始执行步骤一：源代码保存...")
            handle_source_code_preservation(data)
            print("步骤一完成：源代码已保存")
            result = data.get('inputText')
        elif step == 'test_case_generation':
            if request.json and 'test_cases' in request.json:
                test_cases = request.json['test_cases']
                target_lang = request.json.get('targetLang', data.get('targetLang', '')).lower()
                jsonl_path = f'cleaned_data/deepseek/test_cases/test_cases_{target_lang}.jsonl'
                
                # 读取并更新文件
                with open(jsonl_path, 'r') as f:
                    original_data = json.loads(f.readline())
                original_data['test_case'] = test_cases
                
                # 保存回文件
                with open(jsonl_path, 'w') as f:
                    json.dump(original_data, f)
                
                return jsonify({'success': True})
            
            print("开始执行步骤二：测试用例生成...")
            test_cases = handle_test_case_generation(data)  # 获取返回的测试用例数据
            print("步骤二完成：测试用例已生成")
        
            return jsonify({
                'success': True,
                'id': test_cases['id'],
                'test_cases': test_cases['test_case']
            })

        elif step == 'translation_augmentation':
            print("开始执行步骤三：翻译增强...")
            handle_translation_augmentation(data)
            print("步骤三完成：翻译增强已完成")
        elif step == 'translation_repair':
            print("开始执行步骤四：翻译修复...")
            handle_translation_repair(data)
            print("步骤四完成：翻译修复已完成")
        else:
            return jsonify({'success': False, 'error': '未知的处理步骤'})
        
        return jsonify({'success': True, 'output': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def handle_source_code_preservation(data):
    # 源代码保存逻辑
    source_lang = data.get('sourceLang')
    input_text = data.get('inputText')
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_data = {
        "id": 0,
        source_lang: input_text
    }
    data_path = 'cleaned_data/testable_samples.jsonl'
    try:
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f)
            f.write('\n')
    except Exception as e:
        print(f"Error saving data: {e}")

def handle_test_case_generation(data):
    
    source_lang = data.get('sourceLang').lower()
    target_lang = data.get('targetLang').lower()
    
    try:
        # 第一步：生成测试用例
        cmd1 = f"python deepseek.py --src_lang {source_lang} --obj 0 --k 10"
        result1 = subprocess.run(cmd1, shell=True, check=True, capture_output=True, text=True)
        
        # 第二步：处理测试用例
        cmd2 = f"python process_valid_inputs.py --model deepseek --src_lang {source_lang} --dst_lang {target_lang}"
        result2 = subprocess.run(cmd2, shell=True, check=True, capture_output=True, text=True)
        
        if result1.returncode == 0 and result2.returncode == 0:
            # 读取生成的测试用例
            jsonl_path = f'cleaned_data/deepseek/test_cases/test_cases_{target_lang}.jsonl'
            with open(jsonl_path, 'r') as f:
                test_cases = json.loads(f.readline())
            return test_cases  # 返回测试用例数据
        else:
            raise Exception("测试用例生成失败")
            
    except Exception as e:
        raise Exception(f"测试用例生成过程出错: {str(e)}")

def handle_translation_augmentation(data):
    # 翻译增强逻辑
    source_lang = data.get('sourceLang').lower()
    target_lang = data.get('targetLang').lower()
    sample_k = data.get('sampleK', 5)  # 默认值为5
    test_case_num = data.get('testCaseNum', 10)  # 默认值为10
    model_name = data.get('model', 'deepseek')  # 默认使用gpt3_5模型
    round = data.get('round', 2)  # 默认轮次为1
    
    try:
        # 1. 执行翻译增强
        print(f"执行翻译增强: {source_lang} -> {target_lang}...")
        cmd1 = f"python deepseek.py --src_lang {source_lang} --dst_lang {target_lang} --obj 3 --k {sample_k} --test_case_num {test_case_num}"
        result1 = subprocess.run(cmd1, shell=True, check=True, capture_output=True, text=True)
        
        # 2. 处理翻译后的程序
        print("处理翻译后的程序...")
        cmd2 = f"python process_translation.py --src_lang {source_lang} --dst_lang {target_lang} --suffix _w_10cases_2round"
        result2 = subprocess.run(cmd2, shell=True, check=True, capture_output=True, text=True)
        
        # 3. 翻译评估
        print("执行翻译评估...")
        cmd3 = f"python fetch_feedbacks.py --model {model_name} --src_lang {source_lang} --dst_lang {target_lang} --test_case_num {test_case_num} --round {round}"
        result3 = subprocess.run(cmd3, shell=True, check=True, capture_output=True, text=True)
        
        if result1.returncode == 0 and result2.returncode == 0 and result3.returncode == 0:
            print("翻译增强完成")
        else:
            print("翻译增强过程出错")
            
    except Exception as e:
        print(f"翻译增强过程出错: {str(e)}")
        raise Exception(f"翻译增强过程出错: {str(e)}")

def handle_translation_repair(data):
    # 翻译修复逻辑
    input_text = data.get('inputText')
    # 实现翻译修复的具体逻辑
    return "翻译修复的结果"

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)