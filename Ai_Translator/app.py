from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import json
import time

app = Flask(__name__)

# Function to translate text using LibreTranslate API
def translate_text(text, target_lang='es'):
    if not text or text.isspace():
        return text
        
    try:
        # Use a more reliable translation API
        # You can replace this with your preferred translation service
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": target_lang,
            "dt": "t",
            "q": text
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            result = response.json()
            translated_text = ''.join([sentence[0] for sentence in result[0]])
            return translated_text
        return text  # Return original if translation fails
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original if translation fails

@app.route('/', methods=['GET', 'POST'])
def index():
    translated_html = ""
    original_html = ""
    error_message = ""
    
    if request.method == 'POST':
        try:
            original_html = request.form.get('html_input', '')
            
            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(original_html, 'html.parser')
            
            # Find all text nodes and translate them
            for element in soup.find_all(text=True):
                # Skip script and style elements
                if element.parent.name in ['script', 'style']:
                    continue
                    
                # Skip empty strings and whitespace-only strings
                if not element.strip():
                    continue
                
                # Get text content
                text_content = str(element)
                
                # Translate with error handling and rate limiting
                translated_text = translate_text(text_content)
                
                # Replace the original text with the translated text
                element.replace_with(translated_text)
                
                # Add a small delay to avoid hitting rate limits
                time.sleep(0.1)
            
            # Get the modified HTML
            translated_html = str(soup)
            
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)
    
    return render_template('index.html', 
                          translated_html=translated_html,
                          original_html=original_html,
                          error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)