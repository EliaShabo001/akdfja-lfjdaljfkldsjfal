#!/usr/bin/env python3
"""
Local development runner for the Telegram Quiz Bot
This script runs both the Teacher Bot and Student Bot together
"""

import os
import sys
import threading
import time

def run_teacher_bot():
    """Run the teacher bot in a separate thread"""
    try:
        print("Starting Teacher Bot (TelegramBot)...")
        from TelegramBot import bot

        # Set environment variable to use polling
        os.environ['ENVIRONMENT'] = 'local'

        # Remove any existing webhook and start polling
        bot.remove_webhook()
        print("Teacher Bot is now running and listening for messages...")
        bot.polling(none_stop=True)

    except Exception as e:
        print(f"Error starting Teacher Bot: {e}")

def run_student_bot():
    """Run the student bot in a separate thread"""
    try:
        print("Starting Student Bot...")
        from StudentBot import student_bot

        print("Student Bot is now running and listening for messages...")
        student_bot.polling(none_stop=True)

    except Exception as e:
        print(f"Error starting Student Bot: {e}")

def run_local():
    """Run both bots in local development mode with polling"""
    print("Starting Telegram Quiz Bot System in LOCAL DEVELOPMENT mode...")
    print("This will start both Teacher Bot and Student Bot together")
    print("Using polling instead of webhooks for local testing")
    print("Press Ctrl+C to stop both bots\n")

    try:
        # Start webserver for keep-alive (optional)
        try:
            import webserver
            webserver.keep_alive()
        except ImportError:
            print("⚠️ Webserver module not available (optional)")
        except Exception as e:
            print(f"⚠️ Could not start webserver: {e}")

        # Start Teacher Bot in a separate thread
        teacher_thread = threading.Thread(target=run_teacher_bot, daemon=True)
        teacher_thread.start()

        # Give teacher bot a moment to start
        time.sleep(2)

        # Start Student Bot in a separate thread
        student_thread = threading.Thread(target=run_student_bot, daemon=True)
        student_thread.start()

        # Give student bot a moment to start
        time.sleep(2)

        print("Both bots initialized successfully!")
        print("Teacher Bot: @QuizForCollegeBot")
        print("Student Bot: @TestStudentCollegeBot")
        print("Test by sending /start to either bot on Telegram\n")

        # Keep the main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nBoth bots stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting bots: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_local()