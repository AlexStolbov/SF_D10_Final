from datetime import datetime
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver  # импортируем нужный декоратор
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import Post
from .tasks import send_mail_to_subscriber


@receiver(m2m_changed, sender=Post.category.through)
def notify_of_post(sender, instance, action, **kwargs):
    """
    При создании новости подписчикам этой категории автоматически отправляется сообщение о пополнении в разделе.
    """

    # debug
    print(f'-notify_of_post------ start: {instance}')
    if action == 'pre_add':
        # Новые категории для статьи.
        cat_added_id = kwargs.get('pk_set')

        post_description = f' {instance.title} {instance.created.strftime("%d %m %Y")}'
        subject = f'Post changed for {post_description}'
        send_mail_to_subscriber.delay(instance.id, list(cat_added_id), subject)


@receiver(pre_save, sender=Post)
def control_of_post(sender, instance, **kwargs):
    """
    Один пользователь не может публиковать более трёх новостей в сутки
    """
    today = datetime.now()
    start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    finish = datetime(today.year, today.month, today.day, 23, 59, 59, 999999, tzinfo=timezone.utc)

    posted_today = Post.objects.filter(author=instance.author).filter(created__range=[start, finish])

    if len(posted_today) >= 3:
        # ToDo попытаться не выбрасывать исключение, а отменить запись
        raise ValueError('Не более 3 новостей в день')


@receiver(post_save, sender=User)
def new_user_greetings(sender, instance: User, created, **kwargs):
    if created:
        send_mail(
            subject=f'Приветствуем на портале новостей  {instance.username}',
            message='',
            from_email='',
            recipient_list=[instance.email]
        )
