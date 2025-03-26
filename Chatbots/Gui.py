import tkinter as tk
from tkinter import scrolledtext
from nltk.chat.util import Chat, reflections

# Define chatbot response pairs
pairs = [
    [r"hi|hello|hey", ["Hello!", "Hi there!"]],
    [r"how are you?", ["I'm a bot, so I'm always fine!"]],
    [r"what is your name?", ["I'm ChatBot 1.0!"]],
    [r"bye|goodbye", ["Goodbye!", "Bye!"]],
    [r"(.*)", ["Sorry, I don't understand. Can you rephrase?"]]
]

# Initialize chatbot
chatbot = Chat(pairs, reflections)

# Create GUI
def create_gui():
    # Create the main window
    window = tk.Tk()
    window.title("Simple Chatbot")
    window.geometry("500x600")

    # Chat history display
    chat_history = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=60, height=20)
    chat_history.pack(padx=10, pady=10)
    chat_history.insert(tk.END, "Chatbot: Hi! How can I help you today?\n")
    chat_history.configure(state='disabled')  # Make it read-only

    # User input field
    user_input = tk.Entry(window, width=50)
    user_input.pack(padx=10, pady=10)

    # Function to handle user input
    def send_message():
        user_message = user_input.get().strip()
        if user_message:
            # Add user message to chat history
            chat_history.configure(state='normal')
            chat_history.insert(tk.END, f"You: {user_message}\n")
            
            # Get chatbot response
            bot_response = chatbot.respond(user_message)
            chat_history.insert(tk.END, f"Chatbot: {bot_response}\n")
            
            # Clear input field
            user_input.delete(0, tk.END)
            chat_history.configure(state='disabled')
            chat_history.see(tk.END)  # Auto-scroll to bottom

    # Send button
    send_button = tk.Button(window, text="Send", command=send_message)
    send_button.pack(pady=5)

    # Run the GUI loop
    window.mainloop()

# Run the chatbot GUI
if __name__ == "__main__":
    create_gui()