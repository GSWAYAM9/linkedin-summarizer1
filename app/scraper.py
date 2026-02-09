import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

def extract_linkedin_text(url: str) -> str:
    """
    Extract text content from a LinkedIn post URL
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        logger.info(f"Scraping LinkedIn URL: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot fetch LinkedIn page. Status: {response.status_code}"
            )

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try multiple selectors for LinkedIn post content
        selectors = [
            ".feed-shared-update-v2__description-wrapper",
            ".feed-shared-inline-show-more-text",
            ".break-words",
            ".attributed-text-segment-list__content",
            ".update-components-text"
        ]
        
        text_content = ""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text_content = element.get_text(" ", strip=True)
                if text_content and len(text_content) > 10:
                    break
        
        if not text_content:
            # Fallback: try to get any meaningful text
            main_content = soup.find("main") or soup.find("article") or soup.find("div")
            if main_content:
                paragraphs = main_content.find_all("p")
                text_content = " ".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        if not text_content or len(text_content.strip()) < 10:
            raise HTTPException(
                status_code=400, 
                detail="Could not extract meaningful text from the LinkedIn post. The post might be private or require login."
            )
        
        logger.info(f"Successfully extracted {len(text_content)} characters")
        return text_content
        
    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail=f"Error fetching the LinkedIn page: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected scraping error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Error processing the LinkedIn post"
        )