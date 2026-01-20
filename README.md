# linkedin2md

[![PyPI version](https://img.shields.io/pypi/v/linkedin2md)](https://pypi.org/project/linkedin2md/)
[![Python versions](https://img.shields.io/pypi/pyversions/linkedin2md)](https://pypi.org/project/linkedin2md/)
[![License](https://img.shields.io/pypi/l/linkedin2md)](https://github.com/juanmanueldaza/linkedin2md/blob/main/LICENSE)
[![CI](https://github.com/juanmanueldaza/linkedin2md/actions/workflows/ci.yml/badge.svg)](https://github.com/juanmanueldaza/linkedin2md/actions/workflows/ci.yml)

Convert LinkedIn data exports to clean Markdown files - the ideal format for LLM analysis.

## Why Markdown?

Markdown is the lingua franca of AI tools. Once your LinkedIn data is in `.md` format, you can:

- **Upload to [NotebookLM](https://notebooklm.google.com/)** and have conversations about your career history
- **Use [Claude Projects](https://claude.ai)** to analyze patterns across your professional journey
- **Feed to [Obsidian](https://obsidian.md/)** with AI plugins for a personal career knowledge base
- **Run local LLMs** (Ollama, LM Studio) for completely private analysis

### Example Prompts

Once your LinkedIn data is in an LLM, try asking:

| Question | Data Used |
|----------|-----------|
| "What patterns do you see in my career transitions?" | experience.md |
| "What skills have I developed over time?" | skills.md, experience.md |
| "Group my connections by industry" | connections.md |
| "What themes appear in my recommendations?" | recommendations.md |
| "Summarize my job applications and outcomes" | job_applications.md |
| "What qualities do people consistently mention about me?" | recommendations.md, endorsements.md |
| "Based on my experience, what roles should I target?" | All files |

## Installation

**Recommended** (using pipx - installs in isolated environment):
```bash
pipx install linkedin2md
```

Or with pip (in a virtual environment):
```bash
pip install linkedin2md
```

> **Note**: On modern Linux systems (Debian, Ubuntu 23.04+, Fedora), use `pipx` to avoid the "externally-managed-environment" error.

## Usage

```bash
linkedin2md Complete_LinkedInDataExport.zip
linkedin2md export.zip -o ./my-profile
linkedin2md export.zip --lang es
```

Then drag the output folder into your favorite AI tool.

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `source` | LinkedIn ZIP export file (required) | - |
| `-o, --output` | Output directory | `linkedin_export` |
| `--lang` | Output language (`en` or `es`) | `en` |

## How to Export Your LinkedIn Data

Follow these steps to download your LinkedIn data:

1. **Go to Settings**: Log into LinkedIn, click your profile photo in the top right, then select **"Settings & Privacy"**

2. **Navigate to Data Privacy**: In the left sidebar, click **"Data privacy"**

3. **Request your data**: Click **"Get a copy of your data"**

4. **Select data to download**: 
   - Choose **"Download larger data archive"** for complete data
   - Or select specific categories if you only need certain data

5. **Request archive**: Click **"Request archive"**

6. **Wait for email**: LinkedIn will process your request and send an email when ready (usually within 24 hours, sometimes up to 72 hours for large archives)

7. **Download the ZIP file**: Click the download link in the email. The file will be named something like `Complete_LinkedInDataExport_01-20-2025.zip`

> **Note**: The download link expires after a few days. Download it promptly and store it safely.

## LLM Tools That Work Great With This

| Tool | Type | Best For |
|------|------|----------|
| [NotebookLM](https://notebooklm.google.com/) | Cloud | Conversational analysis, audio summaries |
| [Claude Projects](https://claude.ai) | Cloud | Deep analysis, long context |
| [ChatGPT](https://chat.openai.com) | Cloud | General analysis, quick insights |
| [Obsidian](https://obsidian.md/) + AI plugins | Local | Personal knowledge base, linked notes |
| [Open Notebook](https://github.com/Open-Notebook/Open-Notebook) | Local/Cloud | 16+ AI models, open source |
| [Ollama](https://ollama.ai/) | Local | Private, offline analysis |

## Output

Creates 40+ markdown files in the output directory, organized by category:

### Core Profile
- `profile.md` - Name, title, contact, summary
- `experience.md` - Work history with achievements
- `education.md` - Educational background
- `skills.md` - Professional skills
- `certifications.md` - Certifications and licenses
- `languages.md` - Language proficiencies
- `projects.md` - Personal and professional projects

### Recommendations & Endorsements
- `recommendations.md` - Recommendations received
- `endorsements.md` - Skill endorsements received

### Learning
- `learning.md` - LinkedIn Learning courses
- `learning_reviews.md` - Course reviews and ratings

### Network
- `connections.md` - Your connections
- `companies_followed.md` - Companies you follow
- `members_followed.md` - People you follow
- `invitations.md` - Connection invitations sent/received
- `imported_contacts.md` - Contacts imported from address book

### Content & Activity
- `posts.md` - Your posts and shares
- `comments.md` - Comments you made
- `reactions.md` - Likes and reactions
- `reposts.md` - Content you reposted
- `votes.md` - Poll votes
- `saved_items.md` - Bookmarked content
- `events.md` - Events attended

### Job Search
- `job_applications.md` - All job applications
- `saved_jobs.md` - Jobs you saved
- `job_preferences.md` - Job seeker preferences
- `saved_job_answers.md` - Saved application answers
- `screening_responses.md` - Screening question responses
- `saved_job_alerts.md` - Job alert settings

### Activity History
- `search_queries.md` - Search history
- `logins.md` - Login history
- `security_challenges.md` - Security verification events

### Advertising & Privacy
- `ads_clicked.md` - Ads you clicked
- `ad_targeting.md` - How LinkedIn targets ads to you
- `lan_ads.md` - LinkedIn Audience Network engagement
- `inferences.md` - LinkedIn's inferences about you

### Payments
- `receipts.md` - Premium subscription receipts

### Services Marketplace
- `service_engagements.md` - Service provider engagements
- `service_opportunities.md` - Service opportunities

### Identity
- `verifications.md` - Identity verifications
- `identity_assets.md` - Uploaded documents (resumes, etc.)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

GPL-2.0 - see [LICENSE](LICENSE) for details.
