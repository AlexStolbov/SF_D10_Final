from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from .models import Post, Category
from .services.mail_sending import send_news_to_subscribers


@shared_task
def send_mail_to_subscriber(post_id: int, cat_added_id: list, subject: str):
    """
    Отправка эл.письма, о появлении новой статьи в заданных категориях.
    """
    domain = settings.CURRENT_HOST
    post = Post.objects.get(pk=post_id)

    # debug
    print(f'-send_mail_to_subscriber------ start: {post}')

    for category in Category.objects.filter(pk__in=cat_added_id):
        for current_user in category.subscribers.all():
            # debug
            print(f'--send_mail_to_subscriber------ post: {post} domain: {domain}')

            html_content = render_to_string(
                'news_create_email.html',
                {
                    'post': post,
                    'domain': domain,
                }
            ) + f'\nЗдравствуй, {current_user.username}. Новая статья в твоём любимом разделе: {category.name}';

            msg = EmailMultiAlternatives(
                subject=subject,
                body='',
                from_email='',
                to=[current_user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()


@shared_task
def scheduler_send_news():
    send_news_to_subscribers()
