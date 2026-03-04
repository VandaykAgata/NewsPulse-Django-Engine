from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from .ai_logic import analyze_article_ai

# --- Константы ---
ARTICLE = 'AR'
NEWS = 'NW'
TYPE_CHOICES = [
    (ARTICLE, _('Статья')),
    (NEWS, _('Новость'))
]


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('User'))
    rating = models.IntegerField(default=0, verbose_name=_('Rating'))

    def update_rating(self):
        posts_rating = self.post_set.aggregate(pr=Sum('rating')).get('pr', 0) * 3
        author_comments_rating = self.user.comment_set.aggregate(acr=Sum('rating')).get('acr', 0)
        posts_comments_rating = Comment.objects.filter(post__author=self).aggregate(pcr=Sum('rating')).get('pcr', 0)
        self.rating = posts_rating + author_comments_rating + posts_comments_rating
        self.save()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Category Name'))
    subscribers = models.ManyToManyField(User, related_name='categories', blank=True, verbose_name=_('Subscribers'))

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name=_('Author'))
    post_type = models.CharField(max_length=2, choices=TYPE_CHOICES, default=ARTICLE, verbose_name=_('Type'))
    time_in = models.DateTimeField(auto_now_add=True, verbose_name=_('Time In'))
    category = models.ManyToManyField(Category, through='PostCategory', verbose_name=_('Category'))
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    text = models.TextField(verbose_name=_('Text'))
    rating = models.IntegerField(default=0, verbose_name=_('Rating'))

    def save(self, *args, **kwargs):
        print(f"--- DEBUG: Saving post '{self.title}' ---")
        if not self.ai_summary:
            print("--- DEBUG: Calling AI... ---")
            ai_data = analyze_article_ai(self.title, self.text)

    # --- НОВЫЕ ПОЛЯ ДЛЯ ИИ ---
    ai_summary = models.TextField(blank=True, verbose_name=_('AI Summary'))
    ai_sentiment = models.CharField(max_length=20, blank=True, verbose_name=_('AI Sentiment'))
    ai_category_label = models.CharField(max_length=50, blank=True, verbose_name=_('AI Category'))

    class Meta:
        verbose_name = _('Пост')
        verbose_name_plural = _('Посты')

    def preview(self):
        return f'{self.text[:124]}...'

    def __str__(self):
        return f'{self.title} ({self.author.user.username})'

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    # --- УМНЫЙ МЕТОД SAVE ---
    def save(self, *args, **kwargs):
        # Если это новый пост и поля ИИ пустые — запрашиваем анализ
        if not self.ai_summary:
            ai_data = analyze_article_ai(self.title, self.text)
            self.ai_summary = ai_data.get('summary', '')
            self.ai_sentiment = ai_data.get('sentiment', 'нейтральная')
            self.ai_category_label = ai_data.get('category', 'другое')

        super().save(*args, **kwargs)
        cache.delete(f'post-{self.pk}')


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    time_in = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)