import os
from enum import IntEnum

# 基础路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(
    BASE_DIR, "cleaned_data", "deepseek"
)  # 修改输出目录为 deepseek

# API配置
API_KEY = "sk-8fa78eec289b4a9d92a3aed3ee315536"

# 语言配置
SUPPORTED_LANGUAGES = ["python", "java", "cpp"]

# 翻译配置
MAX_TEST_CASES = 3
TRANSLATION_ROUNDS = 2
SAMPLE_NUM = 10


def ensure_dir_exists(file_path):
    """Ensure the directory for the given file path exists."""
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


# 路径配置
class Paths:
    # 输出目录
    TEST_DIR = os.path.join(BASE_DIR, "cleaned_data")
    TEST_CASES_DIR = os.path.join(OUTPUT_DIR, "test_cases")
    ORG_SOL_DIR = os.path.join(OUTPUT_DIR, "org_sol")
    VALID_INPUTS_DIR = os.path.join(OUTPUT_DIR, "valid_inputs")
    FEEDBACK_DIR = os.path.join(OUTPUT_DIR, "feedbacks")
    REPAIR_DIR = os.path.join(OUTPUT_DIR, "repair")


# Obj 类定义
class Obj(IntEnum):
    GEN_VAL_INP = 0
    TRANS = 1
    TRANS_ONE_SHOT = 2
    TRANS_W_CASES = 3
    REFINE = 4
