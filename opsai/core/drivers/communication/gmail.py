import os
import smtplib
import ssl
import hashlib
import aiosmtplib
from jinja2 import Template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from ..base import BaseDriver

class GmailDriver(BaseDriver):
    """
    Driver for sending emails via Gmail SMTP.
    Requires OPSAI_DRIVER_GMAIL_USER and OPSAI_DRIVER_GMAIL_PASS.
    """
    
    def __init__(self) -> None:
        self.smtp_server = "smtp.gmail.com"
        self.port = 465 # For SSL
        self.username: str | None = os.getenv("OPSAI_DRIVER_GMAIL_USER")
        self.password: str | None = os.getenv("OPSAI_DRIVER_GMAIL_PASS")

    def check_health(self) -> bool:
        """
        Verifies SMTP connection and authentication.
        """
        if not self.username or not self.password:
            return False
            
        try:
            context: ssl.SSLContext = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server: smtplib.SMTP_SSL:
                server.login(self.username, self.password)
            return True
        except Exception:
            return False

    async def execute(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends an email using the provided payload.
        """
        payload = step_data.get("payload", {})
        to_email = payload.get("to")
        subject = payload.get("subject", "OpsAI Notification")
        raw_body = payload.get("body", "")
        
        # JINJA2 TEMPLATING (New in Phase 3)
        try:
            template = Template(raw_body)
            # Use the payload itself or specific context as template variables
            body = template.render(**payload)
        except Exception:
            # Fallback to raw body if template fails
            body = raw_body

        if not to_email:
            return {
                "status": "FAILED",
                "is_recoverable": False,
                "error": "Missing 'to' email address in payload"
            }

        try:
            message = MIMEMultipart()
            message["From"] = self.username
            message["To"] = to_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))

            # Use aiosmtplib for non-blocking SMTP dispatch
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.port,
                username=self.username,
                password=self.password,
                use_tls=True
            )

            return {
                "status": "SUCCESS",
                "is_recoverable": False,
                "result": {"provider": "Gmail", "to": to_email, "subject": subject}
            }

        except smtplib.SMTPAuthenticationError:
            return {"status": "FAILED", "is_recoverable": False, "error": "Invalid Gmail Credentials"}
        except Exception as e: Exception:
            return {"status": "FAILED", "is_recoverable": True, "error": str(e)}

    def sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redacts recipient emails and sensitive metadata from audit logs.
        """
        if "to" in data:
            # Hash the email for consistency in audit logs without leaking PII
            email_hash: str = hashlib.sha256(data["to"].encode()).hexdigest()[:12]
            data["to"] = f"REDACTED_{email_hash}@domain.com"
        
        return data
