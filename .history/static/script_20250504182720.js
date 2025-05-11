document.addEventListener('DOMContentLoaded', function() {
    // 获取所有需要的元素
    const sourceLang = document.getElementById('source-lang');
    const targetLang = document.getElementById('target-lang');
    const llmModel = document.getElementById('llm-model');
    const inputText = document.querySelector('.input-section textarea');
    const outputText = document.querySelector('.results-section textarea');
    const translateBtn = document.querySelector('.translate-btn');
    const copyBtn = document.querySelector('.copy-btn');
    const swapIcon = document.querySelector('.swap-icon');

    // 弹窗功能
    const modal = document.getElementById('modal');
    const modalMessage = document.getElementById('modal-message');
    const modalCloseBtn = modal.querySelector('.close');
    const modalNextStepBtn = modal.querySelector('.next-step');
    const modalReloadBtn = modal.querySelector('.reload');
    const translationModal = document.getElementById('translationModal');
    const closeBtn = translationModal.querySelector('.close');
    const reloadBtn = translationModal.querySelector('.reload');
    const nextStepBtn = translationModal.querySelector('.next-step');
    const modalContent = document.querySelector('.modal-content');

    const repairModal = document.getElementById('repairModal');
    const repairModalContent = repairModal.querySelector('.modal-content');
    const repairCloseBtn = repairModal.querySelector('.close');
    const repairReloadBtn = repairModal.querySelector('.reload');
    const repairNextStepBtn = repairModal.querySelector('.next-step');
    const repairProgramCode = document.getElementById('repairProgramCode');
    const repairTestCases = document.getElementById('repairTestCases');
    
    // 加载动画元素
    const loadingContainer = document.querySelector('.loading-container');
    const loadingText = document.querySelector('.loading-text');
    const loadingComplete = document.querySelector('.loading-complete');
    
    // 显示加载动画
    function showLoading(message) {
        loadingText.textContent = message;
        loadingComplete.style.display = 'none';
        loadingContainer.style.display = 'flex';
    }
    
    // 隐藏加载动画
    function hideLoading() {
        loadingContainer.style.display = 'none';
    }
    
    // 显示完成标记
    function showComplete() {
        loadingComplete.style.display = 'block';
        setTimeout(() => {
            hideLoading();
        }, 1500); // 1.5秒后隐藏加载动画
    }
    // 工具函数：统一 fetch 请求
    async function postData(url = '/', data = {}) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('请求出错:', error);
            throw error;
        }
    }

    // 关闭按钮事件
    modalCloseBtn.onclick = () => modal.style.display = "none";
    closeBtn.onclick = () => translationModal.style.display = "none";
    repairCloseBtn.onclick = () => repairModal.style.display = "none";
    window.onclick = function(event) {
        if (event.target === modal) modal.style.display = "none";
        if (event.target === translationModal) translationModal.style.display = "none";
        if (event.target === repairModal) repairModal.style.display = "none";
    };

    // 拖动弹窗
    let isDragging = false, currentX, currentY, initialX, initialY, xOffset = 0, yOffset = 0;
    const testModalContent = modal.querySelector('.modal-content');
    testModalContent.addEventListener('mousedown', dragStart);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', dragEnd);

    function dragStart(e) {
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
        if (e.target === testModalContent) isDragging = true;
    }
    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            xOffset = currentX;
            yOffset = currentY;
            testModalContent.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
        }
    }
    function dragEnd() { isDragging = false; }

    // 语言交换
    swapIcon.onclick = () => {
        [sourceLang.value, targetLang.value] = [targetLang.value, sourceLang.value];
    };

    // 翻译按钮点击事件
    translateBtn.onclick = async function() {
        try {
            // 显示加载动画 - 正在生成测试用例
            showLoading("正在生成测试用例");
            
            // 保存源代码
            const sourceData = {
                sourceLang: sourceLang.value,
                targetLang: targetLang.value,
                llmModel: llmModel.value,
                inputText: inputText.value,
                step: 'source_code_preservation'
            };
            const result = await postData('/', sourceData);
            if (!result.success) {
                hideLoading();
                return console.error('源代码保存失败:', result.error);
            }

            // 生成测试用例
            const testCaseData = { ...sourceData, step: 'test_case_generation' };
            const testCaseResult = await postData('/', testCaseData);
            if (testCaseResult.success && testCaseResult.test_cases) {
                let content = `<div class="modal-header">测试用例</div><div class="test-cases">`;
                testCaseResult.test_cases.forEach((testCase, idx) => {
                    content += `<div class="test-case"><strong>用例 ${idx + 1}:</strong><textarea id="testCase${idx}">${testCase}</textarea></div>`;
                });
                content += '</div>';
                modalMessage.innerHTML = content;
                
                // 隐藏加载动画并显示完成标记
                showComplete();
                
                // 显示测试用例弹窗
                modal.style.display = "block";
            } else {
                hideLoading();
                console.error('测试用例生成失败:', testCaseResult.error);
            }
        } catch (error) {
            hideLoading();
            console.error('处理过程出错:', error);
        }
    };

    // 测试用例弹窗的下一步按钮点击事件
    modalNextStepBtn.onclick = async function() {
        try {
            const testCases = Array.from(document.querySelectorAll('.test-case textarea')).map(t => t.value);
            const saveResult = await postData('/', {
                step: 'test_case_generation',
                test_cases: testCases,
                targetLang: targetLang.value,
                isEditButton: true
            });
            if (!saveResult.success) return alert('保存失败: ' + saveResult.error);

            modal.style.display = "none";
            // 执行翻译增强
            const translationData = {
                sourceLang: sourceLang.value,
                targetLang: targetLang.value,
                llmModel: llmModel.value,
                inputText: inputText.value,
                step: 'translation_augmentation'
            };
            const translationResult = await postData('/', translationData);
            if (translationResult.success) {
                document.getElementById('programCode').textContent = translationResult.translated_code;
                const testCasesContainer = document.getElementById('testCases');
                testCasesContainer.innerHTML = '';
                translationResult.test_results.forEach((result, idx) => {
                    const caseText = result[0]
                        .replace(/^Inputs:/, 'Inputs:')
                        .replace(/\nOutputs/, '\nOutputs');
                    // 格式化输入输出内容，保证换行显示
                    const formattedCase = caseText.replace(/\n/g, '<br>');
                    const resultDiv = document.createElement('div');
                    resultDiv.className = 'test-result';
                    resultDiv.innerHTML = `
                        <h3>测试用例 ${idx + 1}:</h3>
                        <div class="case-input"><strong>Inputs/Outputs:</strong><br>${formattedCase}</div>
                        <div class="case-result ${result[1] === 'OK' ? 'success' : 'error'}">
                            <strong>运行结果:</strong> ${result[1]}
                        </div>
                    `;
                    testCasesContainer.appendChild(resultDiv);
                });
                translationModal.style.display = "block";
            } else {
                alert('翻译增强失败: ' + translationResult.error);
            }
        } catch (error) {
            console.error('处理过程出错:', error);
            alert('处理过程出错: ' + error);
        }
    };
    // 执行翻译修复
    nextStepBtn.onclick = async function() {
        try {
            // 构造请求数据
            const repairData = {
                sourceLang: sourceLang.value,
                targetLang: targetLang.value,
                llmModel: llmModel.value,
                inputText: inputText.value,
                step: 'translation_repair'
            };
            // 发送请求
            const repairResult = await postData('/', repairData);
            if (repairResult.success) {
                // 展示修复后的代码
                document.getElementById('repairProgramCode').textContent = repairResult.translated_code;
                // 展示修复后的测试反馈
                const repairTestCasesContainer = document.getElementById('repairTestCases');
                repairTestCasesContainer.innerHTML = '';
                repairResult.test_results.forEach((result, idx) => {
                    // result 结构为 {idx, case, err_type, ...}
                    const caseText = result.case
                        .replace(/^Inputs:/, 'Inputs:')
                        .replace(/\nOutputs/, '\nOutputs');
                    const formattedCase = caseText.replace(/\n/g, '<br>');
                    const resultDiv = document.createElement('div');
                    resultDiv.className = 'test-result';
                    resultDiv.innerHTML = `
                        <h3>测试用例 ${idx + 1}:</h3>
                        <div class="case-input"><strong>Inputs/Outputs:</strong><br>${formattedCase}</div>
                        <div class="case-result ${result.err_type === 'PASS' ? 'success' : 'error'}">
                            <strong>运行结果:</strong> ${result.err_type}
                        </div>
                        ${result.err_msg ? `<div class="case-error"><strong>错误信息:</strong> ${result.err_msg}</div>` : ''}
                    `;
                    repairTestCasesContainer.appendChild(resultDiv);
                });
                // 显示修复弹窗
                repairModal.style.display = "block";
            } else {
                alert('翻译修复失败: ' + repairResult.error);
            }
        } catch (error) {
            alert('翻译修复请求出错: ' + error);
        }
    };
});
