from flask import Flask, request, jsonify
import cloudscraper, time, re, uuid, os
from threading import Lock

app = Flask(__name__)

class SpotMateAPI:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "android", "mobile": True}
        )
        self.base_url = "https://spotmate.online"
        self.lock = Lock()

    def init_session(self):
        r = self.scraper.get(f"{self.base_url}/en1", timeout=30)
        csrf = re.search(r'csrf-token"\s+content="([^"]+)"', r.text)
        return r.cookies.get_dict(), csrf.group(1) if csrf else None

    def process(self, spotify_url):
        cookies, csrf = self.init_session()
        if not csrf:
            return None

        headers = {"x-csrf-token": csrf}

        self.scraper.post(
            f"{self.base_url}/getTrackData",
            json={"spotify_url": spotify_url},
            headers=headers,
            cookies=cookies,
        )

        time.sleep(2)

        r = self.scraper.post(
            f"{self.base_url}/convert",
            json={"urls": spotify_url},
            headers=headers,
            cookies=cookies,
        )

        data = r.json()
        return data.get("download_url") or data.get("url")

spot = SpotMateAPI()

@app.route("/sp/dl")
def download():
    url = request.args.get("url")
    if not url:
        return jsonify({"success": False, "error": "No URL"})

    dl = spot.process(url)
    if not dl:
        return jsonify({"success": False, "error": "Failed"})

    return jsonify({
        "success": True,
        "download_url": dl
    })

@app.route("/")
def home():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
