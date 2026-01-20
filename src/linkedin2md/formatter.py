"""Markdown formatter for LinkedIn data."""

from pathlib import Path


class MarkdownFormatter:
    """Format LinkedIn data as clean Markdown files."""

    def __init__(self, lang: str = "en"):
        """Initialize formatter with preferred language."""
        self.lang = lang

    def format_all(self, data: dict, output_dir: Path) -> list[Path]:
        """Format all sections and write files to output directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        files = []

        sections = [
            # Core profile
            ("profile", self._format_profile),
            ("experience", self._format_experience),
            ("education", self._format_education),
            ("skills", self._format_skills),
            ("certifications", self._format_certifications),
            ("languages", self._format_languages),
            ("projects", self._format_projects),
            # Recommendations & endorsements
            ("recommendations", self._format_recommendations),
            ("recommendations_given", self._format_recommendations_given),
            ("endorsements", self._format_endorsements),
            ("endorsements_given", self._format_endorsements_given),
            # Learning
            ("learning", self._format_learning),
            ("learning_reviews", self._format_learning_reviews),
            # Network
            ("connections", self._format_connections),
            ("companies_followed", self._format_companies_followed),
            ("members_followed", self._format_members_followed),
            ("invitations", self._format_invitations),
            ("imported_contacts", self._format_imported_contacts),
            # Content & activity
            ("posts", self._format_posts),
            ("comments", self._format_comments),
            ("reactions", self._format_reactions),
            ("reposts", self._format_reposts),
            ("votes", self._format_votes),
            ("saved_items", self._format_saved_items),
            ("events", self._format_events),
            ("media", self._format_media),
            ("messages", self._format_messages),
            # Job search
            ("job_applications", self._format_job_applications),
            ("saved_jobs", self._format_saved_jobs),
            ("job_preferences", self._format_job_preferences),
            ("saved_job_answers", self._format_saved_job_answers),
            ("screening_responses", self._format_screening_responses),
            ("saved_job_alerts", self._format_saved_job_alerts),
            # Activity history
            ("search_queries", self._format_search_queries),
            ("logins", self._format_logins),
            ("security_challenges", self._format_security_challenges),
            # Advertising & privacy
            ("ads_clicked", self._format_ads_clicked),
            ("ad_targeting", self._format_ad_targeting),
            ("lan_ads", self._format_lan_ads),
            ("inferences", self._format_inferences),
            # Premium & payments
            ("receipts", self._format_receipts),
            # Services marketplace
            ("service_engagements", self._format_service_engagements),
            ("service_opportunities", self._format_service_opportunities),
            # Identity & verification
            ("verifications", self._format_verifications),
            ("identity_assets", self._format_identity_assets),
        ]

        for section_key, formatter in sections:
            section_data = data.get(section_key)
            if section_key == "profile":
                content = formatter(data)
            elif section_data:
                content = formatter(section_data)
            else:
                continue

            if content and content.strip():
                path = output_dir / f"{section_key}.md"
                path.write_text(content, encoding="utf-8")
                files.append(path)

        return files

    def _get_text(self, bilingual: dict | str | None) -> str:
        """Extract text in preferred language with fallback."""
        if bilingual is None:
            return ""
        if isinstance(bilingual, str):
            return bilingual
        return (
            bilingual.get(self.lang) or bilingual.get("en") or bilingual.get("es") or ""
        )

    def _format_profile(self, data: dict) -> str:
        """Format profile section."""
        lines = []
        name = data.get("name", "")
        if name:
            lines.append(f"# {name}")
            lines.append("")

        title = self._get_text(data.get("title"))
        if title:
            lines.append(f"**{title}**")
            lines.append("")

        contact_parts = []
        if data.get("location"):
            contact_parts.append(data["location"])
        if data.get("email"):
            contact_parts.append(data["email"])
        if data.get("phone"):
            contact_parts.append(data["phone"])
        if contact_parts:
            lines.append(" | ".join(contact_parts))
            lines.append("")

        summary = self._get_text(data.get("summary"))
        if summary:
            lines.append("## Summary")
            lines.append("")
            lines.append(summary)
            lines.append("")

        return "\n".join(lines)

    def _format_experience(self, experiences: list) -> str:
        """Format experience section."""
        if not experiences:
            return ""

        lines = ["# Experience", ""]

        for exp in experiences:
            company = exp.get("company", "")
            role = self._get_text(exp.get("role"))

            lines.append(f"## {company}")

            date_parts = []
            if exp.get("start"):
                date_parts.append(exp["start"])
            if exp.get("end"):
                date_parts.append(exp["end"])
            else:
                date_parts.append("Present")

            location = exp.get("location", "")
            meta = f"**{role}**" if role else ""
            if date_parts:
                meta += " | " + " - ".join(date_parts)
            if location:
                meta += f" | {location}"
            if meta:
                lines.append(meta)
            lines.append("")

            achievements = exp.get("achievements", [])
            for ach in achievements:
                text = self._get_text(ach.get("text"))
                if text:
                    lines.append(f"- {text}")

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _format_education(self, education: list) -> str:
        """Format education section."""
        if not education:
            return ""

        lines = ["# Education", ""]

        for edu in education:
            institution = edu.get("institution", "")
            degree = self._get_text(edu.get("degree"))

            lines.append(f"## {institution}")

            meta_parts = []
            if degree:
                meta_parts.append(f"**{degree}**")
            if edu.get("start"):
                date_str = edu["start"]
                if edu.get("end"):
                    date_str += f" - {edu['end']}"
                meta_parts.append(date_str)
            if meta_parts:
                lines.append(" | ".join(meta_parts))
            lines.append("")

            notes = self._get_text(edu.get("notes"))
            if notes:
                lines.append(f"> {notes}")
                lines.append("")

            activities = edu.get("activities")
            if activities:
                lines.append(f"Activities: {activities}")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _format_skills(self, skills: list) -> str:
        """Format skills section."""
        if not skills:
            return ""
        return "# Skills\n\n" + ", ".join(skills) + "\n"

    def _format_certifications(self, certifications: list) -> str:
        """Format certifications section."""
        if not certifications:
            return ""

        lines = ["# Certifications", ""]

        for cert in certifications:
            name = cert.get("name", "")
            lines.append(f"## {name}")

            meta_parts = []
            if cert.get("issuer"):
                meta_parts.append(f"**{cert['issuer']}**")
            if cert.get("date"):
                meta_parts.append(cert["date"])
            if meta_parts:
                lines.append(" | ".join(meta_parts))

            if cert.get("url"):
                lines.append("")
                lines.append(f"[View Certificate]({cert['url']})")

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _format_languages(self, languages: list) -> str:
        """Format languages section."""
        if not languages:
            return ""

        lines = ["# Languages", ""]

        for lang in languages:
            name = lang.get("name", "")
            proficiency = lang.get("proficiency", "")
            if proficiency:
                lines.append(f"- **{name}**: {proficiency}")
            else:
                lines.append(f"- {name}")

        lines.append("")
        return "\n".join(lines)

    def _format_projects(self, projects: list) -> str:
        """Format projects section."""
        if not projects:
            return ""

        lines = ["# Projects", ""]

        for proj in projects:
            title = proj.get("title", "")
            lines.append(f"## {title}")

            date_parts = []
            if proj.get("start"):
                date_parts.append(proj["start"])
            if proj.get("end"):
                date_parts.append(proj["end"])
            if date_parts:
                lines.append(" - ".join(date_parts))

            description = self._get_text(proj.get("description"))
            if description:
                lines.append("")
                lines.append(description)

            if proj.get("url"):
                lines.append("")
                lines.append(f"[View Project]({proj['url']})")

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _format_recommendations(self, recommendations: list) -> str:
        """Format recommendations section."""
        if not recommendations:
            return ""

        lines = ["# Recommendations", ""]

        for rec in recommendations:
            author = rec.get("author", "")
            lines.append(f"## From {author}")

            meta_parts = []
            if rec.get("title"):
                meta_parts.append(f"**{rec['title']}**")
            if rec.get("company"):
                meta_parts.append(f"at {rec['company']}")
            if rec.get("date"):
                meta_parts.append(f"| {rec['date']}")
            if meta_parts:
                lines.append(" ".join(meta_parts))

            text = self._get_text(rec.get("text"))
            if text:
                lines.append("")
                lines.append(f"> {text}")

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _format_recommendations_given(self, recommendations: list) -> str:
        """Format recommendations given section."""
        if not recommendations:
            return ""

        lines = ["# Recommendations Given", ""]

        for rec in recommendations:
            recipient = rec.get("recipient", "")
            lines.append(f"## To {recipient}")

            meta_parts = []
            if rec.get("title"):
                meta_parts.append(f"**{rec['title']}**")
            if rec.get("company"):
                meta_parts.append(f"at {rec['company']}")
            if rec.get("date"):
                meta_parts.append(f"| {rec['date']}")
            if meta_parts:
                lines.append(" ".join(meta_parts))

            text = self._get_text(rec.get("text"))
            if text:
                lines.append("")
                lines.append(f"> {text}")

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _format_endorsements(self, endorsements: list) -> str:
        """Format endorsements section."""
        if not endorsements:
            return ""

        lines = ["# Endorsements", ""]
        lines.append("| Skill | Endorsed By | Date |")
        lines.append("|-------|-------------|------|")

        for end in endorsements:
            skill = end.get("skill", "")
            endorser = end.get("endorser", "")
            date = end.get("date", "")
            lines.append(f"| {skill} | {endorser} | {date} |")

        lines.append("")
        return "\n".join(lines)

    def _format_endorsements_given(self, endorsements: list) -> str:
        """Format endorsements given section."""
        if not endorsements:
            return ""

        lines = ["# Endorsements Given", ""]
        lines.append("| Skill | Endorsed | Date |")
        lines.append("|-------|----------|------|")

        for end in endorsements:
            skill = end.get("skill", "")
            endorsee = end.get("endorsee", "")
            date = end.get("date", "")
            lines.append(f"| {skill} | {endorsee} | {date} |")

        lines.append("")
        return "\n".join(lines)

    def _format_learning(self, learning: list) -> str:
        """Format LinkedIn Learning section."""
        if not learning:
            return ""

        lines = ["# LinkedIn Learning", ""]

        for course in learning:
            title = course.get("title", "")
            completed = course.get("completed_at")
            status = "Completed" if completed else "In Progress"
            lines.append(f"- **{title}** ({status})")

        lines.append("")
        return "\n".join(lines)

    def _format_learning_reviews(self, reviews: list) -> str:
        """Format learning reviews section."""
        if not reviews:
            return ""

        lines = ["# Learning Reviews", ""]
        lines.append("| Content | Rating | Date |")
        lines.append("|---------|--------|------|")

        for review in reviews:
            content = review.get("content", "")
            rating = review.get("rating", "")
            date = review.get("date", "")
            lines.append(f"| {content} | {rating} | {date} |")

        lines.append("")
        return "\n".join(lines)

    def _format_connections(self, connections: list) -> str:
        """Format connections section as table."""
        if not connections:
            return ""

        lines = ["# Connections", ""]
        lines.append("| Name | Company | Position | Connected |")
        lines.append("|------|---------|----------|-----------|")

        for conn in connections:
            name = conn.get("name", "")
            company = conn.get("company", "") or ""
            position = conn.get("position", "") or ""
            connected = conn.get("connected_on", "") or ""
            lines.append(f"| {name} | {company} | {position} | {connected} |")

        lines.append("")
        return "\n".join(lines)

    def _format_companies_followed(self, companies: list) -> str:
        """Format companies followed section."""
        if not companies:
            return ""

        lines = ["# Companies Followed", ""]
        for company in companies:
            name = company.get("name", "")
            lines.append(f"- {name}")
        lines.append("")
        return "\n".join(lines)

    def _format_members_followed(self, members: list) -> str:
        """Format members followed section."""
        if not members:
            return ""

        lines = ["# Members Followed", ""]
        lines.append("| Name | Date | Status |")
        lines.append("|------|------|--------|")

        for member in members:
            name = member.get("name", "")
            date = member.get("date", "") or ""
            status = member.get("status", "") or ""
            lines.append(f"| {name} | {date} | {status} |")

        lines.append("")
        return "\n".join(lines)

    def _format_invitations(self, invitations: list) -> str:
        """Format invitations section."""
        if not invitations:
            return ""

        lines = ["# Connection Invitations", ""]
        lines.append("| From | To | Date | Direction |")
        lines.append("|------|-----|------|-----------|")

        for inv in invitations:
            from_name = inv.get("from", "")
            to_name = inv.get("to", "")
            date = inv.get("sent_at", "") or ""
            direction = inv.get("direction", "") or ""
            lines.append(f"| {from_name} | {to_name} | {date} | {direction} |")

        lines.append("")
        return "\n".join(lines)

    def _format_imported_contacts(self, contacts: list) -> str:
        """Format imported contacts section."""
        if not contacts:
            return ""

        lines = ["# Imported Contacts", ""]
        lines.append("| Name | Email | Title |")
        lines.append("|------|-------|-------|")

        for contact in contacts:
            name = contact.get("name", "") or ""
            emails = contact.get("emails", "") or ""
            title = contact.get("title", "") or ""
            lines.append(f"| {name} | {emails} | {title} |")

        lines.append("")
        return "\n".join(lines)

    def _format_posts(self, posts: list) -> str:
        """Format posts section."""
        if not posts:
            return ""

        lines = ["# Posts", ""]

        for post in posts:
            date = post.get("date", "")
            lines.append(f"## {date}")

            content = self._get_text(post.get("content"))
            if content:
                lines.append("")
                lines.append(content)

            if post.get("url"):
                lines.append("")
                lines.append(f"[View Post]({post['url']})")

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _format_comments(self, comments: list) -> str:
        """Format comments section."""
        if not comments:
            return ""

        lines = ["# Comments", ""]

        for comment in comments:
            date = comment.get("date", "")
            message = self._get_text(comment.get("message"))
            url = comment.get("url", "")

            lines.append(f"**{date}**")
            if message:
                lines.append(f"> {message}")
            if url:
                lines.append(f"[View]({url})")
            lines.append("")

        return "\n".join(lines)

    def _format_reactions(self, reactions: list) -> str:
        """Format reactions section."""
        if not reactions:
            return ""

        lines = ["# Reactions", ""]
        lines.append("| Date | Type | Link |")
        lines.append("|------|------|------|")

        for reaction in reactions:
            date = reaction.get("date", "")
            rtype = reaction.get("type", "") or ""
            url = reaction.get("url", "") or ""
            link = f"[View]({url})" if url else ""
            lines.append(f"| {date} | {rtype} | {link} |")

        lines.append("")
        return "\n".join(lines)

    def _format_reposts(self, reposts: list) -> str:
        """Format reposts section."""
        if not reposts:
            return ""

        lines = ["# Reposts", ""]
        lines.append("| Date | Link |")
        lines.append("|------|------|")

        for repost in reposts:
            date = repost.get("date", "")
            url = repost.get("url", "") or ""
            link = f"[View]({url})" if url else ""
            lines.append(f"| {date} | {link} |")

        lines.append("")
        return "\n".join(lines)

    def _format_votes(self, votes: list) -> str:
        """Format votes section."""
        if not votes:
            return ""

        lines = ["# Poll Votes", ""]
        lines.append("| Date | Option | Link |")
        lines.append("|------|--------|------|")

        for vote in votes:
            date = vote.get("date", "")
            option = vote.get("option", "") or ""
            url = vote.get("url", "") or ""
            link = f"[View]({url})" if url else ""
            lines.append(f"| {date} | {option} | {link} |")

        lines.append("")
        return "\n".join(lines)

    def _format_saved_items(self, items: list) -> str:
        """Format saved items section."""
        if not items:
            return ""

        lines = ["# Saved Items", ""]
        lines.append("| Saved At | Link |")
        lines.append("|----------|------|")

        for item in items:
            saved_at = item.get("saved_at", "") or ""
            url = item.get("url", "") or ""
            link = f"[View]({url})" if url else ""
            lines.append(f"| {saved_at} | {link} |")

        lines.append("")
        return "\n".join(lines)

    def _format_events(self, events: list) -> str:
        """Format events section."""
        if not events:
            return ""

        lines = ["# Events", ""]
        lines.append("| Name | Time | Status |")
        lines.append("|------|------|--------|")

        for event in events:
            name = event.get("name", "")
            time = event.get("time", "") or ""
            status = event.get("status", "") or ""
            lines.append(f"| {name} | {time} | {status} |")

        lines.append("")
        return "\n".join(lines)

    def _format_media(self, media: list) -> str:
        """Format uploaded media section."""
        if not media:
            return ""

        lines = ["# Uploaded Media", ""]
        lines.append("| Date | Description | Link |")
        lines.append("|------|-------------|------|")

        for m in media:
            date = m.get("date", "") or ""
            desc = m.get("description", "") or ""
            url = m.get("url", "") or ""
            link = f"[View]({url})" if url else ""
            lines.append(f"| {date} | {desc} | {link} |")

        lines.append("")
        return "\n".join(lines)

    def _format_messages(self, messages: list) -> str:
        """Format messages section."""
        if not messages:
            return ""

        lines = ["# Messages", ""]

        for msg in messages:
            date = msg.get("date", "")
            from_name = msg.get("from_name", "")
            to_name = msg.get("to_name", "")
            subject = msg.get("subject", "") or ""
            content = msg.get("content", "") or ""

            lines.append(f"## {date}")
            lines.append(f"**From:** {from_name} → **To:** {to_name}")
            if subject:
                lines.append(f"**Subject:** {subject}")
            if content:
                lines.append("")
                lines.append(f"> {content[:500]}{'...' if len(content) > 500 else ''}")
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _format_job_applications(self, applications: list) -> str:
        """Format job applications section as table."""
        if not applications:
            return ""

        lines = ["# Job Applications", ""]
        lines.append("| Date | Company | Position | Resume |")
        lines.append("|------|---------|----------|--------|")

        for app in applications:
            date = app.get("date", "")
            company = app.get("company", "")
            title = app.get("title", "")
            resume = app.get("resume_used", "") or ""
            lines.append(f"| {date} | {company} | {title} | {resume} |")

        lines.append("")
        return "\n".join(lines)

    def _format_saved_jobs(self, jobs: list) -> str:
        """Format saved jobs section as table."""
        if not jobs:
            return ""

        lines = ["# Saved Jobs", ""]
        lines.append("| Date | Company | Position |")
        lines.append("|------|---------|----------|")

        for job in jobs:
            date = job.get("date", "")
            company = job.get("company", "")
            title = job.get("title", "")
            lines.append(f"| {date} | {company} | {title} |")

        lines.append("")
        return "\n".join(lines)

    def _format_job_preferences(self, preferences: dict | None) -> str:
        """Format job preferences section."""
        if not preferences:
            return ""

        lines = ["# Job Seeker Preferences", ""]

        if preferences.get("locations"):
            lines.append(f"**Locations:** {', '.join(preferences['locations'])}")
            lines.append("")

        if preferences.get("job_titles"):
            lines.append(f"**Job Titles:** {', '.join(preferences['job_titles'])}")
            lines.append("")

        if preferences.get("job_types"):
            lines.append(f"**Job Types:** {', '.join(preferences['job_types'])}")
            lines.append("")

        if preferences.get("industries"):
            lines.append(f"**Industries:** {', '.join(preferences['industries'])}")
            lines.append("")

        if preferences.get("open_to_recruiters"):
            lines.append("**Open to Recruiters:** Yes")
            lines.append("")

        if preferences.get("dream_companies"):
            lines.append(
                f"**Dream Companies:** {', '.join(preferences['dream_companies'])}"
            )
            lines.append("")

        return "\n".join(lines)

    def _format_saved_job_answers(self, answers: list) -> str:
        """Format saved job answers section."""
        if not answers:
            return ""

        lines = ["# Saved Job Application Answers", ""]

        for answer in answers:
            question = answer.get("question", "")
            ans = answer.get("answer", "") or ""
            lines.append(f"**Q:** {question}")
            lines.append(f"**A:** {ans}")
            lines.append("")

        return "\n".join(lines)

    def _format_screening_responses(self, responses: list) -> str:
        """Format screening responses section."""
        if not responses:
            return ""

        lines = ["# Screening Question Responses", ""]

        for i, response in enumerate(responses, 1):
            lines.append(f"## Response {i}")
            for key, value in response.items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")

        return "\n".join(lines)

    def _format_saved_job_alerts(self, alerts: list) -> str:
        """Format saved job alerts section."""
        if not alerts:
            return ""

        lines = ["# Saved Job Alerts", ""]

        for alert in alerts:
            search_id = alert.get("search_id", "")
            query = alert.get("query_context", "") or ""
            lines.append(f"**Alert ID:** {search_id}")
            if query:
                lines.append(f"**Query:** {query}")
            lines.append("")

        return "\n".join(lines)

    def _format_search_queries(self, queries: list) -> str:
        """Format search queries section."""
        if not queries:
            return ""

        lines = ["# Search History", ""]
        lines.append("| Time | Query |")
        lines.append("|------|-------|")

        for q in queries:
            time = q.get("time", "")
            query = q.get("query", "")
            # Escape pipe characters in query
            query = query.replace("|", "\\|")
            lines.append(f"| {time} | {query} |")

        lines.append("")
        return "\n".join(lines)

    def _format_logins(self, logins: list) -> str:
        """Format logins section."""
        if not logins:
            return ""

        lines = ["# Login History", ""]
        lines.append("| Date | IP Address | Type |")
        lines.append("|------|------------|------|")

        for login in logins:
            date = login.get("date", "")
            ip = login.get("ip_address", "") or ""
            login_type = login.get("login_type", "") or ""
            lines.append(f"| {date} | {ip} | {login_type} |")

        lines.append("")
        return "\n".join(lines)

    def _format_security_challenges(self, challenges: list) -> str:
        """Format security challenges section."""
        if not challenges:
            return ""

        lines = ["# Security Challenges", ""]
        lines.append("| Date | IP Address | Country | Type |")
        lines.append("|------|------------|---------|------|")

        for c in challenges:
            date = c.get("date", "")
            ip = c.get("ip_address", "") or ""
            country = c.get("country", "") or ""
            ctype = c.get("challenge_type", "") or ""
            lines.append(f"| {date} | {ip} | {country} | {ctype} |")

        lines.append("")
        return "\n".join(lines)

    def _format_ads_clicked(self, ads: list) -> str:
        """Format ads clicked section."""
        if not ads:
            return ""

        lines = ["# Ads Clicked", ""]
        lines.append("| Date | Ad ID |")
        lines.append("|------|-------|")

        for ad in ads:
            date = ad.get("date", "")
            ad_id = ad.get("ad_id", "") or ""
            lines.append(f"| {date} | {ad_id} |")

        lines.append("")
        return "\n".join(lines)

    def _format_ad_targeting(self, targeting: dict | None) -> str:
        """Format ad targeting section."""
        if not targeting:
            return ""

        lines = ["# Ad Targeting Criteria", ""]

        for key, value in targeting.items():
            if value:
                # Format key nicely
                formatted_key = key.replace("_", " ").title()
                lines.append(f"**{formatted_key}:** {value}")
                lines.append("")

        return "\n".join(lines)

    def _format_lan_ads(self, ads: list) -> str:
        """Format LinkedIn Audience Network ads section."""
        if not ads:
            return ""

        lines = ["# LinkedIn Audience Network Ads", ""]
        lines.append("| Date | Action | Ad ID | Page/App |")
        lines.append("|------|--------|-------|----------|")

        for ad in ads:
            date = ad.get("date", "")
            action = ad.get("action", "") or ""
            ad_id = ad.get("ad_id", "") or ""
            page = ad.get("page_app", "") or ""
            lines.append(f"| {date} | {action} | {ad_id} | {page} |")

        lines.append("")
        return "\n".join(lines)

    def _format_inferences(self, inferences: list) -> str:
        """Format inferences section."""
        if not inferences:
            return ""

        lines = ["# LinkedIn's Inferences About You", ""]
        lines.append("| Category | Type | Description | Inference |")
        lines.append("|----------|------|-------------|-----------|")

        for inf in inferences:
            category = inf.get("category", "") or ""
            itype = inf.get("type", "") or ""
            desc = inf.get("description", "") or ""
            inference = inf.get("inference", "") or ""
            lines.append(f"| {category} | {itype} | {desc} | {inference} |")

        lines.append("")
        return "\n".join(lines)

    def _format_receipts(self, receipts: list) -> str:
        """Format receipts section."""
        if not receipts:
            return ""

        lines = ["# Payment Receipts", ""]
        lines.append("| Date | Description | Amount | Currency |")
        lines.append("|------|-------------|--------|----------|")

        for receipt in receipts:
            date = receipt.get("date", "") or ""
            desc = receipt.get("description", "") or ""
            amount = receipt.get("amount", "") or ""
            currency = receipt.get("currency", "") or ""
            lines.append(f"| {date} | {desc} | {amount} | {currency} |")

        lines.append("")
        return "\n".join(lines)

    def _format_service_engagements(self, engagements: list) -> str:
        """Format service engagements section."""
        if not engagements:
            return ""

        lines = ["# Service Marketplace Engagements", ""]
        lines.append("| Date | Type | Amount | Currency |")
        lines.append("|------|------|--------|----------|")

        for e in engagements:
            date = e.get("date", "") or ""
            mtype = e.get("marketplace_type", "") or ""
            amount = e.get("amount", "") or ""
            currency = e.get("currency", "") or ""
            lines.append(f"| {date} | {mtype} | {amount} | {currency} |")

        lines.append("")
        return "\n".join(lines)

    def _format_service_opportunities(self, opportunities: list) -> str:
        """Format service opportunities section."""
        if not opportunities:
            return ""

        lines = ["# Service Marketplace Opportunities", ""]

        for opp in opportunities:
            date = opp.get("date", "") or ""
            category = opp.get("category", "") or ""
            location = opp.get("location", "") or ""
            status = opp.get("status", "") or ""

            lines.append(f"## {category}")
            lines.append(f"**Date:** {date}")
            if location:
                lines.append(f"**Location:** {location}")
            if status:
                lines.append(f"**Status:** {status}")

            qa = opp.get("questions_answers", "")
            if qa:
                lines.append("")
                lines.append("**Details:**")
                lines.append(f"> {qa}")

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _format_verifications(self, verifications: list) -> str:
        """Format verifications section."""
        if not verifications:
            return ""

        lines = ["# Identity Verifications", ""]

        for v in verifications:
            name_parts = [
                v.get("first_name", ""),
                v.get("middle_name", ""),
                v.get("last_name", ""),
            ]
            name = " ".join(p for p in name_parts if p and p != "N/A")

            lines.append(f"## {name}")
            if v.get("verification_type"):
                lines.append(f"**Type:** {v['verification_type']}")
            if v.get("document_type"):
                lines.append(f"**Document:** {v['document_type']}")
            if v.get("provider"):
                lines.append(f"**Provider:** {v['provider']}")
            if v.get("verified_date"):
                lines.append(f"**Verified:** {v['verified_date']}")
            if v.get("expiry_date") and v.get("expiry_date") != "N/A":
                lines.append(f"**Expires:** {v['expiry_date']}")

            lines.append("")

        return "\n".join(lines)

    def _format_identity_assets(self, assets: list) -> str:
        """Format identity assets section."""
        if not assets:
            return ""

        lines = ["# Uploaded Documents", ""]

        for asset in assets:
            name = asset.get("name", "")
            has_content = asset.get("has_content", False)
            status = "(with content)" if has_content else "(no content)"
            lines.append(f"- {name} {status}")

        lines.append("")
        return "\n".join(lines)
