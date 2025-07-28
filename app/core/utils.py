from urllib.parse import urlparse, parse_qs, unquote
from bs4 import BeautifulSoup
from .logger import logger
  
def extract_url_request(div):
    try:
        div_soup = BeautifulSoup(str(div), "lxml")
        url_anchor = div_soup.find('a')
        url = url_anchor.get('href', "") if url_anchor else ""
        return url if url else None
    except Exception as e:
        logger.error(f"Error get URL: {str(e)}")
        return None
    

def extract_info_playwright(div):
    try:
        div_soup = BeautifulSoup(str(div), "lxml")
        url_anchor = div_soup.find('a', class_='fuLhoc ZWRArf') or div_soup.find('a')
        
        if not url_anchor:
            logger.warning("No anchor tag found in the provided div.")
            return None, None, None, None

        url = url_anchor.get('href', "")
        title = url_anchor.get_text(strip=True)
        
        display_url_span = url_anchor.find('span', class_='fYyStc') or  url_anchor.find('div', class_='sCuL3')
        display_url = display_url_span.get_text(strip=True) if display_url_span else ""
        
        description_span = div_soup.find('span', class_='qXLe6d FrIlee') or div_soup.find('div', class_='BNeawe s3v9rd AP7Wnd')
        description = description_span.get_text(strip=True) if description_span else ""

        if url:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            decoded_url = unquote(query_params.get('url', [query_params.get('q', [''])[0]])[0])
            
            return decoded_url, title, display_url, description

        return None, title, display_url, description
    except Exception as e:
        logger.error(f"Error extracting info: {str(e)}")
        return None, None, None, None