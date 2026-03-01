from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import asyncio
import httpx
from bs4 import BeautifulSoup

from app.core import settings


@dataclass
class OutreachChannel:
    async def send_notification(self, startup_data: dict, message: dict) -> bool:
        raise NotImplementedError


@dataclass
class EmailOutreach(OutreachChannel):
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = field(default_factory=lambda: settings.email_sender)
    sender_password: str = field(default_factory=lambda: settings.email_password)
    
    async def send_notification(self, startup_data: dict, message: dict) -> bool:
        recipient_email = startup_data.get("contact_email") or startup_data.get("general_email")
        
        if not recipient_email:
            return False
        
        import aiosmtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = message.get("subject", "FinRadar: You've Been Discovered!")
        msg["From"] = self.sender_email
        msg["To"] = recipient_email
        
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 30px; text-align: center;">
              <h1 style="color: white; margin: 0;">🎉 Congratulations!</h1>
            </div>
            <div style="padding: 30px; background: #f9f9f9;">
              <h2 style="color: #333;">{startup_data.get('name', 'Your Team')} Has Been Discovered</h2>
              <p style="color: #666; line-height: 1.6;">
                {message.get('body', 'Our AI agent has identified your team as a high-potential startup.')}
              </p>
              <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;
                          box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h3 style="color: #667eea; margin-top: 0;">Why We Noticed You</h3>
                <p style="color: #333;">{message.get('reason', 'Strong growth signals and team composition.')}</p>
              </div>
              <p style="color: #666;">
                <strong>What this means:</strong> A qualified candidate using FinRadar has expressed 
                interest in connecting with teams like yours for potential opportunities 
                (internships, full-time roles, collaborations).
              </p>
              <p style="color: #666;">
                If you're interested, they may reach out directly. No action required from you.
              </p>
              <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
              <p style="color: #999; font-size: 12px;">
                This message was sent by FinRadar AI Agent. 
                To opt out of future notifications, reply with "UNSUBSCRIBE".
              </p>
            </div>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, "html"))
        
        try:
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.sender_email,
                password=self.sender_password,
                use_tls=True,
            )
            return True
        except Exception as e:
            print(f"Email send failed: {e}")
            return False


@dataclass
class LinkedInOutreach(OutreachChannel):
    async def send_notification(self, startup_data: dict, message: dict) -> bool:
        linkedin_url = startup_data.get("linkedin_url")
        
        if not linkedin_url:
            return False
        
        return True


@dataclass
class TwitterOutreach(OutreachChannel):
    async def send_notification(self, startup_data: dict, message: dict) -> bool:
        twitter_handle = startup_data.get("twitter_handle")
        
        if not twitter_handle:
            return False
        
        tweet_text = f"""
🚀 @{twitter_handle.replace('@', '')} - You've been discovered by FinRadar AI!

{message.get('short_message', 'Our AI identified your team as high-potential.')}

A qualified candidate may reach out soon. Good things coming! 🎉

#startups #hiring #FinRadar
        """.strip()
        
        return True


@dataclass
class SlackNotifier:
    webhook_url: str = field(default_factory=lambda: settings.slack_webhook_url)
    
    async def notify_user(
        self,
        startup_data: dict,
        fit_score: float,
        outreach_status: dict,
    ) -> bool:
        if not self.webhook_url:
            return False
        
        import httpx
        
        color = (
            "#36a64f" if fit_score >= 80
            else "#ff9900" if fit_score >= 60
            else "#cccccc"
        )
        
        payload = {
            "text": f"🎯 New Startup Discovered: {startup_data.get('name', 'Unknown')}",
            "attachments": [
                {
                    "color": color,
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": f"🔍 {startup_data.get('name', 'Startup')}",
                            }
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Fit Score:*\n{fit_score}/100",
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Stage:*\n{startup_data.get('funding_stage', 'N/A')}",
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Industry:*\n{startup_data.get('industry', 'N/A')}",
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Location:*\n{startup_data.get('location', 'N/A')}",
                                },
                            ]
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Description:*\n{startup_data.get('description', 'No description')[:300]}...",
                            }
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "📧 Send Email"},
                                    "url": f"mailto:{startup_data.get('contact_email', '')}",
                                    "style": "primary",
                                },
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "💼 LinkedIn"},
                                    "url": startup_data.get("linkedin_url", "#"),
                                },
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "🌐 Website"},
                                    "url": startup_data.get("website", "#"),
                                },
                            ]
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"📤 Outreach status: {outreach_status.get('status', 'pending')} | "
                                           f"✉️ Email: {'✅' if outreach_status.get('email_sent') else '❌'} | "
                                           f"🔔 Team notified: {'✅' if outreach_status.get('team_notified') else '❌'}",
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.webhook_url, json=payload)
            return resp.status_code == 200


@dataclass  
class NotificationManager:
    slack: SlackNotifier = field(default_factory=SlackNotifier)
    email: EmailOutreach = field(default_factory=EmailOutreach)
    linkedin: LinkedInOutreach = field(default_factory=LinkedInOutreach)
    twitter: TwitterOutreach = field(default_factory=TwitterOutreach)
    
    async def notify_startup(self, startup_data: dict, message: dict) -> dict:
        results = {}
        
        if startup_data.get("contact_email"):
            results["email_sent"] = await self.email.send_notification(startup_data, message)
        
        if startup_data.get("linkedin_url"):
            results["linkedin_ready"] = await self.linkedin.send_notification(startup_data, message)
        
        if startup_data.get("twitter_handle"):
            results["twitter_mentioned"] = await self.twitter.send_notification(startup_data, message)
        
        return results
    
    async def notify_user(
        self,
        startup_data: dict,
        fit_score: float,
        outreach_results: dict,
    ) -> bool:
        return await self.slack.notify_user(startup_data, fit_score, outreach_results)
