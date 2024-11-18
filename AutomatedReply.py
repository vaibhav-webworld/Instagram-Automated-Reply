import requests
import google.generativeai as genai
import json
import os
import schedule
import time

access_token = "" # Upload the access token here of the instagram graph api.
instagram_user_id = "" # Write the instagram user ID code here.
prompt = (" ") # Write the pre prompt on the basis you want the gemini to generate the responses.

replied_comments_file = 'replied_comments.json'

def load_replied_comments():
    if os.path.exists(replied_comments_file):
        with open(replied_comments_file, 'r') as file:
            return set(json.load(file))
    return set()

def save_replied_comments(replied_comments):
    with open(replied_comments_file, 'w') as file:
        json.dump(list(replied_comments), file)
 
def get_gemini_response(comment, user_name):
    try:
        genai.configure(api_key=" ") #API key for gemini 
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Attempt to generate content using the model
        response = model.generate_content(f"{prompt} {comment}")
        
        # Handle successful response
        mentioned_response = f"{response.text}"
        return mentioned_response
    
    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error generating response for comment '{comment}' by user '{user_name}': {e}")
        
        # Return None or a fallback message if needed
        return None

def reply_to_comment(comment_id, reply_message, access_token):
    url = f"https://graph.facebook.com/v17.0/{comment_id}/replies"
    payload = {
        'message': reply_message,
        'access_token': access_token
    }
    
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        print('Reply posted successfully:', response.json())
    else:
        print('Failed to post reply:', response.json())


# Step 2: Get comments on the reel and reply using Gemini API
def get_comments_and_reply(media_id, access_token):
    if media_id is None:
        print("No media ID found, cannot fetch comments.")
        return
    
    url = f"https://graph.facebook.com/{media_id}/comments"
    params = {
        "fields": "id,text,username",
        "access_token": access_token
    }
    
    replied_comments = load_replied_comments()
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data:
            for comment in data['data']:
                comment_id = comment['id']
                
                if comment_id in replied_comments:
                    continue
                
                if 'text' not in comment:
                    print(f"Skipping comment {comment_id} as it doesn't contain text (likely a GIF or sticker).")
                    replied_comments.add(comment_id)
                    save_replied_comments(replied_comments)
                    continue

                comment_text = comment['text']
                user_name = comment['username']
                
                # Generate a response using Gemini API
                reply = get_gemini_response(comment_text, user_name)
                
                # Post the reply to the comment
                reply_to_comment(comment_id, reply, access_token)
                
                # Track the replied comment
                replied_comments.add(comment_id)
                
            # Save the updated list of replied comments
            save_replied_comments(replied_comments)
                
        else:
            print("No comments found or incorrect data format")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except ValueError as e:
        print(f"Failed to parse JSON: {e}")

media_id = # ID of reel you want to make the automated reply. 
get_comments_and_reply(media_id, access_token)

def job():
    media_id = # ID of reel you want to make the automated reply. 
    get_comments_and_reply(media_id, access_token)

# Schedule the job every 20 minutes
schedule.every(6).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
