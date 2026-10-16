# Suma — AI Text Summarizer

A polished, animated Streamlit web app for turning long text and text-based PDFs into concise bullet points. It works without OpenAI or any other API key.

## Features

- Modern dark UI with animated gradients, glass-style panels, hover effects, and responsive layout
- Paste text or upload a PDF
- Choose Short, Balanced, or Detailed summaries
- Adjust the maximum number of bullet points
- Download the result as a `.txt` file
- Offline extractive summarization using word-frequency scoring
- No API key, account, or paid AI service required

> **Transparency:** This project uses a lightweight extractive summarization algorithm, not a cloud LLM. It selects relevant sentences from the source rather than generating new wording. Scanned image-only PDFs may require OCR.

## Run locally

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Push this project to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io/).
3. Choose the repository and `app.py` as the main file.
4. Deploy. No secrets or API keys are needed.

## Project layout

```text
ai-text-summarizer/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Privacy

The summarization code runs inside the Streamlit app process and does not send the submitted text to an AI API. If you deploy the app publicly, follow your hosting provider's policies and avoid submitting sensitive documents.

## License

MIT
