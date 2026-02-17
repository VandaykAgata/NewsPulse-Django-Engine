import datetime  # Изменили импорт, чтобы работала timedelta
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from celery import shared_task
from .models import Post, Category


@shared_task
def weekly_newsletter_task():
    today = timezone.now()
    # Правильный вызов через datetime.timedelta
    last_week = today - datetime.timedelta(days=7)
    posts = Post.objects.filter(time_in__gte=last_week)

    if not posts.exists():
        return

    # Собираем email тех, кто подписан на категории этих постов
    subscribers_emails = set(
        Category.objects.filter(posts__in=posts)
        .values_list('subscribers__email', flat=True)
    )

    for email in subscribers_emails:
        if not email:
            continue

        user_posts = posts.filter(category__subscribers__email=email).distinct()

        html_content = render_to_string(
            'news/daily_post.html',
            {
                'link': settings.SITE_URL,
                'posts': user_posts,
            }
        )

        msg = EmailMultiAlternatives(
            subject='Статьи за неделю',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()


@shared_task
def send_notifications_task(pk):
    # Питонический подход: передаем только ID, а данные берем из базы сами
    # Это защищает от ситуации, когда данные поста изменились, пока задача лежала в очереди
    post = Post.objects.get(pk=pk)
    categories = post.category.all()
    subscribers_emails = set()

    for cat in categories:
        subscribers_emails.update(cat.subscribers.values_list('email', flat=True))

    for email in subscribers_emails:
        html_content = render_to_string(
            'account/email/new_post_notification.html',
            {
                'text': post.preview(),
                'link': f'{settings.SITE_URL}/{pk}'
            }
        )
        msg = EmailMultiAlternatives(
            subject=post.title,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()