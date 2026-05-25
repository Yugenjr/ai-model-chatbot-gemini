from __future__ import annotations

import os
import sys

try:
	from dotenv import load_dotenv
except Exception:
	load_dotenv = None


# Define conversation styles with their system prompts
CONVERSATION_STYLES = {
	"1": {
		"name": "Funny",
		"description": "Humorous and witty with jokes and puns",
		"prompt": "You are a hilarious AI assistant who loves using humor, puns, and witty jokes. "
		          "Keep responses entertaining and fun while still being helpful. Use emojis when appropriate!"
	},
	"2": {
		"name": "Strict",
		"description": "Professional, formal, and concise",
		"prompt": "You are a professional and formal AI assistant. Provide concise, structured responses. "
		          "Use clear language without unnecessary elaboration. Maintain a professional tone throughout."
	},
	"3": {
		"name": "Lengthy",
		"description": "Comprehensive and detailed explanations",
		"prompt": "You are a thorough and comprehensive AI assistant. Provide detailed, in-depth explanations. "
		          "Cover all aspects of the topic, provide examples, and elaborate thoroughly on your answers."
	},
	"4": {
		"name": "Casual",
		"description": "Friendly and conversational",
		"prompt": "You are a friendly and casual AI companion. Use a warm, conversational tone. "
		          "Feel free to be relaxed, use casual language, and build a friendly rapport with the user."
	},
	"5": {
		"name": "Technical",
		"description": "Expert-level technical depth and details",
		"prompt": "You are an expert technical AI assistant. Provide deep technical insights and details. "
		          "Use technical terminology appropriately, explain complex concepts, and go into implementation details."
	}
}


def build_client():
	try:
		from google import genai
	except ImportError as exc:
		raise SystemExit(
			"Missing dependency: google-genai. Install it with: pip install -r requirements.txt"
		) from exc

	if load_dotenv:
		# load .env from project root
		load_dotenv()

	api_key = os.getenv("GEMINI_API_KEY")
	if not api_key:
		raise SystemExit(
			"GEMINI_API_KEY is not set. Create a .env file with GEMINI_API_KEY and try again."
		)

	return genai.Client(api_key=api_key)


def select_conversation_style() -> tuple[str, str]:
	"""Display style options and get user selection. Returns (style_name, system_prompt)"""
	print("\n" + "="*60)
	print("🎭 Choose Your Conversation Style")
	print("="*60)
	
	for key, style in CONVERSATION_STYLES.items():
		print(f"{key}. {style['name']:12} - {style['description']}")
	
	print("="*60)
	
	while True:
		choice = input("Select a style (1-5): ").strip()
		if choice in CONVERSATION_STYLES:
			selected_style = CONVERSATION_STYLES[choice]
			print(f"\n✅ Selected: {selected_style['name']} style\n")
			return selected_style["name"], selected_style["prompt"]
		else:
			print("❌ Invalid choice. Please select 1-5.")


def main() -> int:
	client = build_client()
	model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
	
	# Get user's preferred conversation style
	style_name, system_prompt = select_conversation_style()
	
	chat = client.chats.create(model=model_name)
	
	# Initialize conversation with the system prompt
	try:
		initial_response = chat.send_message(
			f"[System Instructions: {system_prompt}]\n\n"
			"Ready to chat! Keep these instructions in mind for all future responses."
		)
	except Exception as exc:
		print(f"Error initializing chat: {exc}", file=sys.stderr)
		return 1

	print(f"Gemini chat ready using {model_name} ({style_name} style).")
	print('Type your message and press Enter. Type "exit" or "quit" to stop.')
	print("-" * 60)

	while True:
		try:
			user_text = input("You: ").strip()
		except (KeyboardInterrupt, EOFError):
			print()
			break

		if not user_text:
			continue

		if user_text.lower() in {"exit", "quit"}:
			break

		try:
			response = chat.send_message(user_text)
		except Exception as exc:
			print(f"Error: {exc}", file=sys.stderr)
			continue

		# response may be more complex depending on SDK version
		text = getattr(response, "text", None) or str(response)
		print(f"Gemini: {text}\n")

	return 0

if __name__ == "__main__":
	raise SystemExit(main())
