# AI Model Chatbot with Gemini

A command-line chat client for Google Gemini with customizable conversation styles.

## Features

✨ **Five Conversation Styles:**
- **Funny** - Humorous and witty with jokes and puns
- **Strict** - Professional, formal, and concise
- **Lengthy** - Comprehensive and detailed explanations
- **Casual** - Friendly and conversational
- **Technical** - Expert-level technical depth

Simply choose your preferred style at startup, and the AI will adapt its responses accordingly!

## Setup

1. Create a `.env` file in the project root with the following contents:

   ```
   GEMINI_API_KEY=your_api_key_here
   GEMINI_MODEL=gemini-2.0-flash  # optional
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run:

   ```bash
   python ai_model.py
   ```

4. Select your preferred conversation style when prompted (1-5)

5. Start chatting! Type "exit" or "quit" to stop.

## Usage Example

```
============================================================
🎭 Choose Your Conversation Style
============================================================
1. Funny        - Humorous and witty with jokes and puns
2. Strict       - Professional, formal, and concise
3. Lengthy      - Comprehensive and detailed explanations
4. Casual       - Friendly and conversational
5. Technical    - Expert-level technical depth and details
============================================================
Select a style (1-5): 1

✅ Selected: Funny style

Gemini chat ready using gemini-2.0-flash (Funny style).
Type your message and press Enter. Type "exit" or "quit" to stop.
You: Tell me a joke
Gemini: Why did the AI go to school? Because it wanted to improve its learning model! 😄
```

## Owner

This file is created by Thanvir Assif

Enhanced with conversation style selection feature