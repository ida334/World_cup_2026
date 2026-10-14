"""Keep the World Cup 2026 Streamlit app awake.

Streamlit Community Cloud puts free apps to sleep after a period without visits.
A plain HTTP request is not enough to wake one: a sleeping app shows a page with a
"Yes, get this app back up!" button that has to be clicked in a real browser.

This script opens the app in headless Chromium, clicks that button if it is there,
and then stays on the page long enough for the app to finish loading, so the visit
counts as real activity. GitHub Actions runs it on a schedule (see
.github/workflows/keep-awake.yml).
"""

import sys

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

APP_URL = "https://ida334-worldcup2026.streamlit.app/"
WAKE_BUTTON_TEXT = "get this app back up"  # matched case-insensitively, as a substring
PAGE_LOAD_TIMEOUT_MS = 90_000
WAKE_TIMEOUT_MS = 180_000
STAY_ON_PAGE_MS = 45_000


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        print(f"Opening {APP_URL}")
        page.goto(APP_URL, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT_MS)
        page.wait_for_timeout(8_000)  # give the sleep page time to render its button

        wake_button = page.get_by_role("button", name=WAKE_BUTTON_TEXT)
        if wake_button.count() > 0:
            print("App was asleep. Clicking the wake-up button.")
            wake_button.first.click()
            try:
                wake_button.first.wait_for(state="detached", timeout=WAKE_TIMEOUT_MS)
                print("Wake-up button is gone; the app is starting.")
            except PlaywrightTimeout:
                print("The wake-up button did not disappear in time.", file=sys.stderr)
                browser.close()
                return 1
        else:
            print("App is already awake.")

        page.wait_for_timeout(STAY_ON_PAGE_MS)
        print(f"Done. Final page title: {page.title()!r}")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
