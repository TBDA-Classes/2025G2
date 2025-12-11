# Sphinx Documentation – How to Build and View

This folder contains the complete Sphinx documentation for the G2 Project.  
Follow the guide below to install the required tools, build the documentation, and view it locally.

---

## 1. Install Python Dependencies

Ensure you have Python 3.9+ installed.

Then install the required packages:

```bash
pip install -r requirements.txt
```
If Graphviz is not installed on your system (needed for diagrams), install it from:
- Windows: https://graphviz.org/download/
- macOS:
```bash
brew install graphviz
```
- Linux
```bash
sudo apt install graphviz
```
---

## 2. Build the documentation

Move to the documentation folder:
```bash
cd sphinx_documentation
```
- Windows:
```bash
make.bat html
```  
- macOS:
```bash
make html
```
The generated documentation will appear in:
```bash
build/html/
```

---

## 3. Open the documentation

Open the file:
```bash
build/html/index.html
```

---

## 4. Notes

- Do not edit the build/ directory. It is regenerated on every build.
- All editable content is located inside the source/ directory.
- **This documentation is continuously being updated, so you may not be viewing the final version.**
