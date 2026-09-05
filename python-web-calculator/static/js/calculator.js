/**
 * Interactive Client Script for Python Web Calculator
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const appContainer = document.querySelector(".app-container");
  const expressionInput = document.getElementById("expressionInput");
  const displayPrevious = document.getElementById("displayPrevious");
  const livePreview = document.getElementById("livePreview");
  const errorBanner = document.getElementById("errorBanner");
  const errorText = document.getElementById("errorText");
  const btnCopyResult = document.getElementById("btnCopyResult");

  // Mode & Feature Toggles
  const btnStandardMode = document.getElementById("btnStandardMode");
  const btnScientificMode = document.getElementById("btnScientificMode");
  const scientificKeypad = document.getElementById("scientificKeypad");
  const btnAngleMode = document.getElementById("btnAngleMode");
  const angleLabel = btnAngleMode.querySelector(".badge-label");

  // History Drawer
  const btnToggleHistory = document.getElementById("btnToggleHistory");
  const historyDrawer = document.getElementById("historyDrawer");
  const btnCloseHistory = document.getElementById("btnCloseHistory");
  const btnClearHistory = document.getElementById("btnClearHistory");
  const historyList = document.getElementById("historyList");

  // Help Modal
  const btnShowHelp = document.getElementById("btnShowHelp");
  const helpModal = document.getElementById("helpModal");
  const btnCloseHelp = document.getElementById("btnCloseHelp");

  // Calculator Buttons
  const btnClear = document.getElementById("btnClear");
  const btnBackspace = document.getElementById("btnBackspace");
  const btnNegate = document.getElementById("btnNegate");
  const btnEquals = document.getElementById("btnEquals");
  const insertKeys = document.querySelectorAll("[data-insert]");

  // State
  let angleMode = "deg";
  let lastResult = "";
  let isResultState = false;
  let previewDebounceTimer = null;

  // Initial focus
  expressionInput.focus();

  // =========================================================================
  // Expression Editing & Helper Functions
  // =========================================================================

  function clearError() {
    errorBanner.classList.add("hidden");
    errorText.textContent = "";
  }

  function showError(message) {
    errorText.textContent = message;
    errorBanner.classList.remove("hidden");
  }

  function insertText(text) {
    clearError();
    const start = expressionInput.selectionStart || expressionInput.value.length;
    const end = expressionInput.selectionEnd || expressionInput.value.length;
    const currentVal = expressionInput.value;

    // If user just evaluated and enters a number or function, start fresh.
    // If they enter an operator (+, -, *, /, ^), keep the last result and append.
    if (isResultState) {
      isResultState = false;
      const isOperator = ["+", "-", "×", "÷", "*", "/", "^", "%", "//"].includes(text);
      if (!isOperator) {
        expressionInput.value = "";
      }
    }

    const newVal = expressionInput.value.substring(0, start) + text + expressionInput.value.substring(end);
    expressionInput.value = newVal;

    const newCursorPos = start + text.length;
    expressionInput.setSelectionRange(newCursorPos, newCursorPos);
    expressionInput.focus();

    triggerLivePreview();
  }

  function deleteChar() {
    clearError();
    if (isResultState) {
      isResultState = false;
      expressionInput.value = "";
      return;
    }
    const start = expressionInput.selectionStart;
    const end = expressionInput.selectionEnd;
    const currentVal = expressionInput.value;

    if (start === end && start > 0) {
      expressionInput.value = currentVal.substring(0, start - 1) + currentVal.substring(end);
      expressionInput.setSelectionRange(start - 1, start - 1);
    } else if (start !== end) {
      expressionInput.value = currentVal.substring(0, start) + currentVal.substring(end);
      expressionInput.setSelectionRange(start, start);
    }
    expressionInput.focus();
    triggerLivePreview();
  }

  function clearAll() {
    expressionInput.value = "";
    livePreview.textContent = "";
    clearError();
    isResultState = false;
    expressionInput.focus();
  }

  function negateCurrent() {
    clearError();
    let val = expressionInput.value.trim();
    if (!val) return;

    if (val.startsWith("-(") && val.endsWith(")")) {
      expressionInput.value = val.slice(2, -1);
    } else if (val.startsWith("-")) {
      expressionInput.value = val.substring(1);
    } else {
      expressionInput.value = `-(${val})`;
    }
    isResultState = false;
    expressionInput.focus();
    triggerLivePreview();
  }

  // =========================================================================
  // Calculation API Calls
  // =========================================================================

  async function calculateResult() {
    const expr = expressionInput.value.trim();
    if (!expr) return;

    try {
      const response = await fetch("/api/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          expression: expr,
          angle_mode: angleMode
        })
      });

      const data = await response.json();

      if (data.success) {
        clearError();
        displayPrevious.textContent = `${expr} =`;
        expressionInput.value = data.result;
        lastResult = data.result;
        livePreview.textContent = "";
        isResultState = true;
        fetchHistory();
      } else {
        showError(data.error || "Calculation failed");
      }
    } catch (err) {
      showError("Server connection error. Please verify the backend is running.");
    }
  }

  function triggerLivePreview() {
    clearTimeout(previewDebounceTimer);
    const expr = expressionInput.value.trim();

    if (!expr || expr.length < 2 || isResultState) {
      livePreview.textContent = "";
      return;
    }

    previewDebounceTimer = setTimeout(async () => {
      try {
        const response = await fetch("/api/calculate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            expression: expr,
            angle_mode: angleMode
          })
        });
        const data = await response.json();
        if (data.success && expressionInput.value.trim() === expr) {
          livePreview.textContent = `= ${data.result}`;
        } else {
          livePreview.textContent = "";
        }
      } catch {
        livePreview.textContent = "";
      }
    }, 250);
  }

  // =========================================================================
  // History Management
  // =========================================================================

  async function fetchHistory() {
    try {
      const res = await fetch("/api/history");
      const data = await res.json();
      renderHistory(data.history || []);
    } catch (err) {
      console.warn("Could not fetch history:", err);
    }
  }

  function renderHistory(items) {
    if (!items.length) {
      historyList.innerHTML = '<div class="history-empty">No calculations yet</div>';
      return;
    }

    historyList.innerHTML = items.map((item) => `
      <div class="history-item" data-expr="${encodeURIComponent(item.expression)}" data-res="${encodeURIComponent(item.result)}">
        <div class="history-expr">${escapeHtml(item.expression)} =</div>
        <div class="history-res">${escapeHtml(item.result)}</div>
      </div>
    `).join("");

    // Attach click listeners to history items
    historyList.querySelectorAll(".history-item").forEach((el) => {
      el.addEventListener("click", () => {
        const expr = decodeURIComponent(el.getAttribute("data-expr"));
        const res = decodeURIComponent(el.getAttribute("data-res"));
        expressionInput.value = res;
        displayPrevious.textContent = `${expr} =`;
        isResultState = true;
        clearError();
        historyDrawer.classList.remove("open");
        expressionInput.focus();
      });
    });
  }

  async function clearHistory() {
    try {
      await fetch("/api/clear-history", { method: "POST" });
      renderHistory([]);
    } catch (err) {
      console.warn("Failed to clear history", err);
    }
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // =========================================================================
  // Event Listeners & Keypad Handling
  // =========================================================================

  // Keypad button clicks
  insertKeys.forEach((btn) => {
    btn.addEventListener("click", () => {
      const textToInsert = btn.getAttribute("data-insert");
      insertText(textToInsert);
    });
  });

  btnClear.addEventListener("click", clearAll);
  btnBackspace.addEventListener("click", deleteChar);
  btnNegate.addEventListener("click", negateCurrent);
  btnEquals.addEventListener("click", calculateResult);

  // Mode Toggling
  btnStandardMode.addEventListener("click", () => {
    btnStandardMode.classList.add("active");
    btnScientificMode.classList.remove("active");
    scientificKeypad.classList.add("hidden");
    appContainer.classList.remove("scientific-active");
  });

  btnScientificMode.addEventListener("click", () => {
    btnScientificMode.classList.add("active");
    btnStandardMode.classList.remove("active");
    scientificKeypad.classList.remove("hidden");
    appContainer.classList.add("scientific-active");
  });

  // Angle Mode Toggle (DEG / RAD)
  btnAngleMode.addEventListener("click", () => {
    angleMode = angleMode === "deg" ? "rad" : "deg";
    angleLabel.textContent = angleMode.toUpperCase();
    triggerLivePreview();
  });

  // History Drawer Controls
  btnToggleHistory.addEventListener("click", () => {
    historyDrawer.classList.toggle("open");
    if (historyDrawer.classList.contains("open")) {
      fetchHistory();
    }
  });

  btnCloseHistory.addEventListener("click", () => {
    historyDrawer.classList.remove("open");
  });

  btnClearHistory.addEventListener("click", clearHistory);

  // Copy Result Button
  btnCopyResult.addEventListener("click", async () => {
    const textToCopy = expressionInput.value || lastResult;
    if (!textToCopy) return;

    try {
      await navigator.clipboard.writeText(textToCopy);
      btnCopyResult.classList.add("copied");
      setTimeout(() => btnCopyResult.classList.remove("copied"), 1500);
    } catch {
      // Fallback
      expressionInput.select();
      document.execCommand("copy");
      btnCopyResult.classList.add("copied");
      setTimeout(() => btnCopyResult.classList.remove("copied"), 1500);
    }
  });

  // Help Modal
  btnShowHelp.addEventListener("click", () => helpModal.showModal());
  btnCloseHelp.addEventListener("click", () => helpModal.close());
  helpModal.addEventListener("click", (e) => {
    if (e.target === helpModal) helpModal.close();
  });

  // Real-time input typing listener
  expressionInput.addEventListener("input", () => {
    clearError();
    triggerLivePreview();
  });

  // =========================================================================
  // Keyboard Shortcuts & Physical Key Binding
  // =========================================================================

  window.addEventListener("keydown", (e) => {
    // If modal is open and user presses Escape, native dialog handles it
    if (helpModal.open) return;

    // Toggle history shortcut (Ctrl+H)
    if (e.ctrlKey && e.key.toLowerCase() === "h") {
      e.preventDefault();
      historyDrawer.classList.toggle("open");
      if (historyDrawer.classList.contains("open")) fetchHistory();
      return;
    }

    if (e.key === "Enter" || e.key === "=") {
      e.preventDefault();
      highlightKey(btnEquals);
      calculateResult();
    } else if (e.key === "Escape") {
      e.preventDefault();
      highlightKey(btnClear);
      clearAll();
    } else if (e.key === "Backspace") {
      // If user is not directly typing in input, delete
      if (document.activeElement !== expressionInput) {
        e.preventDefault();
        highlightKey(btnBackspace);
        deleteChar();
      }
    } else {
      // Find matching button to highlight on physical press
      const keyMap = {
        "*": "×",
        "/": "÷",
      };
      const mappedChar = keyMap[e.key] || e.key;
      const matchedBtn = Array.from(insertKeys).find(
        (b) => b.getAttribute("data-insert") === mappedChar
      );
      if (matchedBtn) {
        highlightKey(matchedBtn);
      }
    }
  });

  function highlightKey(btnElement) {
    if (!btnElement) return;
    btnElement.classList.add("keyboard-active");
    setTimeout(() => btnElement.classList.remove("keyboard-active"), 120);
  }

  // Load initial history
  fetchHistory();
});
