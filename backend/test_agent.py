from agent import chat_with_agent

while True:
    user_input = input("You: ")
    print("Bot:", chat_with_agent(user_input))
