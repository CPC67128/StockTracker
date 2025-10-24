# Guide pour PEA (Plan d'Épargne en Actions) - French Stocks

## Guide for French PEA Stock Tracking

StockTracker fully supports tracking French stocks using **ISIN codes** (e.g., FR0000121014 for LVMH) or traditional ticker symbols (e.g., MC for LVMH).

## Supported Formats

### 1. ISIN Codes (Recommended for French Stocks)

**What is an ISIN?**
- International Securities Identification Number
- 12 characters: 2-letter country code + 10 alphanumeric characters
- Example: `FR0000121014` (LVMH)

**Benefits:**
- ✅ Unambiguous identification
- ✅ Works perfectly with Boursorama scraper
- ✅ Automatically prioritizes French data sources
- ✅ Official format used by French brokers (PEA, compte-titres)

### 2. Ticker Symbols

French stocks also have short ticker symbols:
- LVMH: `MC`
- TotalEnergies: `TTE`
- Air Liquide: `AI`

## Configuration for PEA Stocks

### Example stocks.json for French PEA:

```json
{
  "stocks": [
    {
      "symbol": "FR0000121014",
      "name": "LVMH",
      "upper_threshold": 700.0,
      "lower_threshold": 600.0
    },
    {
      "symbol": "FR0000120271",
      "name": "TotalEnergies",
      "upper_threshold": 60.0,
      "lower_threshold": 50.0
    },
    {
      "symbol": "FR0000120073",
      "name": "Air Liquide",
      "upper_threshold": 180.0,
      "lower_threshold": 165.0
    },
    {
      "symbol": "FR0000120628",
      "name": "AXA",
      "upper_threshold": 35.0,
      "lower_threshold": 28.0
    },
    {
      "symbol": "FR0000131104",
      "name": "BNP Paribas",
      "upper_threshold": 70.0,
      "lower_threshold": 60.0
    }
  ]
}
```

## Common CAC 40 ISIN Codes

Here are some popular French stocks for your PEA:

| Company | Ticker | ISIN | Sector |
|---------|--------|------|--------|
| LVMH | MC | FR0000121014 | Luxe |
| TotalEnergies | TTE | FR0000120271 | Énergie |
| Air Liquide | AI | FR0000120073 | Gaz industriels |
| Sanofi | SAN | FR0000120578 | Pharmaceutique |
| L'Oréal | OR | FR0000120321 | Cosmétiques |
| BNP Paribas | BNP | FR0000131104 | Banque |
| AXA | CS | FR0000120628 | Assurance |
| Schneider Electric | SU | FR0000121972 | Électrique |
| Danone | BN | FR0000120644 | Agroalimentaire |
| Hermès | RMS | FR0000052292 | Luxe |
| Safran | SAF | FR0000073272 | Aéronautique |
| Vinci | DG | FR0000125486 | Construction |
| Stellantis | STLAM | NL0015000XS7 | Automobile |
| Thales | HO | FR0000033904 | Défense |
| Engie | ENGI | FR0010208488 | Énergie |

## How It Works

### 1. Automatic Source Selection

When StockTracker detects an ISIN code or French symbol:

```python
# Detects FR prefix → Prioritizes Boursorama
sources = ['boursorama', 'google', 'marketwatch']
```

### 2. ISIN Search Process

For ISIN codes, the scraper:
1. Searches Boursorama with the ISIN
2. Finds the stock page from search results
3. Extracts the current price
4. Returns price in EUR (€)

### 3. Price Format

French stocks use European number format:
- Decimal separator: `,` (comma)
- Example: `622,60 €`

The scraper automatically handles both formats:
- European: `622,60 €` → 622.60
- US: `622.60 USD` → 622.60

## Setup for French PEA

### 1. Enable Web Scraping

Edit `.env`:
```env
USE_WEB_SCRAPING=true
CHECK_INTERVAL_MINUTES=30
```

### 2. Configure Your PEA Stocks

Edit `config/stocks.json` with your ISIN codes:

```json
{
  "stocks": [
    {
      "symbol": "FR0000121014",
      "upper_threshold": 700.0,
      "lower_threshold": 600.0
    }
  ]
}
```

### 3. Run StockTracker

```bash
python src/main.py
```

You'll see:
```
INFO - Detected French/ISIN stock FR0000121014, prioritizing Boursorama
INFO - Searching Boursorama for ISIN FR0000121014
INFO - Found stock page: https://www.boursorama.com/cours/1rPMC/
INFO - Fetched FR0000121014 from Boursorama: €622.60
```

## Finding ISIN Codes

### Method 1: From Your Broker

Your PEA broker (Boursorama, Fortuneo, Bourse Direct, etc.) displays ISIN codes:
- In your portfolio
- In order confirmations
- In transaction history

### Method 2: Boursorama Search

1. Go to https://www.boursorama.com/
2. Search for your stock (e.g., "LVMH")
3. ISIN is displayed on the stock page

### Method 3: Use Our Helper Script

Create a file `find_isin.py`:

