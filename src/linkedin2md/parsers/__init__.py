"""Section parsers package.

Each parser handles ONE section (Single Responsibility Principle).
Parsers are registered via decorators (Open/Closed Principle).
"""

from linkedin2md.parsers.activity import (
    LoginsParser,
    SearchQueriesParser,
    SecurityChallengesParser,
)
from linkedin2md.parsers.advertising import (
    AdsClickedParser,
    AdTargetingParser,
    InferencesParser,
    LanAdsParser,
)
from linkedin2md.parsers.base import BaseParser
from linkedin2md.parsers.content import (
    CommentsParser,
    EventsParser,
    MediaParser,
    MessagesParser,
    PostsParser,
    ReactionsParser,
    RepostsParser,
    SavedItemsParser,
    VotesParser,
)
from linkedin2md.parsers.identity import (
    IdentityAssetsParser,
    VerificationsParser,
)
from linkedin2md.parsers.jobs import (
    JobApplicationsParser,
    JobPreferencesParser,
    SavedJobAlertsParser,
    SavedJobAnswersParser,
    SavedJobsParser,
    ScreeningResponsesParser,
)
from linkedin2md.parsers.learning import (
    LearningParser,
    LearningReviewsParser,
)
from linkedin2md.parsers.network import (
    CompanyFollowsParser,
    ConnectionsParser,
    ImportedContactsParser,
    InvitationsParser,
    MemberFollowsParser,
)
from linkedin2md.parsers.payments import ReceiptsParser
from linkedin2md.parsers.professional import (
    CertificationsParser,
    EducationParser,
    ExperienceParser,
    LanguagesParser,
    ProjectsParser,
    SkillsParser,
)
from linkedin2md.parsers.profile import (
    EmailParser,
    LocationParser,
    NameParser,
    PhoneParser,
    ProfileMetaParser,
    SummaryParser,
    TitleParser,
)
from linkedin2md.parsers.recommendations import (
    EndorsementsGivenParser,
    EndorsementsParser,
    RecommendationsGivenParser,
    RecommendationsParser,
)
from linkedin2md.parsers.services import (
    ServiceEngagementsParser,
    ServiceOpportunitiesParser,
)

__all__ = [
    "BaseParser",
    # Profile
    "NameParser",
    "TitleParser",
    "EmailParser",
    "PhoneParser",
    "LocationParser",
    "SummaryParser",
    "ProfileMetaParser",
    # Professional
    "SkillsParser",
    "ExperienceParser",
    "EducationParser",
    "CertificationsParser",
    "LanguagesParser",
    "ProjectsParser",
    # Recommendations
    "RecommendationsParser",
    "RecommendationsGivenParser",
    "EndorsementsParser",
    "EndorsementsGivenParser",
    # Learning
    "LearningParser",
    "LearningReviewsParser",
    # Network
    "ConnectionsParser",
    "CompanyFollowsParser",
    "MemberFollowsParser",
    "InvitationsParser",
    "ImportedContactsParser",
    # Content
    "PostsParser",
    "CommentsParser",
    "ReactionsParser",
    "RepostsParser",
    "VotesParser",
    "SavedItemsParser",
    "EventsParser",
    "MediaParser",
    "MessagesParser",
    # Jobs
    "JobApplicationsParser",
    "SavedJobsParser",
    "JobPreferencesParser",
    "SavedJobAnswersParser",
    "ScreeningResponsesParser",
    "SavedJobAlertsParser",
    # Activity
    "SearchQueriesParser",
    "LoginsParser",
    "SecurityChallengesParser",
    # Advertising
    "AdsClickedParser",
    "AdTargetingParser",
    "LanAdsParser",
    "InferencesParser",
    # Payments
    "ReceiptsParser",
    # Services
    "ServiceEngagementsParser",
    "ServiceOpportunitiesParser",
    # Identity
    "VerificationsParser",
    "IdentityAssetsParser",
]
