import re
import json
from collections import Counter
import quopri

with open('matt_levine_emails.mbox', 'r') as f:
    content = f.read()

emails = content.split('\n\nFrom ')
emails = ['From ' + e if not e.startswith('From ') else e for e in emails]
emails = [e for e in emails if 'From: "Matt Levine"' in e]

parsed_emails = []

for email in emails:
    try:
        subject_match = re.search(r'^Subject: (.+)$', email, re.MULTILINE)
        date_match = re.search(r'^Date: (.+)$', email, re.MULTILINE)
        
        subject = subject_match.group(1) if subject_match else ''
        date = date_match.group(1) if date_match else ''
        
        body_start = email.find('\n\n')
        body = email[body_start+2:] if body_start != -1 else ''
        
        try:
            body = quopri.decodestring(body.encode()).decode('utf-8', errors='ignore')
        except:
            pass
        
        body = body.replace('=\n', '').replace('=\r\n', '')
        
        # Find actual content end - truncate at Bloomberg footer
        footer_idx = body.find('Bloomberg L.P.')
        if footer_idx > 0:
            body = body[:footer_idx]
        
        # Also truncate at common metadata markers
        for marker in ['Update your email preferences', 'This email was sent to']:
            idx = body.find(marker)
            if idx > 0 and (footer_idx < 0 or idx < footer_idx):
                body = body[:idx]
        
        word_count = len(body.split())
        
        # Count footnotes only at start of line
        lines = body.split('\n')
        footones = sum(1 for line in lines if re.match(r'^\[\d+\]', line.strip()))
        
        links = len(re.findall(r'https?://[^\s\]>]+', body))
        saylor_mentions = len(re.findall(r'Michael Saylor|Saylor', body, re.IGNORECASE))
        ackman_mentions = len(re.findall(r'Bill Ackman', body, re.IGNORECASE))
        
        year_match = re.search(r'\b(20\d{2})\b', date)
        year = year_match.group(1) if year_match else 'Unknown'
        
        month_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b', date)
        year_month = f'{month_match.group(2)}-{month_match.group(1)}' if month_match else 'Unknown'
        
        parsed_emails.append({
            'subject': subject,
            'date': date,
            'year': year,
            'year_month': year_month,
            'word_count': word_count,
            'footones': footones,
            'links': links,
            'saylor_mentions': saylor_mentions,
            'ackman_mentions': ackman_mentions,
            'body': body
        })
    except Exception as e:
        print(f"Error: {e}")
        continue

print(f"Parsed {len(parsed_emails)} emails")

# Filter to only 2025
emails_2025 = [e for e in parsed_emails if e['year'] == '2025']
print(f"2025 emails: {len(emails_2025)}")

total_emails = len(emails_2025)
total_saylor = sum(e['saylor_mentions'] for e in emails_2025)
total_ackman = sum(e['ackman_mentions'] for e in emails_2025)
total_footones = sum(e['footones'] for e in emails_2025)
avg_words = sum(e['word_count'] for e in emails_2025) / total_emails if total_emails > 0 else 0
avg_footones = total_footones / total_emails if total_emails > 0 else 0

all_text = ' '.join(e['body'] for e in emails_2025)

stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 
              'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 
              'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'to', 'of',
              'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
              'during', 'before', 'after', 'above', 'below', 'between', 'under',
              'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
              'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some',
              'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
              'very', 'just', 'and', 'but', 'if', 'or', 'because', 'until', 'while',
              'about', 'against', 'this', 'that', 'these', 'those', 'what', 'which',
              'who', 'whom', 'its', 'it', 'i', 'you', 'he', 'she', 'we', 'they',
              'their', 'his', 'her', 'my', 'your', 'me', 'him', 'them', 'us', 'our',
              'one', 'two', 'like', 'get', 'got', 'go', 'went', 'come', 'came',
              'make', 'made', 'take', 'took', 'see', 'saw', 'know', 'knew', 'think',
              'thought', 'want', 'use', 'thing', 'things', 'say', 'said', 'new', 'old',
              'way', 'well', 'also', 'back', 'still', 'even', 'now', 'much', 'many',
              'over', 'very', 'first', 'last', 'long', 'great', 'good', 'right',
              'look', 'really', 'time', 'year', 'years', 'people', 'money', 'companies',
              'company', 'market', 'week', 'deal', 'deals', 'work', 'lot', 'don', 't',
              'don\'t', 'doesn\'t', 'didn\'t', 'isn\'t', 'aren\'t', 'wasn\'t', 'weren\'t',
              'haven\'t', 'hasn\'t', 'hadn\'t', 'won\'t', 'wouldn\'t', 'couldn\'t',
              'shouldn\'t', 'can\'t', 'pm', 'am', 're', 've', 'll', 'd', 's',
              'http', 'https', 'www', 'com', 'bloom', 'bloomberg', 'email', 'mailto',
              'html', 'body', 'head', 'title', 'link', 'style', 'class', 'href',
              'src', 'alt', 'width', 'height', 'border', 'valign', 'align', 'cellpadding',
              'cellspacing', 'colspan', 'rowspan', 'background', 'color', 'font'}

