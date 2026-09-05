# 🐍 Python Web Calculator

A modern, responsive, full-featured web calculator powered by a secure Python backend.

---

## ✨ Features

- **AST-Based Math Engine**: Evaluates mathematical expressions using Python's `ast` (Abstract Syntax Tree) without `eval()`, preventing security risks and arbitrary code execution.
- **Dual Mode**:
  - **Standard Mode**: Basic arithmetic (`+`, `-`, `×`, `÷`, `%`, `//`, `^`), parentheses, and sign negation.
  - **Scientific Mode**: Trigonometry (`sin`, `cos`, `tan`, `asin`, `acos`, `atan`), logarithms (`log10`, `ln`, `log2`), roots (`sqrt`, `cbrt`), powers, factorials (`n!`), absolute values, and constants ($\pi$, $e$).
- **Degree / Radian Toggle**: Seamlessly switch between DEG and RAD for trigonometric calculations.
- **Calculation History**: Review previous calculations, click on history items to reuse them, and clear session history.
- **Keyboard Friendly**: Full support for physical keyboard input with tactile visual button press feedback.
- **Responsive & Modern UI**: Dark glassmorphic design, smooth animations, live preview as you type, and one-click copy to clipboard.

---

## 📁 Project Structure

```
python-web-calculator/
├── app.py                  # Flask web server & API routes
├── calculator_engine.py    # AST-based mathematical evaluation engine
├── requirements.txt        # Project dependencies (Flask, pytest)
├── templates/
│   └── index.html          # Modern HTML5 calculator layout
├── static/
│   ├── css/
│   │   └── style.css       # Glassmorphic responsive styling
│   └── js/
│       └── calculator.js   # Client-side interaction & keyboard handling
├── tests/
│   └── test_calculator.py  # Unit and integration test suite
└── README.md               # Documentation
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Calculator Server
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running Tests

Run the automated unit and integration tests:
```bash
python -m unittest tests/test_calculator.py
```
or using pytest:
```bash
pytest
```

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
| --- | --- |
| `0`–`9`, `.` | Enter digits and decimals |
| `+`, `-`, `*`, `/`, `%` | Arithmetic operators |
| `^` | Exponent / Power |
| `(`, `)` | Parentheses |
| `Enter` or `=` | Calculate result |
| `Backspace` | Delete character |
| `Escape` | Clear all (`AC`) |
| `Ctrl` + `H` | Open / Close calculation history |
| `Ctrl` + `C` | Copy result to clipboard |
