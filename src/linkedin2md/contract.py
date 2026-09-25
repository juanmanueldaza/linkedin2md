"""Declarative contract for supported LinkedIn export sections."""

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class SectionSpec:
    """Describe one parser input and its optional Markdown output."""

    key: str
    parser: str
    formatter: str | None
    source_keys: tuple[str, ...]
    output_file: str | None
    profile_component: bool = False

    @property
    def produces_output(self) -> bool:
        """Return whether this specification owns a standalone output."""
        return self.formatter is not None and self.output_file is not None


@dataclass(frozen=True)
class ConversionContract:
    """Define the stable conversion surface for a release line."""

    format_version: int
    default_language: str
    supported_languages: tuple[str, ...]
    output_extension: str
    output_encoding: str
    sections: tuple[SectionSpec, ...]
    profile_components: tuple[SectionSpec, ...]

    @property
    def parser_keys(self) -> tuple[str, ...]:
        """Return all registered parser section keys."""
        return tuple(
            spec.key
            for spec in (*self.profile_components, *self.sections)
            if not spec.key == "profile"
        )

    @property
    def formatter_keys(self) -> tuple[str, ...]:
        """Return all formatter section keys."""
        return tuple(spec.key for spec in self.sections if spec.produces_output)

    @property
    def output_files(self) -> tuple[str, ...]:
        """Return all declared Markdown output filenames."""
        return tuple(
            spec.output_file for spec in self.sections if spec.output_file is not None
        )

    def validate_registries(
        self,
        parser_keys: Iterable[str],
        formatter_keys: Iterable[str],
    ) -> None:
        """Raise when runtime registrations differ from the contract."""
        expected_parsers = set(self.parser_keys)
        expected_formatters = set(self.formatter_keys)
        actual_parsers = set(parser_keys)
        actual_formatters = set(formatter_keys)

        missing_parsers = sorted(expected_parsers - actual_parsers)
        extra_parsers = sorted(actual_parsers - expected_parsers)
        missing_formatters = sorted(expected_formatters - actual_formatters)
        extra_formatters = sorted(actual_formatters - expected_formatters)

        problems = []
        if missing_parsers:
            problems.append(f"missing parsers: {', '.join(missing_parsers)}")
        if extra_parsers:
            problems.append(f"unexpected parsers: {', '.join(extra_parsers)}")
        if missing_formatters:
            problems.append(f"missing formatters: {', '.join(missing_formatters)}")
        if extra_formatters:
            problems.append(f"unexpected formatters: {', '.join(extra_formatters)}")
        if problems:
            raise ValueError("Conversion contract mismatch: " + "; ".join(problems))


def _section(
    key: str,
    parser: str,
    formatter: str,
    *source_keys: str,
) -> SectionSpec:
    return SectionSpec(
        key=key,
        parser=parser,
        formatter=formatter,
        source_keys=source_keys,
        output_file=f"{key}.md",
    )


def _profile_component(
    key: str,
    parser: str,
    *source_keys: str,
) -> SectionSpec:
    return SectionSpec(
        key=key,
        parser=parser,
        formatter=None,
        source_keys=source_keys,
        output_file=None,
        profile_component=True,
    )


PROFILE_COMPONENTS = (
    _profile_component("name", "NameParser", "profile"),
    _profile_component("title", "TitleParser", "profile"),
    _profile_component("email", "EmailParser", "email_addresses"),
    _profile_component("phone", "PhoneParser", "phonenumbers"),
    _profile_component("location", "LocationParser", "profile"),
    _profile_component("summary", "SummaryParser", "profile"),
    _profile_component(
        "profile_meta",
        "ProfileMetaParser",
        "profile",
        "registration",
        "connections",
    ),
)

