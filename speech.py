# VOICE ASSISTANT - HELENA

import speech_recognition as sr
import openai
from googletrans import Translator  # For translation
from gtts import gTTS  # For text-to-speech
import os
import requests
import time
import re

# Configure Speech Recognition for Greek
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Configure OpenAI GPT-3
openai.api_key = 'INSERT YOUR OWN OPENAI API KEY'


# Function to Recognize Greek Speech
def listen_to_user():
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Σας ακούω...")
        audio = recognizer.listen(source)
        try:
            greek_text = recognizer.recognize_google(audio, language="el-GR")
            return greek_text
        except sr.UnknownValueError:
            print("Συγγνώμη, δεν κατάλαβα τι μου είπατε.")
            return ""
        except sr.RequestError as e:
            print(f"Ένα σφάλμα προέκυψε: {e}")
            return ""

# Function to Translate Greek to English with Retry Mechanism
def translate_to_english_with_retry(greek_text):
    max_retries = 3  # Set the maximum number of retries
    retry_delay = 2  # Set the delay (in seconds) between retries

    for _ in range(max_retries):
        try:
            translator = Translator()
            english_text = translator.translate(greek_text, src="el", dest="en").text
            return english_text
        except requests.exceptions.RequestException as e:
            print("Σφάλμα κατά τη μετάφραση:", e)
            print("Επαναπροσπάθεια σε {} δευτερόλεπτα...".format(retry_delay))
            time.sleep(retry_delay)

    print("Max retries reached. Unable to translate the text.")
    return ""

# Function to Translate English to Greek with Retry Mechanism
def translate_to_greek_with_retry(english_text):
    max_retries = 3  # Set the maximum number of retries
    retry_delay = 2  # Set the delay (in seconds) between retries

    for _ in range(max_retries):
        try:
            translator = Translator()
            greek_text = translator.translate(english_text, src="en", dest="el").text
            return greek_text
        except requests.exceptions.RequestException as e:
            print("Σφάλμα κατά τη μετάφραση:", e)
            print("Επαναπροσπάθεια σε {} δευτερόλεπτα...".format(retry_delay))
            time.sleep(retry_delay)

    print("Μέγιστος αριθμός επαναπροσπαθειών. Αδυναμία μετάφρασης του κειμένου.")
    return ""

# Function to Interact with ChatGPT
def chat_with_gpt(input_text, language="en"):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=input_text,
        max_tokens=100,
        temperature=0.3,
        user=language,  # Set the user language to English
    )
    return response.choices[0].text.strip()

# Function to Convert Text to Greek Speech
def speak_in_greek(text):
    tts = gTTS(text, lang='el')
    tts.save("assistant_response.mp3")
    os.system("mpg123 assistant_response.mp3")  # Adjust this based on your system
    os.remove("assistant_response.mp3")  # Remove the generated audio file after playing

# Format GPT-3 Response
def format_response(response):
    # Add a prefix or format the response as needed
    formatted_response = "Assistant: " + response
    return formatted_response

# Main Loop
while True:
    user_input = listen_to_user()
    if not user_input:
        continue

    print("Εσείς είπατε (Ελληνικά - Greek):", user_input)

    if "exit" in user_input:
        print("Τέλος...")
        break

    # Translate Greek to English with retry
    english_input = translate_to_english_with_retry(user_input)

    if english_input:
        print("Εσείς είπατε σε μετάφραση (Αγγλικά - English):", english_input)

        # Get English response from GPT-3
        gpt_response = chat_with_gpt(english_input, language="en")  # Set the language to English

        print("Helena (Αγγλικά - English):", gpt_response)

        # Translate the English response to Greek
        greek_response = translate_to_greek_with_retry(gpt_response)

        if greek_response:
            formatted_greek_response = format_response(greek_response)
            print(formatted_greek_response)
            speak_in_greek(greek_response)
        else:
            print("Αδυναμία μετάφρασης της απάντησης. Ελέγξτε τη σύνδεσή σας και ξαναπροσπαθήστε.")
    else:
        print("Αδυναμία μετάφρασης της απάντησης. Ελέγξτε τη σύνδεσή σας και ξαναπροσπαθήστε.")
