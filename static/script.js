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
    const editButton = document.getElementById('editButton');
    
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    // 添加拖动功能
    const modalContent = document.querySelector('.modal-content');
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    let xOffset = 0;
    let yOffset = 0;

    modalContent.addEventListener('mousedown', dragStart);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', dragEnd);

    function dragStart(e) {
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
        if (e.target === modalContent) {
            isDragging = true;
        }
    }

    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            xOffset = currentX;
            yOffset = currentY;
            modalContent.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
        }
    }

    function dragEnd() {
        isDragging = false;
    }


    // 语言交换功能
    swapIcon.addEventListener('click', function() {
        const sourceValue = sourceLang.value;
        const targetValue = targetLang.value;
        sourceLang.value = targetValue;
        targetLang.value = sourceValue;
    });

    // 翻译按钮点击事件
    translateBtn.addEventListener('click', async function() {
        // 首先保存源代码
        const sourceData = {
            sourceLang: sourceLang.value,
            targetLang: targetLang.value,
            llmModel: llmModel.value,
            inputText: inputText.value,
            step: 'source_code_preservation'
        };

        try {
            const response = await fetch('/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(sourceData)
            });

            const result = await response.json();
            if (!result.success) {
                console.error('源代码保存失败:', result.error);
                return;
            }
            
            // 然后生成测试用例
            const testCaseData = {
                sourceLang: sourceLang.value,
                targetLang: targetLang.value,
                llmModel: llmModel.value,
                inputText: inputText.value,
                step: 'test_case_generation'
            };
            
            const testCaseResponse = await fetch('/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(testCaseData)
            });
            
            const testCaseResult = await testCaseResponse.json();
            console.log('测试用例生成结果:', testCaseResult);
            
            if (testCaseResult.success && testCaseResult.test_cases) {
                // 显示测试用例弹窗
                let content = `<div class="modal-header">测试用例</div>`;
                content += '<div class="test-cases">';
                
                testCaseResult.test_cases.forEach((testCase, index) => {
                    content += `
                        <div class="test-case">
                            <strong>用例 ${index + 1}:</strong>
                            <textarea id="testCase${index}">${testCase}</textarea>
                        </div>`;
                });
                
                content += '</div>';
                modalMessage.innerHTML = content;
                modal.style.display = "block";
            } else {
                console.error('测试用例生成失败:', testCaseResult.error);
            }
            
        } catch (error) {
            console.error('处理过程出错:', error);
        }
    });

    editButton.addEventListener('click', async function() {
        try {
            const testCases = [];
            const textareas = document.querySelectorAll('.test-case textarea');
            textareas.forEach(textarea => {
                testCases.push(textarea.value);
            });
    
            const response = await fetch('/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    step: 'test_case_generation',
                    test_cases: testCases,
                    targetLang: targetLang.value,  // 添加目标语言参数
                    isEditButton: true
                })
            });

            const result = await response.json();
            if (result.success) {
                alert('保存成功！');
                modal.style.display = "none";
                
                // 继续执行翻译增强和修复步骤
                const augmentData = {
                    sourceLang: sourceLang.value,
                    targetLang: targetLang.value,
                    llmModel: llmModel.value,
                    inputText: inputText.value,
                    step: 'translation_augmentation'
                };
                
                const augmentResponse = await fetch('/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(augmentData)
                });
                
                const augmentResult = await augmentResponse.json();
                if (augmentResult.success) {
                    // 最后执行翻译修复
                    const repairData = {
                        sourceLang: sourceLang.value,
                        targetLang: targetLang.value,
                        llmModel: llmModel.value,
                        inputText: augmentResult.output || inputText.value,
                        step: 'translation_repair'
                    };
                    
                    const repairResponse = await fetch('/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(repairData)
                    });
                    
                    const repairResult = await repairResponse.json();
                    if (repairResult.success && repairResult.output) {
                        outputText.value = repairResult.output;
                    }
                }
            } else {
                alert('保存失败：' + result.error);
            }
        } catch (error) {
            alert('保存失败：' + error);
        }
    });

});

