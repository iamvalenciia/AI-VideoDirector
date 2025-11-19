import requests
from pathlib import Path

def download_image(url: str, save_path: str):
    print(f"Downloading image from {url} to {save_path}...")
    # Convert save_path to a Path object
    save_path = Path(save_path)

    # Create directories if they don't exist
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Send HTTP GET request
    response = requests.get(url, stream=True)

    # Check if the download was successful
    if response.status_code == 200:
        # Write file in binary mode
        with save_path.open("wb") as f:
            f.write(response.content)
        print(f"Image downloaded successfully → {save_path}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}")
