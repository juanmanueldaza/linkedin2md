"""Job-related section parsers.

Each parser handles ONE section (SRP).
"""

from linkedin2md.parsers.base import BaseParser
from linkedin2md.registry import register_parser


@register_parser
class JobApplicationsParser(BaseParser):
    """Parse job applications from all split files."""

    @property
    def section_key(self) -> str:
        return "job_applications"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        apps = self._merge_csv_sources(
            raw_data,
            ["job_applications", "job_applications_1", "job_applications_2"],
        )
        result = []

        for a in apps:
            date = a.get("Application Date", "")
            company = a.get("Company Name", "")
            title = a.get("Job Title", "")

            if not company and not title:
                continue

            entry = {
                "date": date,
                "company": company,
                "title": title,
                "url": a.get("Job Url", "") or None,
                "resume_used": a.get("Resume Name", "") or None,
                "contact_email": a.get("Contact Email", "") or None,
                "contact_phone": a.get("Contact Phone Number", "") or None,
                "questions_answers": a.get("Question And Answers", "") or None,
            }
            result.append(entry)

        return result


@register_parser
class SavedJobsParser(BaseParser):
    """Parse saved jobs."""

    @property
    def section_key(self) -> str:
        return "saved_jobs"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        jobs = self._get_csv(raw_data, "saved_jobs")
        result = []

        for j in jobs:
            date = j.get("Saved Date", "")
            company = j.get("Company Name", "")
            title = j.get("Job Title", "")

            if not company and not title:
                continue

            entry = {
                "date": date,
                "company": company,
                "title": title,
                "url": j.get("Job Url", "") or None,
            }
            result.append(entry)

        return result


@register_parser
class JobPreferencesParser(BaseParser):
    """Parse job seeker preferences."""

    @property
    def section_key(self) -> str:
        return "job_preferences"

    def parse(self, raw_data: dict[str, list[dict]]) -> dict | None:
        prefs = self._get_csv(raw_data, "job_seeker_preferences")
        if not prefs:
            return None

        p = prefs[0]

        def split_field(val: str) -> list[str]:
            if not val:
                return []
            return [x.strip() for x in val.split("|") if x.strip()]

        return {
            "locations": split_field(p.get("Locations", "")),
            "industries": split_field(p.get("Industries", "")),
            "job_types": split_field(p.get("Preferred Job Types", "")),
            "job_titles": split_field(p.get("Job Titles", "")),
            "open_to_recruiters": p.get("Open To Recruiters", "").lower() == "yes",
            "dream_companies": split_field(p.get("Dream Companies", "")),
            "profile_shared": p.get("Profile Shared With Job Poster", "").lower()
            == "yes",
            "intro_statement": p.get("Introduction Statement", "") or None,
            "phone": p.get("Phone Number", "") or None,
        }


@register_parser
class SavedJobAnswersParser(BaseParser):
    """Parse saved job application answers."""

    @property
    def section_key(self) -> str:
        return "saved_job_answers"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        answers = self._get_csv(raw_data, "job_applicant_saved_answers")
        result = []

        for a in answers:
            question = a.get("Question", "")
            answer = a.get("Answer", "")

            if not question:
                continue

            entry = {
                "question": question,
                "answer": answer or None,
            }
            result.append(entry)

        return result


@register_parser
class ScreeningResponsesParser(BaseParser):
    """Parse screening question responses from all files."""

    @property
    def section_key(self) -> str:
        return "screening_responses"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        responses = self._merge_csv_sources(
            raw_data,
            [
                "job_applicant_saved_screening_question_responses",
                "job_applicant_saved_screening_question_responses_1",
                "job_applicant_saved_screening_question_responses_2",
            ],
        )
        result = []

        for r in responses:
            entry = {}
            for field_key, field_value in r.items():
                if field_value:
                    normalized_key = field_key.lower().replace(" ", "_")
                    entry[normalized_key] = field_value

            if entry:
                result.append(entry)

        return result


@register_parser
class SavedJobAlertsParser(BaseParser):
    """Parse saved job alerts."""

    @property
    def section_key(self) -> str:
        return "saved_job_alerts"

    def parse(self, raw_data: dict[str, list[dict]]) -> list[dict]:
        alerts = self._get_csv(raw_data, "savedjobalerts")
        result = []

        for a in alerts:
            search_id = a.get("SAVED_SEARCH_ID", "")

            entry = {
                "search_id": search_id or None,
                "parameters": a.get("ALERT_PARAMETERS", "") or None,
                "query_context": a.get("QUERY_CONTEXT", "") or None,
            }
            result.append(entry)

        return result
