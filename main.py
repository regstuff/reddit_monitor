import praw, requests, os
from datetime import datetime, timezone, timedelta
import json, gspread, base64
from google.oauth2.service_account import Credentials

def azure_call(data):
    azure_url = os.environ["AZURE_URL"]
    azure_key = os.environ["AZURE_KEY"]
    azure_headers = {"Content-Type": "application/json", "api-key": azure_key}
    response = requests.post(azure_url, headers=azure_headers, json=data)
    if response.status_code == 200:
        # tokens can be logged if needed
        pass
    else:
        print('Azure API Error:', response.status_code, response.text)
        return 'FAILED'
    return response.json()['choices'][0]['message']['content']

# Gsheet API
sheet = None
GSHEETS_API_KEY = """ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAibGVhcm5lZC10dWJlLTEyNzUxMiIsCiAgInByaXZhdGVfa2V5X2lkIjogIjkzMWE3MWZlZjRjZGQzMDY5ZDI2MWFkZmMzNTMyNDFhNGI5M2Y0YzYiLAogICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUV2UUlCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktjd2dnU2pBZ0VBQW9JQkFRRHEvN2EvU0I3QUVOSWNcbmVqVndkdGhHUHhiaTRIdFY3Y1NRWmRINEtZdGo3U25ScWQyMFZFcUhoUEh3WnpsdzRFN0lIRmdNRHA4TlMyQlRcbjg2WFNxT3dkcHVGUk04VUpUdGJxZW1oTmdpQ0hTL1A4RVRLL3VoMWVldTlHUm4xQ3U1RWJqNzVDRmJ2N2hWZVlcbnQvdHJxbDZjTlk1L3ZZTGRSanNaaHZ0WW1HSVhuOU5zRXkzMWkrTmFtUG1Ob3ZMWERuSHVMNkV3WnlJWGFWZlJcbkZVcThkOUluUTlSRndvK0F2SzBPTHBjYk5VZk9KK2R3a0ZWV3lYSWo4R2dwakhtaDNzNlpDVGJFdXV5VHFJR3hcbmFvRnhPbnZ2S014OE5xNXNLb3QxU05KaTZMdTlmeGp6ZVhXaUJodG9pY0lpUHg1T04zRWRVb1BsL0R3MEJMaGVcbkxFa0JDYmo1QWdNQkFBRUNnZ0VBV1JmYW9ubUd3djE5a3pOWCtFdnVZZStBVDBLWkwvSkZnQk5DUUNvTUFUWUVcbmtVc3IxVGJSek1BLzg0dEhFVDdSVDNmRGY4cTVUVktDOGtFZzRKV1Bjd3gyUnhGd0JiL2dwaVFEVUVOaDdybUNcbmhsSEU0a0IrNnZlRHFLcUh5ZG1Qd1puRklZdlk2WnBiby9nNHQxQnZyeHgwNm9RZ1RhRFhQaTNaTS9VTjEzTlVcbk92ZTZha2NONWsyYjZDeXp1OENwUVY1RFNNT21FTG4zU0tpRjRwWGk2SldLUGpHK1VxSTVpdDZ6VnRWYUZNdjdcbi9UQk9BMys0UnFFQkRRMFJkNDR5aVNJVmFTUnZsYStaUjR2T0VHZ0d0ZDJBYS9LNlJmbGRJelRqMDlFVzR1N3dcbllQZUlxYkJ1OC9PY05ST0YzT0pjRGRMVkZyQURKakZCbGZ5ZG1nV1lTd0tCZ1FEMWxZUXptc0NsM1cwMm1hU1JcbllLaTJZQVliRzVsM0NzU1VxK1dQV1pnODJoRjYyYjBsWmJnS3phV3c4eGUvMUNrREx2cnR4NVJ5N1RNcmNBeCtcbkhvbUk1OW9hNnQ5RWZaVmg0dVA5S004ZkFXZGhEL1hsRzFIaGZWTUVETXBMeUE0cysvd2dYMkJrZGxSMVVVZWFcbnp2STd1dVZxL3N4dm5UMlloQXZvU1BlOFl3S0JnUUQwOTBSQ2lMczNmOE1hbnVIb21iMFpYRzd1RzUxU1pYRWpcblAyWmltMmVTSk5iZVVQQnRNcUgzeTBBTzJBdjNDS3dIcEJXOWFJQWEyVWFDeC9SRklqcHlYbXFyNTF0YytXVElcbmVZeG1GUFFqT2ZkeWJLaVVSSE02S0NpWEptWnpMRksrMUVJcm5nNlBKVlBDa0xBRkc2VlVDNHVLQnd4cllYaEFcbkJZQktPeEd0OHdLQmdCU2c3NDdxSTk2SzMvNmpIMGk2NXRFUzlkQlhIQ2Y4dHBDS2MrajdyS2NINWtuOGVqL21cbjhIT3YzSWdsazB3Z3hTVW9VQm1qRnh3a1FwVVdmMllrcUliZ2V0aWgvQWtqeDJXR2lvSWNhSEdCUzY3Q2lYUXFcblBGR0ZsbkNUcG5hQkluZXkzdlhWTFNLak1lcjgzZGZxSkR6U01TMHdvL21JS3NGaDdpSWY1dmRqQW9HQVdMeHBcbllhQ2VFTkNiSUQyRm4vaHc0NHIwTkJTVXZKQTZsNFlUMUl4dXpDWEVIK3c1NjVSM3o0YzB3U3ZKeWNhK2FsWXBcbitkNnM2UXpqMmVRTXZDNVY5YS8xL0NkbWxSdFNRcnlrK3lXRCttNjVFQjRFUXhFNG5FeUh4NWtGYTVzV3JrRzlcblpvZHV4clBDejZ3UjF3ZllyOFV1MnVVS3Zxc2tJQ3pkK0FYRnRia0NnWUVBcTB6bURxZU9lMDErSENPejZ6WTRcbjRGN0I1eS81Ty9mdyttU0cwRjB4Y2s1SkZDNWZKeElzWmVYNVZBdkxHbHJVa000NGlHL3hzN3BYTzVaL3hZWkRcbmV3OHBJVURQeGNyeGVNS3E4UTFpdFk2aWpBbXdOWTFjYjBjQ0szWHFRWG9lZ3Q5TWxabUJWUXhOMVZnV1RUNUhcbkZvWEZHQko0Tk5QM0U2aEwydC84R2VRPVxuLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLVxuIiwKICAiY2xpZW50X2VtYWlsIjogInB1YmxpY2F0aW9ucy1nZG9jLWFjbEBsZWFybmVkLXR1YmUtMTI3NTEyLmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAiY2xpZW50X2lkIjogIjExNDEzOTc1NTYyODc2MTgwNzY1NiIsCiAgImF1dGhfdXJpIjogImh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRoMi9hdXRoIiwKICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwKICAiYXV0aF9wcm92aWRlcl94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92MS9jZXJ0cyIsCiAgImNsaWVudF94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3JvYm90L3YxL21ldGFkYXRhL3g1MDkvcHVibGljYXRpb25zLWdkb2MtYWNsJTQwbGVhcm5lZC10dWJlLTEyNzUxMi5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsCiAgInVuaXZlcnNlX2RvbWFpbiI6ICJnb29nbGVhcGlzLmNvbSIKfQo="""
SHEET_ID = "1cwbj5gl-zx0vL0xWHWb0xUPebclsdg0HQSXNb91OIzo" #os.environ.get("SHEET_ID")