words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
words = [w for w in words if w not in stop_words]
word_counts = Counter(words)

exclude_companies = {'Crypto', 'Bitcoin', 'SEC', 'X', 'IPO', 'SPAC', 'Fed', 'Target'}

company_patterns = [
    # Prediction Markets (user requested)
    'Kalshi', 'Polymarket', 'PredictIt', 'Betmgm', 'Draftkings', 'Fanduel', 'BlackOwl',
    
    # Crypto
    'Tether', 'Circle', 'Coinbase', 'Binance', 'Kraken', 'Ripple', 'Ethereum', 'Solana', 'Bitcoin',
    'MicroStrategy', 'Strategy', 'FTX', 'BlockFi', 'Celsius', 'Genesis', 'Bittrex',
    
    # AI/Tech
    'OpenAI', 'ChatGPT', 'DeepSeek', 'Anthropic', 'Claude', 'Mistral', 'Google', 'Microsoft',
    'Apple', 'Amazon', 'Meta', 'Facebook', 'Nvidia', 'AMD', 'Intel', 'Oracle', 'Salesforce',
    'Palantir', 'Snowflake', 'Databricks', 'Uber', 'Lyft', 'Airbnb', 'DoorDash', 'Stripe', 'Square', 'Block',
    
    # Auto/Tesla
    'Tesla', 'SpaceX', 'Rivian', 'Lucid', 'Ford', 'GM', 'General Motors', 'Toyota', 'Volkswagen',
    
    # Banks
    'Goldman', 'Goldman Sachs', 'JPMorgan', 'JPM', 'Morgan Stanley', 'Bank of America', 'BoA',
    'Citigroup', 'Citi', 'Wells Fargo', 'Wells', 'Deutsche Bank', 'UBS', 'Credit Suisse',
    'JP Morgan', 'Morgan',
    
    # Asset Managers
    'BlackRock', 'Vanguard', 'Fidelity', 'State Street', 'Berkshire', 'Hathaway',
    'Apollo', 'KKR', 'Blackstone', 'Carlyle', 'Silver Lake', 'TPG',
    
    # Hedge Funds
    'Citadel', 'Point72', 'Pershing Square', 'Bridgewater', 'Millennium', 'Two Sigma',
    'D.E. Shaw', 'Balyon', 'Schonfeld', 'Brevan Howard', 'Marshall Wace',
    
    # Fintech
    'Robinhood', 'Revolut', 'Wise', 'PayPal', 'Visa', 'Mastercard', 'American Express', 'Amex',
    
    # Companies
    'Netflix', 'Twitter', 'X', 'Disney', 'ESPN', 'Warner', 'Comcast', 'Paramount',
    'MGM', 'Sony', 'Nintendo', 'Microsoft', 'Salesforce', 'Slack', 'Zoom',
    'Snowflake', 'ServiceNow', 'Workday', 'Intuit', 'Adobe', 'Oracle',
    
    # Airlines/Retail
    'McDonald', 'Starbucks', 'Walmart', 'Target', 'Costco', 'Home Depot', 'Lowe',
    'Delta', 'American Airlines', 'United', 'Southwest', 'JetBlue',
    
    # Defense/Industrials
    'Boeing', 'Lockheed', 'Raytheon', 'Northrop', 'General Dynamics', 'L3Harris',
    
    # Other
    'SoftBank', 'Ark', 'Cathie Wood', 'Hertz', 'WeWork', 'Peloton', 'Beyond Meat',
    'Oatly', 'Carvana', 'Avis', 'Hertz', 'SVB', 'Silicon Valley Bank', 'First Republic',
    'Signature Bank', 'Federal Reserve', 'Fed',
    
    # Tickers (as they appear in text)
    'TSLA', 'NVDA', 'AAPL', 'MSFT', 'GOOG', 'GOOGL', 'AMZN', 'META', 'NFLX',
    'BTC', 'ETH',
    
    # Recent hot topics
    'Perplexity', 'Character AI', 'Adept', 'Inflection', 'Runway', 'Midjourney',
]

company_counts = {}
for company in company_patterns:
    count = len(re.findall(r'\b' + re.escape(company) + r'\b', all_text, re.IGNORECASE))
    if count > 0:
        company_counts[company] = count

# Merge company aliases
merge_map = {
    'Strategy': 'MicroStrategy',
    'Goldman Sachs': 'Goldman',
    'JPM': 'JPMorgan',
    'JP Morgan': 'JPMorgan',
    'BoA': 'Bank of America',
    'Citi': 'Citigroup',
    'Wells': 'Wells Fargo',
    'Morgan': 'Morgan Stanley',
    'META': 'Meta',
    'Hathaway': 'Berkshire',
    'X': 'Twitter',
    'GM': 'General Motors',
    'Federal Reserve': 'Fed',
}

