# dailyNews

Tools to publish a daily newspaper.

## Email automation

This project can import emails from an IMAP inbox and turn each message into a newspaper article file.

The automation is implemented in:

- `src/email_articles.py`
- `src/auto_news.py`

### Install

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you are on Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Required environment variables

Set these in your shell before running the import:

```bash
export EMAIL_HOST=imap.example.com
export EMAIL_USER=you@example.com
export EMAIL_PASSWORD='your-app-password'
export EMAIL_FOLDER=INBOX
export EMAIL_LOOKBACK_DAYS=7
```

For Gmail / Google Workspace, use your IMAP host:

```bash
export EMAIL_HOST=imap.gmail.com
```

And make sure to create an app password if Google requires one.

### Run the importer

From the project root:

```bash
python src/auto_news.py --output-dir .
```

This reads recent unread emails and saves the generated article files into a date-based folder such as:

```text
./240101_15/
```

The generated files are in the same format used by the rest of the newspaper generator:

- `a_<slug>.tex`
- `a_<slug>.json`

### Example cron job

To run it automatically every morning at 06:00:

```cron
0 6 * * * cd /path/to/dailyNews && source .venv/bin/activate && EMAIL_HOST=imap.gmail.com EMAIL_USER=you@example.com EMAIL_PASSWORD='your-app-password' EMAIL_FOLDER=INBOX EMAIL_LOOKBACK_DAYS=7 python src/auto_news.py --output-dir /path/to/dailyNews >> /path/to/dailyNews/email_import.log 2>&1
```

### Where to install it

Install the project on the same machine/server where you want the newspaper generation to run, and where the email account is reachable over IMAP.

This is typically:

- your local development machine,
- a small Linux server,
- or a scheduled VM / Raspberry Pi / NAS box that can access the mailbox over IMAP.

The importer does not need a desktop UI; it can be scheduled in cron or another task runner and simply generates the article files for the newspaper tool.
