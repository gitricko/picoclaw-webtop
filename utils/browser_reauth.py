import sys
import os
import re
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

SERVICE_DIR = Path.home() / ".google-oauth-automation"
PROFILE_DIR = SERVICE_DIR / "chrome-profile"
LOGIN_FLAG = SERVICE_DIR / "logged-in"

# Check if DEBUG environment variable is set
IS_DEBUG = os.environ.get("DEBUG") is not None


async def auto_click(page):

    """Attempt to automatically click through the Google OAuth flow"""
    # 0. Check if password is being requested
    try:
        password_input = await page.query_selector("input[type='password']")
        if password_input and await password_input.is_visible():
            pwd_file = Path.home() / ".google-oauth-automation" / "password.txt"
            if pwd_file.exists():
                print("🔑 Google asked for a password. Injecting it from password.txt...")
                pwd = pwd_file.read_text().strip()
                await password_input.fill(pwd)
                
                # Press 'Next' to submit the password
                next_btn = await page.query_selector("button span:has-text('Next')")
                if next_btn:
                    await next_btn.click()
                else: 
                    await password_input.press("Enter")
                
                print("✅ Password submitted.")
                await asyncio.sleep(5)  # Wait for Google to process the password
                return True
            else:
                print("❌ ERROR: Google is asking for a password! Your session may have expired.")
                print("   To automate this, you can save your password in:")
                print(f"   {pwd_file}")
                return False
    except Exception:
        pass
        
    # 1. Click account if chooser is present
    try:
        # Give it a moment to load
        await page.wait_for_selector("div[data-identifier], div[data-authuser='0']", timeout=3000)
        elements = await page.query_selector_all("div[data-identifier], div[data-authuser='0']")
        for el in elements:
            if await el.is_visible():
                await el.click()
                print("✅ Auto-selected account.")
                break
    except Exception:
        pass

    # 2. Click Continue/Allow on consent screen
    try:
        # Google's continue buttons often use span inside a button
        await page.wait_for_selector("button span:has-text('Sign In'), button span:has-text('Allow'), button span:has-text('Continue')", timeout=3000)
        elements = await page.query_selector_all("button:has-text('Sign In'), button:has-text('Allow'), button:has-text('Continue')")
        for el in elements:
            if await el.is_visible():
                await el.click()
                print("✅ Auto-clicked Continue/Allow.")
                break
    except Exception:
        pass

    return True

