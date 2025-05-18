from chatbot import agricola_chat

print("Welcome to Agricola! Type 'exit' to quit.\n")

while True:
    user_input = input("User: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    reply = agricola_chat(user_input)
    print("Agricola: Thinking...")
    print("Agricola:", reply)
