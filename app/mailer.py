import logging
import smtplib
from email.mime.text import MIMEText

from sqlalchemy.orm import Session

from .crud import mark_person_emailed

logger = logging.getLogger(__name__)


def send_email(email: str, name: str, message, db: Session):
    msg = MIMEText(message)
    msg["Subject"] = name
    msg["From"] = "josh@reach.com"
    msg["To"] = email
    with smtplib.SMTP(host="localhost", port=8025) as s:
        try:
            s.sendmail("jsoh@reach.com", [email], msg.as_string())
            logger.info("Recipient reached at {}".format(email))
        except smtplib.SMTPRecipientsRefused:
            logger.error("Recipient refused at {}".format(email))
    mark_person_emailed(db, email)
