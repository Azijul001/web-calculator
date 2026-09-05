let currentInput = '';
const display = document.getElementById('display');

function updateDisplay(value) {
  display.innerText = value || '0';
}

function appendNumber(num) {
  if (currentInput === '0' && num !== '.') {
    currentInput = num;
  } else {
    currentInput += num;
  }
  updateDisplay(currentInput);
}

function appendOperator(op) {
  if (!currentInput) return;
  const lastChar = currentInput.slice(-1);
  if (['+', '-', '*', '/'].includes(lastChar)) {
    currentInput = currentInput.slice(0, -1);
  }
  currentInput += op;
  updateDisplay(currentInput);
}

function clearDisplay() {
  currentInput = '';
  updateDisplay('0');
}

function deleteLast() {
  currentInput = currentInput.slice(0, -1);
  updateDisplay(currentInput);
}

function calculate() {
  try {
    // Sanitized expression evaluation for safety
    if (!currentInput) return;
    if (/\/0(?!\d)/.test(currentInput)) {
      updateDisplay('Error: Div by 0');
      currentInput = '';
      return;
    }
    const result = Function('"use strict"; return (' + currentInput + ')')();
    currentInput = String(Number(result.toFixed(8))); // format floating point safely
    updateDisplay(currentInput);
  } catch (err) {
    updateDisplay('Error');
    currentInput = '';
  }
}