SECTION_SPECS = (
    _section(
        "profile",
        "composed",
        "ProfileFormatter",
        "profile",
        "email_addresses",
        "phonenumbers",
        "registration",
        "connections",
    ),
    _section("skills", "SkillsParser", "SkillsFormatter", "skills"),
    _section("experience", "ExperienceParser", "ExperienceFormatter", "positions"),
    _section("education", "EducationParser", "EducationFormatter", "education"),
    _section(
        "certifications",
        "CertificationsParser",
        "CertificationsFormatter",
        "certifications",
    ),
    _section("languages", "LanguagesParser", "LanguagesFormatter", "languages"),
    _section("projects", "ProjectsParser", "ProjectsFormatter", "projects"),
    _section(
        "recommendations",
        "RecommendationsParser",
        "RecommendationsFormatter",
        "recommendations_received",
    ),
    _section(
        "recommendations_given",
        "RecommendationsGivenParser",
        "RecommendationsGivenFormatter",
        "recommendations_given",
    ),
    _section(
        "endorsements",
        "EndorsementsParser",
        "EndorsementsFormatter",
        "endorsement_received_info",
    ),
    _section(
        "endorsements_given",
        "EndorsementsGivenParser",
        "EndorsementsGivenFormatter",
        "endorsement_given_info",
    ),
    _section("learning", "LearningParser", "LearningFormatter", "learning"),
    _section(
        "learning_reviews",
        "LearningReviewsParser",
        "LearningReviewsFormatter",
        "reviews",
    ),
    _section("connections", "ConnectionsParser", "ConnectionsFormatter", "connections"),
    _section(
        "companies_followed",
        "CompanyFollowsParser",
        "CompaniesFollowedFormatter",
        "company_follows",
    ),
    _section(
        "members_followed",
        "MemberFollowsParser",
        "MembersFollowedFormatter",
        "member_follows",
    ),
    _section(
        "invitations",
        "InvitationsParser",
        "InvitationsFormatter",
        "invitations",
    ),
    _section(
        "imported_contacts",
        "ImportedContactsParser",
        "ImportedContactsFormatter",
        "importedcontacts",
    ),
    _section("groups", "GroupsParser", "GroupsFormatter", "groups"),
    _section("posts", "PostsParser", "PostsFormatter", "shares"),
    _section("comments", "CommentsParser", "CommentsFormatter", "comments"),
    _section("reactions", "ReactionsParser", "ReactionsFormatter", "reactions"),
    _section("reposts", "RepostsParser", "RepostsFormatter", "instantreposts"),
    _section("votes", "VotesParser", "VotesFormatter", "votes"),
    _section(
        "saved_items",
        "SavedItemsParser",
        "SavedItemsFormatter",
        "saved_items",
    ),
    _section("events", "EventsParser", "EventsFormatter", "events"),
    _section("media", "MediaParser", "MediaFormatter", "rich_media"),
    _section("messages", "MessagesParser", "MessagesFormatter", "messages"),
    _section("scripts", "ScriptParser", "ScriptFormatter", "scripts"),
    _section("articles", "ArticlesParser", "ArticlesFormatter", "articles"),
    _section(
        "job_applications",
        "JobApplicationsParser",
        "JobApplicationsFormatter",
        "job_applications",
        "job_applications_1",
        "job_applications_2",
    ),
    _section(
        "job_descriptions",
        "JobDescriptionParser",
        "JobDescriptionFormatter",
        "job_descriptions",
        "job_descriptions_1",
        "job_descriptions_2",
        "job_applications",
        "job_applications_1",
        "job_applications_2",
    ),
    _section("saved_jobs", "SavedJobsParser", "SavedJobsFormatter", "saved_jobs"),
    _section(
        "job_preferences",
        "JobPreferencesParser",
        "JobPreferencesFormatter",
        "job_seeker_preferences",
    ),
    _section(
        "saved_job_answers",
        "SavedJobAnswersParser",
        "SavedJobAnswersFormatter",
        "job_applicant_saved_answers",
    ),
    _section(
        "screening_responses",
        "ScreeningResponsesParser",
        "ScreeningResponsesFormatter",
        "job_applicant_saved_screening_question_responses",
        "job_applicant_saved_screening_question_responses_1",
        "job_applicant_saved_screening_question_responses_2",
    ),
    _section(
        "saved_job_alerts",
        "SavedJobAlertsParser",
        "SavedJobAlertsFormatter",
        "savedjobalerts",
    ),
    _section(
        "search_queries",
        "SearchQueriesParser",
        "SearchQueriesFormatter",
        "searchqueries",
    ),
    _section("logins", "LoginsParser", "LoginsFormatter", "logins"),
    _section(
        "security_challenges",
        "SecurityChallengesParser",
        "SecurityChallengesFormatter",
        "security_challenges",
    ),
    _section(
        "ads_clicked",
        "AdsClickedParser",
        "AdsClickedFormatter",
        "ads_clicked",
    ),
    _section(
        "ad_targeting",
        "AdTargetingParser",
        "AdTargetingFormatter",
        "ad_targeting",
    ),
    _section(
        "lan_ads",
        "LanAdsParser",
        "LanAdsFormatter",
        "lan_ads_engagement",
        "linkedin_audience_network_ad_engagement",
    ),
    _section(
        "inferences",
        "InferencesParser",
        "InferencesFormatter",
        "inferences_about_you",
    ),
    _section(
        "receipts",
        "ReceiptsParser",
        "ReceiptsFormatter",
        "receipts",
        "receipts_v2",
    ),
    _section(
        "service_engagements",
        "ServiceEngagementsParser",
        "ServiceEngagementsFormatter",
        "engagements",
    ),
    _section(
        "service_opportunities",
        "ServiceOpportunitiesParser",
        "ServiceOpportunitiesFormatter",
        "opprtunities",
    ),
    _section(
        "verifications",
        "VerificationsParser",
        "VerificationsFormatter",
        "verifications",
    ),
    _section(
        "identity_assets",
        "IdentityAssetsParser",
        "IdentityAssetsFormatter",
        "private_identity_asset",
    ),
    _section("causes", "CausesParser", "CausesFormatter", "causes"),
    _section("interests", "InterestsParser", "InterestsFormatter", "interests"),
    _section("courses", "CoursesParser", "CoursesFormatter", "courses"),
    _section(
        "honors_awards",
        "HonorsAwardsParser",
        "HonorsAwardsFormatter",
        "honors_awards",
    ),
    _section(
        "test_scores",
        "TestScoresParser",
        "TestScoresFormatter",
        "test_scores",
    ),
    _section("patents", "PatentsParser", "PatentsFormatter", "patents"),
    _section(
        "organizations",
        "OrganizationsParser",
        "OrganizationsFormatter",
        "organizations",
    ),
    _section(
        "publications",
        "PublicationsParser",
        "PublicationsFormatter",
        "publications",
    ),
    _section(
        "volunteer_experience",
        "VolunteerExperienceParser",
        "VolunteerExperienceFormatter",
        "volunteer_experience",
    ),
    _section(
        "contact_settings",
        "ContactSettingsParser",
        "ContactSettingsFormatter",
        "contact_settings",
    ),
    _section(
        "data_export_history",
        "DataExportHistoryParser",
        "DataExportHistoryFormatter",
        "data_export_history",
    ),
    _section(
        "deletion_history",
        "DeletionHistoryParser",
        "DeletionHistoryFormatter",
        "deletion_history",
    ),
    _section(
        "who_viewed_profile",
        "WhoViewedProfileParser",
        "WhoViewedProfileFormatter",
        "who_viewed_profile",
    ),
    _section(
        "linkedin_salary",
        "LinkedInSalaryParser",
        "LinkedInSalaryFormatter",
        "linkedin_salary",
    ),
    _section(
        "profile_for_business",
        "ProfileForBusinessParser",
        "ProfileForBusinessFormatter",
        "profile_for_business",
    ),
    _section(
        "profile_summary",
        "ProfileSummaryParser",
        "ProfileSummaryFormatter",
        "profile_summary",
    ),
)

CONVERSION_CONTRACT = ConversionContract(
    format_version=1,
    default_language="en",
    supported_languages=("en", "es"),
    output_extension=".md",
    output_encoding="utf-8",
    sections=SECTION_SPECS,
    profile_components=PROFILE_COMPONENTS,
)
