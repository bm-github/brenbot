# OpenAI Chatbot with Tkinter

This is a GUI-based chatbot application built using Python’s `tkinter` library and OpenAI’s GPT-3.5 API. It allows users to interact with the chatbot, save and load conversations, and regenerate responses. The chatbot has different modes, including code analysis and adding comments to code.

## Features

- **Interactive Chatbot**: A simple, user-friendly interface for chatting with the OpenAI GPT-3.5 model.
- **Code Analysis**: Break down code or add comments to code via specialised prompts.
- **Conversation History**: Save and load conversations from files stored in a `history` folder.
- **Regenerate Responses**: Regenerate the last AI response to the user’s message.
- **File Management**: Load and delete saved conversations from the UI.

## Prerequisites

Before running the chatbot, ensure you have the following:

- Python 3.x
- OpenAI API Key
- Required Python libraries:
  - `openai`
  - `tkinter`

You can install the `openai` library using pip:

```bash
pip install openai

How to Run

    Clone or download this repository.

    Install the required dependencies using the command above.

    Run the script:

    bash

    python chatbot.py

    Upon running the application, you will be prompted to enter your OpenAI API key.

How to Use

    API Key Input: The application starts with a window where you need to input your OpenAI API key.
    Chat Window: After entering the API key, a chat window will open. You can start interacting with the chatbot by typing in the input box at the bottom and pressing "Send" or pressing Ctrl+Enter.
    Special Modes:
        Code Breakdown: Click the "Code Breakdown" button to have the chatbot analyse code you input.
        Add Comments: Click the "Add Comments" button to make the chatbot add comments to each line of provided code.
    Save/Load Conversations: Use the "Save Conversation" and "Load Conversation" buttons to manage chat history.
    Delete Files: Use the "Delete File" button to delete saved conversations from the history folder.

File Structure

    Main Script: The main functionality resides in chatbot.py, which contains the logic for interacting with OpenAI’s API and the Tkinter GUI.
    history/: This folder stores saved conversations as JSON files.

Key Functions
Chat Functionality

    send_message(entry): Sends the user input to the chatbot and displays the response.
    regenerate_response(): Regenerates the last AI response.
    update_chat_log(): Updates the chat log UI with the conversation history.

Conversation Management

    save_conversation(): Saves the current conversation as a JSON file.
    load_conversation_from_file(filename): Loads a saved conversation from a JSON file.
    delete_json_file(filename): Deletes a saved conversation file.

File Management

    update_file_listbox(): Updates the Listbox UI to show all files in the history folder.

Example UI

The UI consists of:

    A chat area with a scrollable chat log.
    Input box for typing messages.
    Buttons to send messages, regenerate responses, and switch chatbot modes.
    A Listbox to manage saved conversations.

Customisation

    System Messages: You can modify the chatbot’s behaviour by changing the system message in the code_system_message() and comments_system_message() functions.
    Temperature: You can adjust the temperature of the AI’s responses by modifying the temperature parameter in the openai.ChatCompletion.create() call.