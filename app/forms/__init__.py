from app.forms.auth_forms import LoginForm, RegisterForm, ProfileForm
from app.forms.project_forms import ProjectSubmissionForm, ProjectReviewForm
from app.forms.content_forms import (
    ArticleForm, EventForm, OpportunityForm, TrainingCourseForm,
    PartnerForm, PageForm
)
from app.forms.admin_forms import (
    SiteSettingsForm, StrategicObjectiveForm, OrganizationalValueForm,
    NavigationItemForm, UserManagementForm
)
from app.forms.networking_forms import (
    NetworkingRequestForm, EventRegistrationForm, CourseEnrollmentForm,
    OpportunityApplicationForm
)

__all__ = [
    'LoginForm', 'RegisterForm', 'ProfileForm',
    'ProjectSubmissionForm', 'ProjectReviewForm',
    'ArticleForm', 'EventForm', 'OpportunityForm', 'TrainingCourseForm',
    'PartnerForm', 'PageForm',
    'SiteSettingsForm', 'StrategicObjectiveForm', 'OrganizationalValueForm',
    'NavigationItemForm', 'UserManagementForm',
    'NetworkingRequestForm', 'EventRegistrationForm', 'CourseEnrollmentForm',
    'OpportunityApplicationForm'
]
