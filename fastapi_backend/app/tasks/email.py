from pathlib import Path
from typing import List, Dict, Any, Optional
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.core.logging import logger
from app.tasks.worker import celery


# Cấu hình Jinja2 cho templates email
templates_path = Path(__file__).parent.parent / settings.TEMPLATE_DIR
template_env = Environment(
    loader=FileSystemLoader(templates_path),
    autoescape=True
)


def _send_email(
    to_email: str,
    subject: str,
    html_content: str,
    from_email: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
) -> bool:
    """
    Hàm nội bộ để gửi email
    """
    # Cấu hình email
    sender_email = from_email or settings.MAIL_FROM or "noreply@eduscan.vn"
    sender_name = settings.MAIL_FROM_NAME or "EduScan"
    
    # Tạo message
    message = MIMEMultipart()
    message["From"] = f"{sender_name} <{sender_email}>"
    message["To"] = to_email
    message["Subject"] = subject
    
    # Thêm nội dung HTML
    message.attach(MIMEText(html_content, "html"))
    
    # Thêm attachments nếu có
    if attachments:
        for attachment in attachments:
            attachment_part = MIMEText(attachment["content"], attachment.get("subtype", "plain"))
            attachment_part.add_header(
                "Content-Disposition",
                f"attachment; filename={attachment['filename']}"
            )
            message.attach(attachment_part)
    
    # Gửi email
    try:
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            if settings.MAIL_STARTTLS:
                server.starttls()
            
            if settings.MAIL_USERNAME and settings.MAIL_PASSWORD:
                server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            
            server.send_message(message)
            
        return True
    except Exception as e:
        logger.error(f"Lỗi khi gửi email: {e}")
        return False


@celery.task(
    name="app.tasks.email.send_email",
    max_retries=3,
    retry_backoff=True,
)
def send_email_task(
    to_email: str,
    subject: str,
    template_name: str,
    template_data: Dict[str, Any],
    from_email: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
) -> bool:
    """
    Task gửi email bất đồng bộ
    """
    try:
        # Tạo nội dung email từ template
        template = template_env.get_template(f"{template_name}.html")
        html_content = template.render(**template_data)
        
        # Gửi email
        return _send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            from_email=from_email,
            attachments=attachments,
        )
    except Exception as e:
        logger.error(f"Lỗi khi gửi email task: {e}")
        return False


@celery.task(name="app.tasks.email.send_welcome_email")
def send_welcome_email(user_id: int, email: str, name: str) -> bool:
    """
    Task gửi email chào mừng cho người dùng mới
    """
    return send_email_task(
        to_email=email,
        subject="Chào mừng bạn đến với EduScan",
        template_name="welcome",
        template_data={
            "name": name,
            "login_url": f"{settings.FRONTEND_URL}/login",
        },
    )


@celery.task(name="app.tasks.email.send_password_reset_email")
def send_password_reset_email(email: str, token: str) -> bool:
    """
    Task gửi email reset mật khẩu
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    return send_email_task(
        to_email=email,
        subject="Khôi phục mật khẩu EduScan",
        template_name="password_reset",
        template_data={
            "reset_url": reset_url,
            "valid_hours": 24,  # Token hết hạn sau 24 giờ
        },
    )


@celery.task(name="app.tasks.email.send_verification_email")
def send_verification_email(email: str, token: str) -> bool:
    """
    Task gửi email xác minh tài khoản
    """
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    return send_email_task(
        to_email=email,
        subject="Xác minh tài khoản EduScan",
        template_name="email_verification",
        template_data={
            "verify_url": verify_url,
            "valid_hours": 48,  # Token hết hạn sau 48 giờ
        },
    ) 