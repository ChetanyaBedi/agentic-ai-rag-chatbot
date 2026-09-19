from pathlib import Path
from urllib.request import Request, urlopen

PDF_URL = "https://konverge.ai/pdf/Ebook-Agentic-AI.pdf"
OUTPUT = Path("data/Ebook-Agentic-AI.pdf")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    req = Request(PDF_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=60) as response:
        data = response.read()

    OUTPUT.write_bytes(data)
    print(f"Downloaded {len(data):,} bytes to {OUTPUT}")


if __name__ == "__main__":
    main()
