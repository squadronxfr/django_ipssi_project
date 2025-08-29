import logging
from typing import Optional, List, Mapping, Union, Sequence
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_templated_email(
        subject: str,
        to_emails: Union[str, Sequence[str]],
        template_txt: str,
        context: Optional[Mapping] = None,
        html_template: Optional[str] = None,
        from_email: Optional[str] = None,
) -> bool:
    context = context or {}
    recipients: List[str] = [to_emails] if isinstance(to_emails, str) else list(to_emails)

    try:
        body_text = render_to_string(template_txt, context)
    except Exception as e:
        logger.error("Echec rendu template texte '%s': %s", template_txt, e, exc_info=True)
        return False

    try:
        message = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            to=recipients,
            from_email=from_email
        )

        if html_template:
            try:
                body_html = render_to_string(html_template, context)
                message.attach_alternative(body_html, "text/html")
            except Exception as e:
                logger.info("Template HTML '%s' introuvable ou erreur: %s", html_template, e)

        message.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error("Echec envoi email vers %s: %s", ", ".join(recipients), e, exc_info=True)
        return False


def send_welcome_email(user, extra_context: Optional[Mapping] = None) -> bool:
    context = {
        "user": user,
        "first_name": user.first_name or user.username,
        "last_name": user.last_name,
        "username": user.username,
        "email": user.email,
        "site_name": "RH System",
        "login_url": "/login/",
    }
    if extra_context:
        context.update(extra_context)

    return send_templated_email(
        subject="Bienvenue sur RH System",
        to_emails=user.email or [],
        template_txt="accounts/emails/welcome_email.txt",
        context=context,
        html_template="accounts/emails/welcome_email.html",
    )