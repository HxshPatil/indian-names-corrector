# 🧠 Indian Name Corrector

A smart tool to correct Indian first and last names using fuzzy string matching with optional fallback to AI (Anthropic Claude). It supports both **single name correction** and **bulk CSV uploads** through a Gradio interface.

---

## 🚀 Features

- 🔤 Corrects misspelled Indian names using RapidFuzz
- 🎓 Automatically strips salutations like "Mr", "Dr", etc.
- 🤖 AI fallback with Claude Sonnet (optional via `.env`)
- 📁 CSV mode to correct names in bulk

---

## 📦 Installation

### 1. Clone the repository

 ```bash
git clone https://github.com/HxshPatil/indian-names-corrector.git
cd indian-name-corrector 
```

### 2. install dependencies

 ```bash
pip install gradio pandas rapidfuzz python-dotenv anthropic chardet
```
### 3. create an .env file in your root directory for your anthropic api key(optional)

```shell
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```
### 4. run the code

```bash
python main.py
```