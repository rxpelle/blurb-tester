# Copart API Guide for Registered Members

## Overview

As a registered Copart member, you likely have access to API endpoints that provide vehicle data in JSON format. This is much better than web scraping!

## Step 1: Discover API Endpoints

Run the API discovery tool:

```bash
python3 discover_api.py
```

**What it does:**
1. Opens a browser window (visible)
2. Asks for your Copart login credentials
3. Logs you in
4. Monitors network traffic for API calls
5. Saves all API endpoints to `logs/copart_api_calls.json`

**What to look for:**
- Endpoints containing: `/api/`, `/rest/`, `/graphql/`
- Search-related endpoints: `/search`, `/vehicles`, `/lots`
- Authentication tokens in headers
- Request/response formats

## Step 2: Analyze the API Calls

After running the discovery tool, check:

```bash
cat logs/copart_api_calls.json
```

Look for:

### 1. **Authentication**
```json
{
  "headers": {
    "Authorization": "Bearer xxx...",
    "X-Auth-Token": "xxx...",
    "Cookie": "session=xxx..."
  }
}
```

### 2. **Search Endpoints**
Common patterns:
- `https://www.copart.com/api/v1/search`
- `https://www.copart.com/api/lots/search`
- `https://www.copart.com/public/data/...`

### 3. **Vehicle Data Endpoints**
- `https://www.copart.com/api/vehicle/{lot_number}`
- `https://www.copart.com/api/lots/{lot_id}`

### 4. **Request Format**
```json
{
  "query": "Toyota",
  "location": "OR",
  "page": 1,
  "size": 100
}
```

## Step 3: Create API Credentials File

Once you find the API endpoints, create a credentials file:

```bash
# Create .env file (never commit this!)
cat > config/.env << 'EOF'
COPART_USERNAME=your_email@example.com
COPART_PASSWORD=your_password
COPART_API_KEY=<if_needed>
EOF
```

## Step 4: Use the API Client

I'll create an API client for you once we discover the endpoints!

## Common Copart API Patterns

Based on typical auction site APIs, Copart likely uses:

### Authentication
- Session cookies after login
- Bearer tokens
- API keys for members

### Search API
```
POST /api/v1/search
{
  "query": "Toyota Camry",
  "filters": {
    "location": ["OR - PORTLAND"],
    "year": {"min": 2015, "max": 2023},
    "damage": ["Front End", "Hail"]
  },
  "page": 1,
  "size": 100
}
```

### Vehicle Details API
```
GET /api/v1/lot/{lot_number}
```

### Auction Schedule API
```
GET /api/v1/auctions/upcoming
```

## Benefits of Using the API

### vs. Web Scraping:
✅ **Faster** - Direct JSON responses
✅ **More reliable** - No selector changes
✅ **No bot detection** - You're authenticated
✅ **Complete data** - Access to all fields
✅ **Rate limit friendly** - Designed for programmatic access
✅ **Legal** - Within Terms of Service for members

## Next Steps

1. **Run the discovery tool** to find actual endpoints
2. **Share the results** with me (logs/copart_api_calls.json)
3. **I'll create a proper API client** based on what we find
4. **Update the scraper** to use API instead of web scraping

## Alternative: Manual API Discovery

If you prefer to discover manually:

1. **Open Copart in Chrome**
2. **Open DevTools** (F12)
3. **Go to Network tab**
4. **Filter by "Fetch/XHR"**
5. **Log in and search for vehicles**
6. **Look for JSON responses**
7. **Note the URLs, headers, and request format**

## Example: What We're Looking For

In DevTools Network tab, you might see:

```
Request URL: https://www.copart.com/api/vehicle/search
Request Method: POST
Headers:
  Authorization: Bearer eyJhbGc...
  Content-Type: application/json

Request Payload:
{
  "location": "OR",
  "page": 1
}

Response:
{
  "total": 250,
  "vehicles": [
    {
      "lotNumber": 12345678,
      "make": "TOYOTA",
      "model": "CAMRY",
      "year": 2020,
      "currentBid": 5000,
      "estimatedValue": 12000,
      ...
    }
  ]
}
```

## Security Notes

⚠️ **IMPORTANT:**
- Never commit credentials to git
- Keep `.env` file private
- Don't share API tokens
- Respect rate limits
- Follow Copart's Terms of Service

---

**Ready to discover the API? Run:**
```bash
python3 discover_api.py
```
