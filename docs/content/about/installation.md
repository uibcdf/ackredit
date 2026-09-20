# Installation

Ackredit can be installed using `pip`. It is designed to be lightweight and has zero mandatory dependencies for its core functionality.

## Standard Installation
```bash
pip install ackredit
```

## Extra Features
Some advanced features require additional Python dependencies:

### Web UI
To enable the interactive dashboard (`ackredit.serve_ui()`):
```bash
pip install "ackredit[web]"
```

## System Requirements (Optional)
To use the automatic **PDF compilation** feature, you need a working LaTeX distribution installed on your system:
*   **Linux:** `sudo apt install texlive-latex-extra` (or similar)
*   **macOS:** [MacTeX](https://tug.org/mactex/)
*   **Windows:** [MiKTeX](https://miktex.org/)
