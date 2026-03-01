import dspy
from pydantic import BaseModel, Field


class GenerateOutreachEmail(dspy.Signature):
    startup_name: str = dspy.InputField()
    startup_description: str = dspy.InputField()
    founder_info: str = dspy.InputField()
    candidate_background: str = dspy.InputField()
    position_interest: str = dspy.InputField()
    
    email_subject: str = dspy.OutputField(desc="Professional email subject line")
    email_body: str = dspy.OutputField(desc="Personalized outreach email body")
    tone: str = dspy.OutputField(desc="Tone: professional, casual, or enthusiastic")


class GenerateLinkedInMessage(dspy.Signature):
    recipient_name: str = dspy.InputField()
    recipient_role: str = dspy.InputField()
    startup_name: str = dspy.InputField()
    candidate_background: str = dspy.InputField()
    
    message: str = dspy.OutputField(desc="LinkedIn connection message (under 300 chars)")
    value_proposition: str = dspy.OutputField(desc="Why they should connect")


class AssessTeamFit(dspy.Signature):
    candidate_skills: list[str] = dspy.InputField()
    candidate_experience: str = dspy.InputField()
    startup_tech_stack: list[str] = dspy.InputField()
    startup_stage: str = dspy.InputField()
    startup_needs: str = dspy.InputField()
    
    fit_score: float = dspy.OutputField(desc="Team fit score 0-100")
    matching_skills: list[str] = dspy.OutputField()
    gap_skills: list[str] = dspy.OutputField()
    recommended_role: str = dspy.OutputField()
    conversation_starters: list[str] = dspy.OutputField()


class GenerateDiscoveryNotification(dspy.Signature):
    startup_name: str = dspy.InputField()
    discovery_reason: str = dspy.InputField()
    why_notable: str = dspy.InputField()
    
    notification_title: str = dspy.OutputField()
    notification_message: str = dspy.OutputField()
    call_to_action: str = dspy.OutputField()


class CandidateProfile(BaseModel):
    name: str
    email: str
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    current_role: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience_years: int = 0
    education: str | None = None
    interests: list[str] = Field(default_factory=list)
    target_roles: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    seeking: list[str] = Field(default_factory=list)


class OutreachAgent(dspy.Module):
    def __init__(self, candidate: CandidateProfile):
        super().__init__()
        self.candidate = candidate
        self.email_generator = dspy.ChainOfThought(GenerateOutreachEmail)
        self.linkedin_generator = dspy.ChainOfThought(GenerateLinkedInMessage)
        self.fit_assessor = dspy.ChainOfThought(AssessTeamFit)
        self.notification_generator = dspy.ChainOfThought(GenerateDiscoveryNotification)
    
    def assess_fit(self, startup_data: dict) -> dict:
        result = self.fit_assessor(
            candidate_skills=self.candidate.skills,
            candidate_experience=f"{self.candidate.experience_years} years, {self.candidate.current_role}",
            startup_tech_stack=startup_data.get("tech_stack", []),
            startup_stage=startup_data.get("funding_stage", "unknown"),
            startup_needs=startup_data.get("hiring_signals", []),
        )
        return {
            "fit_score": result.fit_score,
            "matching_skills": result.matching_skills,
            "gap_skills": result.gap_skills,
            "recommended_role": result.recommended_role,
            "conversation_starters": result.conversation_starters,
        }
    
    def generate_email(self, startup_data: dict, position: str = "Software Engineer") -> dict:
        founder_info = startup_data.get("founders", [])
        founder_str = ", ".join([f.get("name", "") for f in founder_info])
        
        result = self.email_generator(
            startup_name=startup_data.get("name", "Startup"),
            startup_description=startup_data.get("description", ""),
            founder_info=founder_str,
            candidate_background=f"{self.candidate.name}, {self.candidate.current_role}",
            position_interest=position,
        )
        return {
            "subject": result.email_subject,
            "body": result.email_body,
            "tone": result.tone,
        }
    
    def generate_linkedin_message(self, recipient: dict) -> str:
        result = self.linkedin_generator(
            recipient_name=recipient.get("name", "Founder"),
            recipient_role=recipient.get("role", "Founder"),
            startup_name=recipient.get("company", "Startup"),
            candidate_background=self.candidate.name,
        )
        return result.message
    
    def generate_notification(self, startup_data: dict) -> dict:
        result = self.notification_generator(
            startup_name=startup_data.get("name", "Startup"),
            discovery_reason=startup_data.get("discovery_reason", "AI-detected growth signals"),
            why_notable=startup_data.get("why_notable", "Strong team and traction"),
        )
        return {
            "title": result.notification_title,
            "message": result.notification_message,
            "call_to_action": result.call_to_action,
        }