```python
import sys
sys.path.insert(0, 'src')
from web_scraper import WebScraper

scraper = WebScraper()
# Test if ISIN works
price = scraper.get_stock_price('FR0000121014')
print(f"LVMH: €{price}")
```

## Thresholds for French Stocks

### Setting Realistic Thresholds

Consider:
- **Historical range**: Check 52-week high/low
- **Support/resistance levels**
- **Your entry price** (if you already own the stock)
- **Target price** (analyst consensus)

### Example Thresholds:

**LVMH (FR0000121014)**
- Current: ~€660
- Upper: €700 (sell signal or take profit)
- Lower: €600 (buy opportunity or stop loss)

**TotalEnergies (FR0000120271)**
- Current: ~€54
- Upper: €60
- Lower: €50

## Email Alerts in French

You can customize email templates to be in French. Edit `src/email_notifier.py`:

```python
def _build_email_body(self, violations: List[Dict]) -> str:
    body = "Alerte StockTracker - Seuils atteints\n"
    body += "=" * 50 + "\n\n"

    for violation in violations:
        body += f"Action: {violation['symbol']}\n"
        body += f"Prix actuel: {violation['current_price']:.2f} €\n"
        body += f"Seuil ({violation['threshold_type']}): {violation['threshold']:.2f} €\n"
        body += f"Statut: {violation['message']}\n"
        body += "-" * 50 + "\n\n"

    body += "\nCeci est une alerte automatique de StockTracker.\n"
    return body
```

## PEA-Specific Tips

### 1. Market Hours

French markets (Euronext Paris) are open:
- Monday-Friday: 9:00 - 17:30 CET
- Prices update only during market hours
- Set `CHECK_INTERVAL_MINUTES` accordingly

### 2. Currency

All French stocks are priced in EUR (€):
- No currency conversion needed
- Thresholds in euros
- Alerts in euros

### 3. Dividends

StockTracker shows **ex-dividend prices**:
- Price drops on ex-dividend date
- Adjust thresholds after dividend payments

### 4. Corporate Actions

Update your configuration after:
- Stock splits
- Mergers
- Ticker changes

## Troubleshooting

### ISIN Not Found

**Problem:**
```
WARNING - Could not find price element for FR0000XXXXX
```

**Solutions:**
1. Verify ISIN is correct (check broker statement)
2. Stock might be delisted
3. Try the ticker symbol instead
4. Check Boursorama manually: https://www.boursorama.com/

### Wrong Price

**Problem:** Price seems incorrect

**Solutions:**
1. Check if it's a different share class (A, B, etc.)
2. Verify on Boursorama manually
3. Some ISINs have multiple listings

### Encoding Issues

**Problem:** Euro symbol displays incorrectly

**Solution:**
- This is a display issue only
- Prices are calculated correctly
- Set console encoding: `chcp 65001` (Windows CMD)

## Performance

### Recommended Settings for French PEA

```env
# .env
USE_WEB_SCRAPING=true
CHECK_INTERVAL_MINUTES=30  # Check every 30 minutes
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**Why 30 minutes?**
- French stocks less volatile than US
- Boursorama has no rate limits with reasonable intervals
- Reduces unnecessary checks
- Still catches significant moves

### Tracking Multiple Stocks

You can safely track 10-20 French stocks:
- 3-second delay between requests
- Boursorama is reliable
- No rate limiting with 30+ minute intervals

## Example PEA Portfolio Configuration

```json
{
  "stocks": [
    {
      "symbol": "FR0000121014",
      "name": "LVMH",
      "upper_threshold": 700.0,
      "lower_threshold": 600.0,
      "notes": "Position principale - luxe"
    },
    {
      "symbol": "FR0000120271",
      "name": "TotalEnergies",
      "upper_threshold": 60.0,
      "lower_threshold": 50.0,
      "notes": "Dividende élevé"
    },
    {
      "symbol": "FR0000120073",
      "name": "Air Liquide",
      "upper_threshold": 180.0,
      "lower_threshold": 165.0,
      "notes": "Valeur défensive"
    },
    {
      "symbol": "FR0000120578",
      "name": "Sanofi",
      "upper_threshold": 105.0,
      "lower_threshold": 90.0,
      "notes": "Pharma - dividende stable"
    },
    {
      "symbol": "FR0000120321",
      "name": "L'Oréal",
      "upper_threshold": 450.0,
      "lower_threshold": 400.0,
      "notes": "Croissance à long terme"
    }
  ]
}
```

## Legal & Tax Notes

**Important:** StockTracker is a monitoring tool only.

- Does NOT execute trades
- Does NOT provide investment advice
- Does NOT track PEA tax status
- You remain responsible for:
  - Investment decisions
  - PEA contribution limits (€150,000)
  - Tax reporting
  - Regulatory compliance

## Support

Questions about French stocks?
- Check `WEB_SCRAPING.md` for technical details
- See `TROUBLESHOOTING.md` for common issues
- Test ISIN codes before adding to portfolio

## Contributing

Have a suggestion for French stock tracking?
- Add more French data sources
- Improve ISIN detection
- French language support
- Euronext-specific features

---

**Bon trading! 📈**
