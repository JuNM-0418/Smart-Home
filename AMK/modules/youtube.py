from googleapiclient.discovery import build
import argparse
import pafy
import vlc
import time

DEVELOPER_KEY = 'AIzaSyDy_thKnnsXEaNi39Un4-4tTt6rcySDzag'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
# Define VLC player




class YoutubePlayer:
    def __init__(self):
        self.instance = vlc.Instance('--input-repeat=-1', '--fullscreen')
        self.player = None
    
    @staticmethod
    def search(options):
        try:
            youtube = build(YOUTUBE_API_SERVICE_NAME,
                            YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

            parser = argparse.ArgumentParser()
            parser.add_argument('--q', help='Search term', default=options)
            parser.add_argument('--max-results', help='Max results', default=25)
            args = parser.parse_args()

            search_response = youtube.search().list(
                q=args.q,
                part='id,snippet',
                maxResults=args.max_results
            ).execute()

            videos = []
            url = []

            for search_result in search_response.get('items', []):
                # print(search_result)
                if search_result['id']['kind'] == 'youtube#video' and not search_result['snippet']['liveBroadcastContent'] == "live":
                    videos.append('%s (%s)' % (
                        search_result['snippet']['title'], search_result['id']['videoId']))
                    url.append(search_result['id']['videoId'])
            resultURL = "https://www.youtube.com/watch?v=" + url[0]
            return resultURL

        except:
            print("Youtube Error")

    def set_with_url(self, play_url):
        if self.is_set():
            print("audio is already set")
            return
        self.player = self.instance.media_player_new()
        video = pafy.new(play_url)
        best = video.getbestaudio()
        url = best.url
        # Define VLC media
        media = self.instance.media_new(url)
        # Set player media
        self.player.set_media(media)
    
    def set_with_text(self, serach_text):
        url = self.search(serach_text)
        self.set_with_url(url)
        
    def is_set(self):
        return self.player is not None
        
    def play(self):
        if not self.is_set():
            print("player is not set")
            return
        # Play the media
        self.player.play()

    def pause(self):
        if not self.is_set():
            print("player is not set")
            return
        self.player.pause()

    def stop(self):
        if not self.is_set():
            print("player is not set")
            return
        self.player.stop()
        self.player = None

if __name__ == "__main__":
    youtube = YoutubePlayer()
    youtube.set_with_text("한국 가요")
    youtube.play()
    time.sleep(20)
    youtube.stop()

    youtube.set_with_text("재즈")
    youtube.play()
    time.sleep(20)
    youtube.stop()