async def main():
    SERVICE_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    
    first_time = not LOGIN_FLAG.exists()
    is_headless = False if (first_time or IS_DEBUG) else True
    
    print(f"🚀 Starting automation (First time: {first_time} | Debug: {IS_DEBUG})")

    async with Stealth().use_async(async_playwright()) as p:
        # Construct arguments based on headlessness
        headless_args = []
        if is_headless:
            headless_args.append("--headless=new")

        context_args = {
            "user_data_dir": str(PROFILE_DIR),
            "headless": False if (not is_headless) else True,
            "channel": "chrome",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-extensions",
                "--disable-infobars",
                *headless_args
            ],
            "viewport": {"width": 1280, "height": 900},
        }

        if os.path.exists("/usr/bin/chromium"):
            context_args["executable_path"] = "/usr/bin/chromium"

        context = await p.chromium.launch_persistent_context(**context_args)
        
        page = await context.new_page()

        try:
            print("🌐 Navigating to credentials page...")
            await page.goto("http://localhost:18800/credentials")
            
            if first_time:
                print("\n📌 FIRST TIME SETUP:")
                print("   1. Please log into the web UI if necessary.")
                print("   2. Click the 'Browser OAuth' button under 'Google Antigravity'.")
                print("   3. Complete the Google login manually in the popup.")
                print("   Waiting for a popup to open and close...\n")
                
                popup_closed = False
                success = False

                def update_closed(p):
                    nonlocal popup_closed
                    print("🪟 Popup closed!")
                    popup_closed = True

                def handle_popup(new_page):
                    print(f"🪟 Popup opened: {new_page.url}")
                    new_page.on("close", update_closed)

                context.on("page", handle_popup)
                
                for _ in range(600): # 10 minutes timeout
                    if popup_closed:
                        LOGIN_FLAG.write_text("ok")
                        print("✅ Login completed and saved! You will not have to do this again.")
                        success = True
                        break
                    
                    await asyncio.sleep(1)
                
                if not success:
                    print("❌ Timeout waiting for auth completion.")
            else:
                print("🤖 Running headless automation...")
                
                # Find the card or section for "Google Antigravity"
                # It has a "Browser OAuth" button.
                # Use a locator to find the section and then the button to be extremely precise
                # We also grab the last button in case there are multiple matching
                card_loc = page.locator("div").filter(has_text="Google Antigravity")
                button_loc = card_loc.locator("button:has-text('Browser OAuth')").last
                
                # Wait for button to be visible
                await button_loc.wait_for(timeout=10000)
                
                # Attempt to extract the email to use as a login_hint. 
                # This drastically lowers the chance of Google asking for a password in Web Flows!
                email_address = ""
                try:
                    email_text = await card_loc.get_by_text("Email:").inner_text(timeout=2000)
                    if "Email:" in email_text:
                        email_address = email_text.split("Email:")[1].strip()
                except Exception:
                    pass
                
                # Intercept network requests to catch the Google URL BEFORE it hits their servers
                # This prevents Google from detecting the popup context
                target_url = None
                
                async def intercept_google(route):
                    nonlocal target_url
                    url = route.request.url
                    if "accounts.google.com" in url and target_url is None:
                        target_url = url
                        await route.abort()
                    else:
                        await route.fallback()
                        
                # Use fallback to safely ignore things we don't handle
                await context.route("**/*", intercept_google)
                
                # Click the button and wait for the popup
                print("👆 Clicking 'Browser OAuth' button...")
                async with page.expect_popup() as popup_info:
                    await button_loc.click()
                
                popup = await popup_info.value
                
                # Wait for the intercepted request
                for _ in range(20):
                    if target_url:
                        break
                    await asyncio.sleep(0.5)
                
                # Clean up interception and close the flagged popup
                await context.unroute("**/*", intercept_google)
                await popup.close()
                
                if not target_url:
                     print("❌ Failed to capture Google OAuth URL.")
                     success = False
                     
                # Inject the login hint if we successfully parsed the email from the UI
                if email_address and "login_hint=" not in target_url:
                     target_url += f"&login_hint={email_address}"
                     
                print(f"🔒 Captured URL stealthily. Launching clean page for: {target_url[:50]}...")
                
                clean_page = await context.new_page()
                
                success = False
                async def on_framenavigated(frame):
                    nonlocal success
                    url = frame.url
                    if url.startswith("http://localhost") or url.startswith("http://127.0.0.1"):
                        success = True

                clean_page.on("framenavigated", on_framenavigated)

                try:
                    await clean_page.goto(target_url, referer="http://localhost:18800/credentials")
                except Exception as e:
                    if "localhost" in str(e) or "127.0.0.1" in str(e) or "ERR_CONNECTION_REFUSED" in str(e):
                        success = True

                # loop until done
                for _ in range(60): # 60 seconds max
                    if success:
                        print("✅ Headless auth completed! (Redirect successful)")
                        break
                    
                    try:
                        if clean_page.url.startswith("http://localhost") or clean_page.url.startswith("http://127.0.0.1"):
                            print("✅ Headless auth completed! (URL check)")
                            success = True
                            break
                    except:
                        pass
                        
                    # attempt auto clicking on the clean_page
                    print("   Checking for account chooser or consent screen...")
                    progress = await auto_click(clean_page)
                    if not progress:
                        print("🛑 Aborting headless flow due to password or security prompt.")
                        success = False
                        break
                        
                    await asyncio.sleep(1)
                    
                if not success:
                     print("⚠️ Timeout: Failed to reach completion automatically.")
                     
                try:
                    await clean_page.close()
                except:
                    pass
             
        except Exception as e:
             print(f"❌ Error during automation: {e}")

        # Cleanup
        try:
            if not page.is_closed():
                await page.close()
            await context.close()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
