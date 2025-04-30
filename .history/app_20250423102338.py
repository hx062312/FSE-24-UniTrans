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
                jsonl_path = 'cleaned_data/deepseek/test_cases/test_cases_python.jsonl'
                
                # 读取并更新文件
                with open(jsonl_path, 'r') as f:
                    original_data = json.loads(f.readline())
                original_data['test_case'] = test_cases
                
                # 保存回文件
                with open(jsonl_path, 'w') as f:
                    json.dump(original_data, f)
                
                return jsonify({'success': True})
            
            print("开始执行步骤二：测试用例生成...")
            handle_test_case_generation(data)
            print("步骤二完成：测试用例已生成")

            jsonl_path = 'cleaned_data/deepseek/test_cases/test_cases_python.jsonl'
            with open(jsonl_path, 'r') as f:
                test_cases = json.loads(f.readline())
            
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
        "id": current_time,
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
    input_text = data.get('inputText')
    
    try:
        # 第一步：生成测试用例
        cmd1 = f"python deepseek.py --src_lang {source_lang} --obj 0 --k 5"
        result1 = subprocess.run(cmd1, shell=True, check=True, capture_output=True, text=True)
        
        # 第二步：处理测试用例
        cmd2 = f"python process_valid_inputs.py --model deepseek --src_lang {source_lang}"
        result2 = subprocess.run(cmd2, shell=True, check=True, capture_output=True, text=True)
        
        if result1.returncode == 0 and result2.returncode == 0:
            return input_text  # 返回原始输入，供下一步使用
        else:
            raise Exception("测试用例生成失败")
            
    except Exception as e:
        raise Exception(f"测试用例生成过程出错: {str(e)}")

def handle_translation_augmentation(data):
    # 翻译增强逻辑
    input_text = data.get('inputText')
    # 实现翻译增强的具体逻辑
    return "翻译增强的结果"

def handle_translation_repair(data):
    # 翻译修复逻辑
    input_text = data.get('inputText')
    # 实现翻译修复的具体逻辑
    return "翻译修复的结果"

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)