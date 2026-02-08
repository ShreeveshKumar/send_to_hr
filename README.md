This bot automates the process of finding and applying for jobs via Telegram. It monitors specified Telegram channels for job postings, extracts contact information, and sends personalized cold emails using AI-generated content.

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repo_url>
   cd tele-bot
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Configure Environment:**
   Copy `.env.example` to `.env` and fill in the required values.
   ```bash
   cp .env.example .env
   ```

   **Required Variables:**
   - `API_ID`, `API_HASH`: Telegram API credentials.
   - `CHANNEL_NAMES`: Comma-separated list of Telegram channel usernames to monitor.
   - `BOT_KEY`: Tavily API key for AI generation.
   - `DATABASE_URL`: MongoDB connection string.
   - `MY_EMAIL`, `APP_PASSWORD`: Gmail credentials (use App Password).
   - `NAME`: Your full name.
   - `ROLE_KEYWORD`: Default role to apply for if context is unclear (e.g., "Backend Engineer").
   - `LINKS`: Comma-separated links to your profiles (LinkedIn, GitHub).
   - `SCRAPE_LINKS`: Comma-separated URLs to your portfolio/resume for context.


The bot will start, wait until 9:00 AM, and then process any new messages since its last run.
