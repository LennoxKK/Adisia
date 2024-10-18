from googleapiclient.discovery import build
from decouple import config
import re

def extract_video_id(youtube_link):
    # Regular expression to match different YouTube video URL formats
    regex = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(regex, youtube_link)
    return match.group(1) if match else None


def youtuber_video_stats(video_id):
    youtube = build("youtube", "v3", developerKey=config("YOU_TUBE_API_KEY"))
    youtube_request = youtube.videos().list(part="statistics", id=video_id)
    response = youtube_request.execute()
    return response
import requests

def get_youtube_video_stats(video_url, api_key):
    # Extract the video ID from the URL
    video_id = video_url.split('v=')[-1].split('&')[0]
    
    # Define the API endpoint
    api_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={api_key}"
    
    # Make the API request
    response = requests.get(api_url)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        
        # Check if we have any items in the response
        if 'items' in data and len(data['items']) > 0:
            statistics = data['items'][0]['statistics']
            views = statistics.get('viewCount', 'N/A')
            likes = statistics.get('likeCount', 'N/A')
            return {'views': views, 'likes': likes}
        else:
            return {'error': 'No video found.'}  # No video found
    else:
        # Handle errors
        print(f"Error: {response.status_code}, Message: {response.text}")
        return {'error': f"Request failed with status {response.status_code}"}


