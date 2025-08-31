import praw, requests, os
from datetime import datetime, timezone, timedelta

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


# Reddit API credentials from your app settings
CLIENT_ID = os.environ["REDDIT_CLIENTID"]
CLIENT_SECRET = os.environ["REDDIT_CLIENTSECRET"]
USER_AGENT = "script:search_mcdonalds:v1.0 (by u/YOUR_USERNAME)"

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

search_query = os.environ["search_query"]
org_query = os.environ["org_query"]
exclude_

title_check_prompt = f"""INSTRUCTION: I will give you a Reddit post. You must do sentiment analysis and determine if the post expresses a positive or negative sentiment about {search_query}, founder of {org_query}.
Your answer must be either: NA, Positive or Negative 
If the post is unrelated to {search_query}, founder of {org_query}, reply with: NA. 
If the post expresses a positive sentiment about {search_query}, founder of {org_query}, reply with: Positive
If the post expresses a negative sentiment about {search_query}, founder of {org_query}, reply with: Negative 
When in doubt about whether the post is related to {search_query}, founder of {org_query}, or whether the sentiment is positive or negative, reply with: Negative
Do not add anything else to your answer other than either: NA, Positive or Negative 
Reddit Post: """

exclude_subreddits = eval(os.environ["exclude_subreddits"])
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
            print("="*10)  # visual separator
            


print(f"Total submissions: {num_submissions}")
