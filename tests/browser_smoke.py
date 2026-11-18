"""Exercise the built starter at a project subpath in Chromium."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import tempfile
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    screenshots = ROOT / "browser-checks"
    screenshots.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        shutil.copytree(ROOT / "dist", Path(temporary) / "ferrycountss")
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=temporary))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": 1280, "height": 1000})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{server.server_port}/ferrycountss/")
                page.locator("#chart .hour").first.wait_for()
                page.locator("#route").select_option("FerryHW")
                page.locator("#weekday").select_option("work")
                assert "Halifax → Woodside" in page.locator("#finding").inner_text()
                page.locator("summary").click()
                assert page.locator("tbody tr").count() == 24
                with page.expect_download() as download:
                    page.locator("#download").click()
                assert download.value.suggested_filename == "halifax-ferry-counts.csv"
                page.screenshot(path=str(screenshots / "desktop.png"), full_page=True)
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.screenshot(path=str(screenshots / "mobile.png"), full_page=True)
                assert not errors, errors
                browser.close()
            print("Browser checks passed: project subpath, route filters, 24 hours, CSV and mobile layout")
        finally:
            server.shutdown()


if __name__ == "__main__":
    main()
