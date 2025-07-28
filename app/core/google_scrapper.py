import os
import pandas as pd
import concurrent.futures
from bs4 import BeautifulSoup

from playwright.async_api import async_playwright
try:
    from playwright_stealth import stealth_async
except ImportError:
    # Fallback if stealth_async is not available
    async def stealth_async(page):
        # Basic stealth measures
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
import requests

from .logger import logger
from .agent import get_random_user_agent
from .utils import extract_info_playwright

# Hàm chặn các tài nguyên không cần thiết
async def block_unnecessary_resources(page):
    async def route_intercept(route, request):
        if request.resource_type in ["image", "stylesheet", "font"]:
            await route.abort()
        else:
            await route.continue_()
    await page.route("**/*", route_intercept)

async def fetch_page_headless(keyword, device, numPages, proxy, language, location):
    google_url = f'https://www.google.com/search?num={int(numPages)*10}&q={keyword}&hl={language}&gl={location}'
    agent = get_random_user_agent(device)
    
    proxy_config = None
    if proxy:
        proxy_config = {"server": f"http://{proxy}"}
        logger.info(f"Fetching page using proxy: {proxy}")
    else:
        logger.info("Fetching page without proxy")

    logger.info(f"Google URL: {google_url}")
    logger.info(f"User Agent: {agent}")

    try:
        async with async_playwright() as p:
            browser_type = p.firefox
            # Khởi chạy browser ở chế độ headless
            browser = await browser_type.launch(proxy=proxy_config, headless=True)
            context = await browser.new_context(user_agent=agent)
            page_obj = await context.new_page()
            # Chặn các tài nguyên không cần thiết
            await block_unnecessary_resources(page_obj)
            await stealth_async(page_obj)
            
            # Thiết lập timeout cho việc tải trang (15 giây)
            logger.info("Navigating to Google...")
            await page_obj.goto(google_url, timeout=15000)
            
            # Wait for search results to load
            try:
                await page_obj.wait_for_selector('div[data-async-context]', timeout=5000)
                logger.info("Search results container found")
            except:
                logger.warning("Search results container not found, proceeding anyway")
            
            content = await page_obj.content()
            logger.info(f"Page content length: {len(content)} characters")
            
            # Log a snippet of the content for debugging
            if content:
                snippet = content[:500] + "..." if len(content) > 500 else content
                logger.info(f"Content snippet: {snippet}")
            
            await browser.close()
            return content
    except Exception as e:
        logger.error(f"Playwright error: {type(e).__name__}: {str(e)}")
        return None
        
async def fetch_page_request(keyword, device, numPages, proxy, language, location):
    google_url = f'https://www.google.com/search?num={int(numPages) * 10}&q={keyword}&hl={language}&gl={location}'
    user_agent = get_random_user_agent(device)

    proxies = None
    if proxy:
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }

    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    logger.info(f"Google URL: {google_url}")
    logger.info(f"Using proxy: {proxy}" if proxy else "No proxy")
    logger.info(f"User Agent: {user_agent}")

    try:
        response = requests.get(google_url, proxies=proxies, headers=headers, timeout=15)
        logger.info(f"Request status code: {response.status_code}")
        logger.info(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            content_length = len(response.text)
            logger.info(f"Request successful, content length: {content_length}")
            
            # Log a snippet for debugging
            snippet = response.text[:500] + "..." if len(response.text) > 500 else response.text
            logger.info(f"Content snippet: {snippet}")
            
            return response.text
        else:
            logger.error(f"Request failed with status code: {response.status_code}")
            logger.error(f"Response content: {response.text[:1000]}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {type(e).__name__}: {str(e)}")
        return None

async def google_search(query, device="desktop", language="vi", location="VN", num_pages=1, user_proxy=None, max_workers=5):
    """
    Simplified Google search function
    Args:
        query: Search keyword
        device: desktop or mobile
        language: Language code (default: vi)
        location: Location code (default: VN)
        num_pages: Number of pages to fetch (default: 1)
        user_proxy: Optional user-provided proxy
        max_workers: Max workers for parallel processing
    """
    logger.info(f"Starting Google search for: '{query}' | Device: {device} | Language: {language} | Location: {location} | Pages: {num_pages}")
    
    content = None
    proxy = user_proxy
    
    # Try requests first (faster), fallback to headless browser
    try:
        if proxy and "@" in proxy:
            logger.info("Using requests with authenticated proxy")
            content = await fetch_page_request(keyword=query, device=device, numPages=num_pages, 
                                             proxy=proxy, language=language, location=location)
        else:
            logger.info("Using headless browser")
            content = await fetch_page_headless(keyword=query, device=device, numPages=num_pages, 
                                              proxy=proxy, language=language, location=location)
    except Exception as e:
        logger.error(f"Error in fetch method: {type(e).__name__}: {str(e)}")
        content = None
    
    if not content:
        logger.error("Failed to fetch content from Google")
        return None

    # Check for common blocking indicators
    content_lower = content.lower()
    blocking_indicators = [
        "our systems have detected unusual traffic",
        "unusual traffic from your computer network",
        "captcha",
        "robot",
        "automated queries",
        "please enable javascript",
        "blocked",
        "access denied"
    ]
    
    for indicator in blocking_indicators:
        if indicator in content_lower:
            logger.warning(f"Detected blocking indicator: '{indicator}'")
            logger.warning("Google may be blocking our requests")

    # Xử lý nội dung HTML bằng BeautifulSoup
    try:
        soup = BeautifulSoup(content, "lxml")
        
        # Try multiple selectors for search results
        selectors_to_try = [
            'div.ezO2md',  # Desktop
            'div.Gx5Zad.xpd.EtOod.pkphOe',  # Mobile
            'div[data-async-context]',  # Alternative
            'div.g',  # Classic Google results
            'div.MjjYud',  # New format
        ]
        
        urls = []
        for selector in selectors_to_try:
            try:
                urls = soup.select(selector)
                if urls:
                    logger.info(f"Found {len(urls)} results using selector: {selector}")
                    break
                else:
                    logger.info(f"No results found with selector: {selector}")
            except Exception as e:
                logger.error(f"Error with selector {selector}: {e}")
                continue

        if not urls:
            logger.warning("No search results found with any selector")
            # Log some HTML structure for debugging
            all_divs = soup.find_all('div', limit=10)
            logger.info(f"Found {len(all_divs)} div elements in total")
            for i, div in enumerate(all_divs[:5]):
                logger.info(f"Div {i}: class={div.get('class', 'no-class')}, id={div.get('id', 'no-id')}")
            return None
            
        results = []

        # Chạy song song phần trích xuất URL với ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_div = {executor.submit(extract_info_playwright, div): div for div in urls}
            for future in concurrent.futures.as_completed(future_to_div):
                try:
                    url, title, display_url, description = future.result()
                    if url:
                        results.append({
                            "url": url,
                            "title": title,
                            "display_url": display_url,
                            "description": description
                        })
                except Exception as e:
                    logger.error(f"Error extracting info: {str(e)}")
                    
        logger.info(f"Successfully extracted {len(results)} search results")
        return results
        
    except Exception as e:
        logger.error(f"Error processing content: {type(e).__name__}: {str(e)}")
        return None



            
