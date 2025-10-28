document.addEventListener("DOMContentLoaded", function () {
  // 获取所有需要的元素
  const sourceLang = document.getElementById("source-lang");
  const targetLang = document.getElementById("target-lang");
  const llmModel = document.getElementById("llm-model");
  const playDemoBtn = document.getElementById("playDemoBtn");
  const videoModal = document.getElementById("videoModal");
  const demoVideo = document.getElementById("demoVideo");
  const videoModalCloseBtn = videoModal.querySelector(".close");
  const inputText = document.querySelector(".input-section textarea");
  const outputText = document.querySelector(".results-section textarea");
  const translateBtn = document.querySelector(".translate-btn");
  const copyBtn = document.querySelector(".copy-btn");
  const swapIcon = document.querySelector(".swap-icon");

  // 弹窗功能
  const modal = document.getElementById("modal");
  const modalMessage = document.getElementById("modal-message");
  const modalCloseBtn = modal.querySelector(".close");
  const modalNextStepBtn = modal.querySelector(".next-step");
  const modalReloadBtn = modal.querySelector(".reload");
  const translationModal = document.getElementById("translationModal");
  const closeBtn = translationModal.querySelector(".close");
  const translationReloadBtn = translationModal.querySelector(".reload");
  const nextStepBtn = translationModal.querySelector(".next-step");
  const modalContent = document.querySelector(".modal-content");

  const repairModal = document.getElementById("repairModal");
  const repairModalContent = repairModal.querySelector(".modal-content");
  const repairCloseBtn = repairModal.querySelector(".close");
  const repairReloadBtn = repairModal.querySelector(".reload");
  const repairNextStepBtn = repairModal.querySelector(".next-step");
  const repairProgramCode = document.getElementById("repairProgramCode");
  const repairTestCases = document.getElementById("repairTestCases");

  // 加载动画元素
  const loadingContainer = document.querySelector(".loading-container");
  const loadingText = document.querySelector(".loading-text");

  // 显示加载动画
  function showLoading(message) {
    loadingText.textContent = message;
    loadingContainer.style.display = "flex";
  }

  // 隐藏加载动画
  function hideLoading() {
    loadingContainer.style.display = "none";
  }
  // 工具函数：统一 fetch 请求
  async function postData(url = "/", data = {}) {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      return await response.json();
    } catch (error) {
      console.error("请求出错:", error);
      throw error;
    }
  }

  // 关闭按钮事件
  modalCloseBtn.onclick = () => (modal.style.display = "none");
  closeBtn.onclick = () => {
    translationModal.style.display = "none";
    outputText.value = document.getElementById("programCode").textContent;
  };
  repairCloseBtn.onclick = () => {
    repairModal.style.display = "none";
    outputText.value = repairProgramCode.textContent;
  };

  // 拖动弹窗
  let isDragging = false,
    currentX,
    currentY,
    initialX,
    initialY,
    xOffset = 0,
    yOffset = 0;
  const testModalContent = modal.querySelector(".modal-content");
  testModalContent.addEventListener("mousedown", dragStart);
  document.addEventListener("mousemove", drag);
  document.addEventListener("mouseup", dragEnd);

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
  function dragEnd() {
    isDragging = false;
  }

  // 语言交换
  swapIcon.onclick = () => {
    [sourceLang.value, targetLang.value] = [targetLang.value, sourceLang.value];
  };

  // 复制按钮
  copyBtn.onclick = function () {
    const text = outputText.value;
    navigator.clipboard
      .writeText(text)
      .then(() => {
        copyBtn.textContent = "已复制";
        setTimeout(() => {
          copyBtn.textContent = "复制";
        }, 1000);
      })
      .catch((err) => {
        alert("复制失败，请手动复制。");
      });
  };

  // reload 按钮事件绑定
  modalReloadBtn.onclick = function () {
    translateBtn.onclick();
  };
  translationReloadBtn.onclick = function () {
    modalNextStepBtn.onclick();
  };

  // 视频播放按钮事件
  playDemoBtn.onclick = function () {
    videoModal.style.display = "block";
    demoVideo.play().catch(function (error) {
      console.log("视频播放失败:", error);
    });
  };

  // 视频加载错误处理
  demoVideo.addEventListener("error", function (e) {
    console.error("视频加载错误:", demoVideo.error);
  });

  // 视频模态框关闭按钮事件
  videoModalCloseBtn.onclick = function () {
    videoModal.style.display = "none";
    demoVideo.pause();
    demoVideo.currentTime = 0;
  };
  repairReloadBtn.onclick = function () {
    nextStepBtn.onclick();
  };

  // 获取顶部选项卡
  const typeItems = document.querySelectorAll(".translation-types .type-item");

  // 辅助函数：激活指定索引的type-item
  function activateTypeTab(index) {
    typeItems.forEach((item, idx) => {
      if (idx === index) {
        item.className = "type-item active";
      } else {
        item.className = "type-item";
      }
    });
  }

  // 翻译按钮点击事件
  translateBtn.onclick = async function () {
    // 激活第一个选项卡（生成测试用例）
    activateTypeTab(0);
    try {
      // 显示加载动画 - 正在生成测试用例
      showLoading("正在生成测试用例");

      // 保存源代码
      const sourceData = {
        sourceLang: sourceLang.value,
        targetLang: targetLang.value,
        llmModel: llmModel.value,
        inputText: inputText.value,
        step: "source_code_preservation",
      };
      const result = await postData("/", sourceData);
      if (!result.success) {
        hideLoading();
        return console.error("源代码保存失败:", result.error);
      }

      // 生成测试用例
      const testCaseData = { ...sourceData, step: "test_case_generation" };
      const testCaseResult = await postData("/", testCaseData);
      if (testCaseResult.success && testCaseResult.test_cases) {
        let content = `<div class="modal-header">测试用例</div>
        <div class="format-info">
          <div class="format-section">
            <h4>Python 测试用例格式：</h4>
            <pre>
Inputs:
Variable1 = Data1
Variable2 = Data2
...
Outputs:
result1
result2
...</pre>
          </div>
          <div class="format-section">
            <h4>C++/Java 测试用例格式：</h4>
            <pre>
Inputs:
type variable1 = value1 ;
type variable2 = value2 ;
...
Outputs (return_type):
result1
result2
...</pre>
          </div>
        </div>
        <div class="test-cases">`;
        testCaseResult.test_cases.forEach((testCase, idx) => {
          content += `<div class="test-case"><strong>用例 ${
            idx + 1
          }:</strong><textarea id="testCase${idx}">${testCase}</textarea></div>`;
        });
        content += "</div>";
        modalMessage.innerHTML = content;

        // 隐藏加载动画
        hideLoading();

        // 显示测试用例弹窗
        modal.style.display = "block";
      } else {
        hideLoading();
        console.error("测试用例生成失败:", testCaseResult.error);
        alert("测试用例生成失败: " + testCaseResult.error);
      }
    } catch (error) {
      hideLoading();
      console.error("处理过程出错:", error);
    }
  };

  // 测试用例弹窗的下一步按钮点击事件
  modalNextStepBtn.onclick = async function () {
    // 激活第二个选项卡（翻译增强）
    activateTypeTab(1);
    try {
      // 显示加载动画 - 正在执行翻译增强
      showLoading("正在执行翻译增强");

      const testCases = Array.from(
        document.querySelectorAll(".test-case textarea")
      ).map((t) => t.value);
      const saveResult = await postData("/", {
        step: "test_case_generation",
        test_cases: testCases,
        targetLang: targetLang.value,
        isEditButton: true,
      });
      if (!saveResult.success) {
        hideLoading();
        return alert("保存失败: " + saveResult.error);
      }

      modal.style.display = "none";
      // 执行翻译增强
      const translationData = {
        sourceLang: sourceLang.value,
        targetLang: targetLang.value,
        llmModel: llmModel.value,
        inputText: inputText.value,
        step: "translation_augmentation",
      };
      const translationResult = await postData("/", translationData);
      if (translationResult.success) {
        document.getElementById("programCode").textContent =
          translationResult.translated_code;
        const testCasesContainer = document.getElementById("testCases");
        testCasesContainer.innerHTML = "";
        translationResult.test_results.forEach((result, idx) => {
          const caseText = result[0]
            .replace(/^Inputs:/, "Inputs:")
            .replace(/\nOutputs/, "\nOutputs");
          // 格式化输入输出内容，保证换行显示
          const formattedCase = caseText.replace(/\n/g, "<br>");
          const resultDiv = document.createElement("div");
          resultDiv.className = "test-result";
          resultDiv.innerHTML = `
                        <h3>测试用例 ${idx + 1}:</h3>
                        <div class="case-input"><strong>Inputs/Outputs:</strong><br>${formattedCase}</div>
                        <div class="case-result ${
                          result[1] === "OK" ? "success" : "error"
                        }">
                            <strong>运行结果:</strong> ${result[1]}
                        </div>
                    `;
          testCasesContainer.appendChild(resultDiv);
        });

        // 隐藏加载动画
        hideLoading();

        // 显示翻译结果弹窗
        translationModal.style.display = "block";
      } else {
        hideLoading();
        alert("翻译增强失败: " + translationResult.error);
      }
    } catch (error) {
      hideLoading();
      console.error("处理过程出错:", error);
      alert("处理过程出错: " + error);
    }
  };
  // 执行翻译修复
  nextStepBtn.onclick = async function () {
    // 激活第三个选项卡（翻译修复）
    activateTypeTab(2);
    try {
      // 自动隐藏翻译结果弹窗
      translationModal.style.display = "none";
      // 显示加载动画 - 正在执行翻译修复
      showLoading("正在执行翻译修复");

      // 构造请求数据
      const repairData = {
        sourceLang: sourceLang.value,
        targetLang: targetLang.value,
        llmModel: llmModel.value,
        inputText: inputText.value,
        step: "translation_repair",
      };
      // 发送请求
      const repairResult = await postData("/", repairData);
      if (repairResult.success) {
        // 展示修复后的代码
        document.getElementById("repairProgramCode").textContent =
          repairResult.translated_code;
        // 展示fetch_feedbacks_results（调试信息前的测试用例运行结果）
        const repairTestCasesSection = document.getElementById(
          "repairTestCasesFeedback"
        );
        if (repairTestCasesSection && repairResult.fetch_feedbacks_results) {
          repairTestCasesSection.innerHTML = "";
          repairResult.fetch_feedbacks_results.forEach((result, idx) => {
            const caseText = result[0]
              .replace(/^Inputs:/, "Inputs:")
              .replace(/\nOutputs/, "\nOutputs");
            const formattedCase = caseText.replace(/\n/g, "<br>");
            const resultDiv = document.createElement("div");
            resultDiv.className = "test-result";
            resultDiv.innerHTML = `
                            <h3>测试用例 ${idx + 1}:</h3>
                            <div class="case-input"><strong>Inputs/Outputs:</strong><br>${formattedCase}</div>
                            <div class="case-result ${
                              result[1] === "OK" ? "success" : "error"
                            }">
                                <strong>运行结果:</strong> ${result[1]}
                            </div>
                        `;
            repairTestCasesSection.appendChild(resultDiv);
          });
        }
        // 展示修复后的测试反馈
        const repairTestCasesContainer =
          document.getElementById("repairTestCases");
        repairTestCasesContainer.innerHTML = "";
        repairResult.test_results.forEach((result, idx) => {
          // result 结构为 {idx, case, err_type, ...}
          const caseText = result.case
            .replace(/^Inputs:/, "Inputs:")
            .replace(/\nOutputs/, "\nOutputs");
          const formattedCase = caseText.replace(/\n/g, "<br>");
          const resultDiv = document.createElement("div");
          resultDiv.className = "test-result";
          resultDiv.innerHTML = `
                        <h3>测试用例 ${idx + 1}:</h3>
                        <div class="case-input"><strong>Inputs/Outputs:</strong><br>${formattedCase}</div>
                        <div class="case-result ${
                          result.err_type === "PASS" ? "success" : "error"
                        }">
                            <strong>运行结果:</strong> ${result.err_type}
                        </div>
                        ${
                          result.err_msg
                            ? `<div class="case-error"><strong>错误信息:</strong> ${result.err_msg}</div>`
                            : ""
                        }
                    `;
          repairTestCasesContainer.appendChild(resultDiv);
        });

        // 隐藏加载动画
        hideLoading();

        // 显示修复弹窗
        repairModal.style.display = "block";
      } else {
        hideLoading();
        alert("翻译修复失败: " + repairResult.error);
      }
    } catch (error) {
      hideLoading();
      alert("翻译修复请求出错: " + error);
    }
  };
  repairNextStepBtn.onclick = () => {
    repairModal.style.display = "none";
    outputText.value = repairProgramCode.textContent;
  };
});
