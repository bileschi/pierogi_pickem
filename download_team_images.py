import requests
from pathlib import Path

def download_image(team_code, image_url):
    """Downloads an image from the given URL and saves it with the team code as the filename."""
    response = requests.get(image_url)
    response.raise_for_status()  # Raise an exception for error HTTP statuses

    image_path = Path(f"images/nfl/{team_code}.png")
    with open(image_path, 'wb') as f:
        f.write(response.content)

def main():
    """Downloads images for all 32 NFL teams."""
    teams = [
        "ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", "DAL", "DEN",
        "DET", "GB", "HOU", "IND", "JAX", "KC", "LAC", "LAR", "LV", "MIA",
        "MIN", "NE", "NO", "NYG", "NYJ", "PHI", "PIT", "SEA", "SF", "TB", "TEN", "WSH"
    ]

    image_base_url = "https://a.espncdn.com/i/teamlogos/nfl/500-dark/"

    for team in teams:
        image_url = image_base_url + f"{team}.png"
        try:
            download_image(team, image_url)
            print(f"Downloaded image for {team}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image for {team}: {e}")

if __name__ == "__main__":
    main()