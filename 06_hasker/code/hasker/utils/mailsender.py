import re
import logging
from django.core.mail import send_mail
from django.conf import settings


class MailSender():
    @staticmethod
    def send(email, alias, context):
        logger = logging.getLogger(__name__)
        if settings.EMAIL_ENABLE:
            try:
                msg = settings.EMAIL_MESSAGES[alias]
                subject = msg[0]
                message = Mailer.replace_context(msg[1], context) + settings.EMAIL_SIGN
                send_mail(subject, message=' ', html_message=message,
                    from_email=settings.EMAIL_FROM, recipient_list=[email],
                    fail_silently=False,
                )
                return message
            except Exception as err:
                logger.error("Error: %s", err)
        else:
            logger.info("Mail sender not enable")

    @staticmethod
    def replace_context(msg, context):
        if isinstance(context, dict):
            for key in context.keys():
                tag = '<%' + str(key).upper() + '%>'
                msg = re.sub(tag, context[key], msg)

        return msg

