"""
Description Cleaner Tool for standardizing transaction descriptions.
Removes common prefixes, normalizes merchant names, and standardizes formatting.
"""

import re
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Dictionary of common merchant name normalizations
MERCHANT_NORMALIZATIONS = {
    "AMZN": "Amazon",
    "AMAZONCOM": "Amazon",
    "AMAZON.COM": "Amazon",
    "AMZNMKTPLCE": "Amazon Marketplace",
    "WM": "Walmart",
    "WALMART": "Walmart",
    "WALM SUPERCENTER": "Walmart",
    "SQ": "Square",
    "SQ *": "Square",
    "STARBUCKS": "Starbucks",
    "SBUX": "Starbucks",
    "MCDONALD": "McDonald's",
    "MCD": "McDonald's",
    "COSTCO": "Costco",
    "COSTCO WHSE": "Costco",
    "COSTCO GAS": "Costco Gas",
    "UBER": "Uber",
    "UBER *": "Uber",
    "UBER EATS": "Uber Eats",
    "UBEREATS": "Uber Eats",
    "DOORDASH": "DoorDash",
    "GRUBHUB": "Grubhub",
    "INSTACART": "Instacart",
    "LYFT": "Lyft",
    "LYFT *": "Lyft",
    "VENMO": "Venmo",
    "PAYPAL": "PayPal",
    "PAYPAL *": "PayPal",
    "ZELLE": "Zelle",
    "CASH APP": "Cash App",
    "SQC*CASH APP": "Cash App",
    "TARGET": "Target",
    "TGT": "Target",
    "TGTCM": "Target",
    "KROGER": "Kroger",
    "TRADER JOE": "Trader Joe's",
    "WHOLEFDS": "Whole Foods",
    "WHOLE FOODS": "Whole Foods",
    "AMZN WHOLE FOODS": "Whole Foods",
    "NETFLIX": "Netflix",
    "NFLX": "Netflix",
    "SPOTIFY": "Spotify",
    "HULU": "Hulu",
    "DISNEY PLUS": "Disney+",
    "DISNEY+": "Disney+",
}

# Common bank statement prefixes/suffixes to remove
COMMON_PREFIX_SUFFIX = [
    "POS TRANSACTION", 
    "POS PURCHASE",
    "DEBIT CARD PURCHASE", 
    "ATM WITHDRAWAL", 
    "ONLINE PAYMENT", 
    "E-TRANSFER", 
    "AUTOPAY", 
    "ACH PAYMENT",
    "ACH DEPOSIT", 
    "DIRECT DEPOSIT", 
    "DIRECT DEBIT",
    "PURCHASE AUTHORIZED ON", 
    "RECURRING PAYMENT", 
    "CHECK CARD",
    "CHECK #", 
    "CKCD", 
    "CHECKCARD", 
    "PAYPAL DES:INST XFER", 
    "PAYPAL INST XFER",
    "PYMT ID:", 
    "REF #", 
    "REFERENCE #", 
    "TRANSACTION #",
    "AUTHORIZATION CODE",
]


def clean_description(description: str) -> str:
    """
    Clean and standardize a transaction description.
    
    Args:
        description: Raw transaction description
        
    Returns:
        Cleaned and standardized description
    """
    if not description:
        return ""
    
    # Convert to string if not already
    description = str(description).strip()
    
    # Remove common bank prefixes/suffixes
    for prefix in COMMON_PREFIX_SUFFIX:
        regex = re.compile(f"{prefix}\\s*", re.IGNORECASE)
        description = regex.sub("", description)
    
    # Remove transaction IDs, reference numbers, and dates at the end
    description = re.sub(r'\b\d{2}/\d{2}/\d{2,4}\b$', '', description)  # Date at end
    description = re.sub(r'\b\d{6,}\b$', '', description)  # ID number at end
    description = re.sub(r'#\d{4,}$', '', description)  # # followed by numbers
    
    # Remove extra whitespace (including multiple spaces, tabs, newlines)
    description = re.sub(r'\s+', ' ', description).strip()
    
    # Normalize merchant names
    for abbrev, full_name in MERCHANT_NORMALIZATIONS.items():
        if abbrev in description.upper():
            description = re.sub(
                r'\b' + re.escape(abbrev) + r'\b', 
                full_name, 
                description, 
                flags=re.IGNORECASE
            )
    
    # Convert to title case for consistency, but preserve common acronyms
    # Split, capitalize each word, then join
    words = description.split()
    capitalized_words = []
    for word in words:
        # Check if it's an acronym (all uppercase)
        if word.isupper() and len(word) > 1:
            capitalized_words.append(word)  # Keep acronyms as is
        else:
            capitalized_words.append(word.capitalize())
    
    description = ' '.join(capitalized_words)
    
    return description


def categorize_description(description: str) -> str:
    """
    Suggest a category based on the description.
    
    Args:
        description: Cleaned transaction description
        
    Returns:
        Suggested category
    """
    # Convert to lowercase for matching
    desc_lower = description.lower()
    
    # Category mapping based on keywords
    categories = [
        ("Groceries", ["grocery", "supermarket", "market", "food", "kroger", "walmart", "target", 
                    "trader joe", "whole foods", "safeway", "costco", "aldi"]),
        ("Dining", ["restaurant", "cafe", "coffee", "starbucks", "mcdonald", "burger", "pizza", 
                 "taco", "sushi", "doordash", "uber eats", "grubhub", "meal", "diner"]),
        ("Transportation", ["gas", "fuel", "uber", "lyft", "taxi", "transit", "parking", "tolls", 
                         "metro", "subway", "train", "bus", "airline", "flight"]),
        ("Utilities", ["electric", "water", "gas bill", "utility", "internet", "phone", "mobile", 
                     "wifi", "cable", "sewage"]),
        ("Housing", ["rent", "mortgage", "hoa", "home", "apartment", "insurance", "property"]),
        ("Entertainment", ["movie", "netflix", "hulu", "disney", "spotify", "theatre", "concert", 
                        "ticket", "game", "book", "kindle"]),
        ("Shopping", ["amazon", "ebay", "etsy", "clothing", "fashion", "apparel", "electronics", 
                   "department", "store"]),
        ("Health", ["doctor", "medical", "pharmacy", "prescription", "dental", "vision", "fitness", 
                 "gym", "healthcare"]),
        ("Education", ["tuition", "school", "college", "university", "course", "class", "book", 
                     "education"]),
        ("Personal", ["haircut", "salon", "spa", "beauty", "barber"]),
        ("Gifts/Donations", ["gift", "donation", "charity", "non-profit"]),
        ("Subscription", ["membership", "subscription", "monthly", "annual fee"]),
        ("Income", ["salary", "payroll", "deposit", "revenue", "interest", "dividend"]),
    ]
    
    # Check for category matches
    for category, keywords in categories:
        if any(keyword in desc_lower for keyword in keywords):
            return category
    
    # Default category if no match found
    return "Uncategorized"
