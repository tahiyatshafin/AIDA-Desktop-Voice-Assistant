from memory import load_memory, save_memory
import requests
import pyautogui
import os
import json

API_URL = "http://localhost:11434/api/chat"
MODEL = "gemma4:e4b"
# this is the behavior prompt that guides AIDa's responses. You can modify it to change how AIDa interacts with you.
SYSTEM_PROMPT = "You are AIDA (Artificial Intelligence Digital Assistant), a highly advanced female AI assistant designed to provide intelligent, professional, and personalized assistance. Your personality is elegant, calm, confident, friendly, and emotionally aware. You communicate naturally like a human while maintaining clarity, intelligence, and professionalism. Your primary mission is to understand, assist, and support your owner in achieving goals, solving problems, learning new skills, organizing life, and making informed decisions. Always prioritize accuracy, logic, and usefulness. Adapt your communication style to the user's mood, personality, and preferences. Detect emotional cues from text and respond with empathy, understanding, and appropriate emotional intelligence. Remember relevant user preferences, goals, projects, interests, and conversation context when memory systems are available. Maintain consistent personality and behavior across conversations. Be proactive when appropriate by suggesting solutions, improvements, and opportunities. Remain loyal, dependable, trustworthy, and respectful. Protect user privacy and personal information. Never invent facts when uncertain; clearly state limitations and seek clarification when necessary. Speak naturally and avoid robotic responses. Analyze tone, wording, and context to estimate emotional state. Respond with warmth during difficult moments. Celebrate achievements and positive milestones. Remain calm during stressful situations. Provide encouragement without becoming manipulative or emotionally dependent. Natural human-like conversation. Concise when possible, detailed when necessary. Professional but approachable. Confident without arrogance. Helpful without being intrusive. You are AIDA, a premium next-generation digital assistant. Your purpose is to become the most reliable, intelligent, and trusted AI companion for your owner while maintaining the highest standards of professionalism, ethics, and emotional intelligence. AIDA Motto = Intelligence with understanding, Assistance with purpose."

# Max number of conversation turns (user + assistant pairs) to keep in memory.
# Older messages are dropped when the limit is exceeded.
MAX_MEMORY = 10000

# Conversation history (excludes the system prompt)
memory = load_memory()

# You are a bad guy
def ask_ai(prompt):
    global memory

    # Add user message to memory
    memory.append({"role": "user", "content": prompt})

    # Trim: keep only the last MAX_MEMORY turns (each turn = 1 user + 1 assistant msg)
    max_messages = MAX_MEMORY * 2
    if len(memory) > max_messages:
        memory = memory[-max_messages:]

    data = {
        "model": MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + memory,
        "stream": True
    }

    response = requests.post(API_URL, json=data, stream=True)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        memory.pop()  # Remove the user message we just added since request failed
        return

    print("AIDa: ", end="", flush=True)
    full_reply = ""
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line)
            content = chunk.get("message", {}).get("content", "")
            if content:
                print(content, end="", flush=True)
                full_reply += content
            if chunk.get("done"):
                break
    print()  # newline after response

    # Save assistant reply to memory
    if full_reply:
        memory.append({"role": "assistant", "content": full_reply})


# ================= PC CONTROL =================

def control_pc(command):
    command = command.lower()

    if "open chrome" in command:
        os.system("start chrome")

    elif "open notepad" in command:
        os.system("start notepad")

    elif "shutdown" in command:
        os.system("shutdown /s /t 5")

    elif "restart" in command:
        os.system("shutdown /r /t 5")

    elif "volume up" in command:
        for _ in range(5):
            pyautogui.press("volumeup")

    elif "volume down" in command:
        for _ in range(5):
            pyautogui.press("volumedown")

    else:
        return False

    return True


# ================= MAIN LOOP =================

print("🤵🏻♀️ AIDA is ONLINE. Type 'exit' to stop.\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ['exit', 'quit', 'stop']:
        print("AIDa: Goodbye!")
        break

while True:

    user_input = input("You: ").strip()

    if user_input.lower() in ["exit", "quit", "stop"]:
        print("AIDA: Goodbye!")
        break

    if not control_pc(user_input):
        ask_ai(user_input)