# Apply merges
merged_counts = {}
for company, count in company_counts.items():
    mapped = merge_map.get(company, company)
    merged_counts[mapped] = merged_counts.get(mapped, 0) + count

# Remove excluded companies
merged_counts = {k: v for k, v in merged_counts.items() if k not in exclude_companies}
company_counts = merged_counts

# Crypto tracking
crypto_patterns = {
    'Bitcoin': ['Bitcoin', 'BTC'],
    'Ethereum': ['Ethereum', 'ETH', 'Vitalik'],
    'Solana': ['Solana', 'SOL', 'Anatoly'],
    'Tether': ['Tether', 'USDT'],
    'USDC': ['USDC', 'Circle'],
    'Ripple': ['Ripple', 'XRP', 'Brad'],
    'BNB': ['BNB', 'Binance Coin'],
    'Dogecoin': ['Dogecoin', 'DOGE',],
    'Shiba Inu': ['Shiba Inu', 'SHIB'],
    'Cardano': ['Cardano', 'ADA', 'Hoskinson'],
    'Polkadot': ['Polkadot', 'DOT', 'Gavin'],
    'Avalanche': ['Avalanche', 'AVAX', 'Ava Labs'],
    'Chainlink': ['Chainlink']
}

crypto_counts = {}
for crypto_name, patterns in crypto_patterns.items():
    total = 0
    for pattern in patterns:
        total += len(re.findall(r'\b' + re.escape(pattern) + r'\b', all_text, re.IGNORECASE))
    if total > 0:
        crypto_counts[crypto_name] = total

monthly_word_totals = {}
monthly_email_counts = {}

for e in emails_2025:
    ym = e['year_month']
    if ym not in monthly_word_totals:
        monthly_word_totals[ym] = 0
        monthly_email_counts[ym] = 0
    monthly_word_totals[ym] += e['word_count']
    monthly_email_counts[ym] += 1

monthly_avg_words = {}
for ym in sorted(monthly_word_totals.keys()):
    if ym != 'Unknown' and '-' in ym:
        try:
            year, month_str = ym.split('-')
            month_num = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                         'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}[month_str]
            monthly_avg_words[f"{year}-{month_num}"] = round(monthly_word_totals[ym] / monthly_email_counts[ym], 0)
        except Exception as e:
            print(f"Skipping {ym}: {e}")

# Trend tracking by month
monthly_kalshi = {}
monthly_polymarket = {}
monthly_securities_fraud = {}

for e in emails_2025:
    ym = e['year_month']
    if ym != 'Unknown' and '-' in ym:
        year, month_str = ym.split('-')
        month_num = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                     'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}[month_str]
        ym_key = f"{year}-{month_num}"
        
        kalshi_count = len(re.findall(r'\bKalshi\b', e['body'], re.IGNORECASE))
        polymarket_count = len(re.findall(r'\bPolymarket\b', e['body'], re.IGNORECASE))
        fraud_count = len(re.findall(r'\bsecurities fraud\b', e['body'], re.IGNORECASE))
        
        monthly_kalshi[ym_key] = monthly_kalshi.get(ym_key, 0) + kalshi_count
        monthly_polymarket[ym_key] = monthly_polymarket.get(ym_key, 0) + polymarket_count
        monthly_securities_fraud[ym_key] = monthly_securities_fraud.get(ym_key, 0) + fraud_count

stats = {
    'boring_issues': 0,
    'saylor_mentions': total_saylor,
    'ackman_mentions': total_ackman,
    'avg_words': round(avg_words, 0),
    'total_issues': total_emails,
    'total_footones': total_footones,
    'avg_footones': round(avg_footones, 2),
    'year_distribution': {'2025': total_emails},
    'top_words': dict(word_counts.most_common(50)),
    'top_companies': dict(sorted(company_counts.items(), key=lambda x: -x[1])[:15]),
    'top_crypto': dict(sorted(crypto_counts.items(), key=lambda x: -x[1])),
    'monthly_avg_words': monthly_avg_words,
    'monthly_kalshi': dict(sorted(monthly_kalshi.items())),
    'monthly_polymarket': dict(sorted(monthly_polymarket.items())),
    'monthly_securities_fraud': dict(sorted(monthly_securities_fraud.items()))
}

with open('newsletter_data.json', 'w') as f:
    json.dump(stats, f, indent=2)

print("Stats saved to newsletter_data.json")
print(f"2025 emails: {total_emails}")
print(f"Avg words: {avg_words:.0f}")
print(f"Avg footones: {avg_footones:.2f}")
print(f"Total Saylor: {total_saylor}")
print(f"Total Ackman: {total_ackman}")
print(f"Top companies: {sorted(company_counts.items(), key=lambda x: -x[1])[:10]}")
print(f"Top crypto: {sorted(crypto_counts.items(), key=lambda x: -x[1])[:10]}")
print(f"Monthly avg words: {monthly_avg_words}")
