from datetime import datetime, timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from ..models import Category, Post


def send_news_to_subscribers():
    """
    Если пользователь подписан на какую-либо категорию, то каждую неделю ему приходит
    на почту список новых статей, появившийся за неделю с гиперссылкой на них,
    чтобы пользователь мог перейти и прочесть любую из статей.
    """
    for category in Category.objects.all():
        today = datetime.now()
        start = datetime(today.year, today.month, today.day - 7, tzinfo=timezone.utc)
        finish = datetime(today.year, today.month, today.day, 23, 59, 59, 999999, tzinfo=timezone.utc)
        posted_last_weeks = Post.objects.filter(created__range=[start, finish]).filter(category=category)

        if posted_last_weeks:

            subject = f'News of last week of {category}'

            domain = settings.CURRENT_HOST

            for current_user in category.subscribers.all():
                print(f'send email of cat {category} to user {current_user}')

                html_content = render_to_string(
                    'news_last_week_to_subscr.html',
                    {
                        'posted': posted_last_weeks,
                        'domain': domain,
                    }
                )
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body='',
                    from_email='',
                    to=[current_user.email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