if GSHEETS_API_KEY and SHEET_ID:
    if 1 == 1:
        creds_json = json.loads(base64.b64decode(GSHEETS_API_KEY).decode("utf-8"))
        
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(creds_json, scopes=scope)
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(SHEET_ID).sheet1
        print("Successfully connected to Google Sheets.")
    else:
        print(f"Could not connect to Google Sheets: {e}")
else:
    print("Google Sheets credentials not found. Skipping Google Sheets integration.")
    
# Reddit API credentials from your app settings
CLIENT_ID = os.environ["REDDIT_CLIENTID"]
CLIENT_SECRET = os.environ["REDDIT_CLIENTSECRET"]
USER_AGENT = "script:search_mcdonalds:v1.0 (by u/YOUR_USERNAME)"

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

search_query = os.environ["SEARCH_QUERY"]
org_query = os.environ["ORG_QUERY"]

title_check_prompt = f"""INSTRUCTION: I will give you a Reddit post. You must do sentiment analysis and determine if the post expresses a positive or negative sentiment about {search_query}, founder of {org_query}.
Your answer must be either: NA, Positive or Negative 
If the post is unrelated to {search_query}, founder of {org_query}, reply with: NA. 
If the post expresses a positive sentiment about {search_query}, founder of {org_query}, reply with: Positive
If the post expresses a negative sentiment about {search_query}, founder of {org_query}, reply with: Negative 
When in doubt about whether the post is related to {search_query}, founder of {org_query}, or whether the sentiment is positive or negative, reply with: Negative
Do not add anything else to your answer other than either: NA, Positive or Negative 
Reddit Post: """

exclude_subreddits = eval(os.environ["EXCLUDE_SUBREDDITS"])
# Search and filter recent posts
time_threshold = datetime.now(timezone.utc) - timedelta(hours=1)
reddit_search_query = f'"{search_query}" OR "{org_query}"'  # OR search

num_submissions = 0

for submission in reddit.subreddit("all").search(search_query, sort="new", time_filter="hour"):
    created_time = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
    if created_time > time_threshold and submission.subreddit.display_name.lower() not in exclude_subreddits:
        num_submissions += 1
        if submission.selftext.strip() != "":
            data = {
                    "messages": [{"role":"user","content": title_check_prompt + submission.title + '\n' + submission.selftext.strip()}],
                    "max_completion_tokens": 2,
                    "temperature": 1,
                    "frequency_penalty": 0,
                    "top_p": 0.95,
                    "stop": None
                }
            response = azure_call(data)
            print(f"[{created_time}] r/{submission.subreddit}: {submission.title}")
            print(submission.url, "\n")
            print(submission.selftext.strip())
            print('RESPONSE:', response)
            if response.lower().strip() in ['negative', 'positive]:
              created_time_str = created_time.strftime('%Y-%m-%d %H:%M:%S')
              row_to_insert = [submission.title, submission.selftext, submission.url, submission.subreddit.display_name, created_time_str]
              sheet.append_row(row_to_insert)
            print("="*10)  # visual separator
            


print(f"Total submissions: {num_submissions}")
