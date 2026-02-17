from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

# --- Константы для выбора типа поста ---
ARTICLE = 'AR'
NEWS = 'NW'
TYPE_CHOICES = [
    (ARTICLE, _('Статья')),
    (NEWS,_('Новость'))
]

# --- 1. Модель Author ---
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

    class Meta:
        verbose_name = _('Автор')
        verbose_name_plural = _('Авторы')


# --- 2. Модель Category ---
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Category Name'))
    subscribers = models.ManyToManyField(User, related_name='categories', blank=True, verbose_name=_('Subscribers'))

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')

    def __str__(self):
        return self.name

# --- 3. Модель Post ---
class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name=_('Author'))
    post_type = models.CharField(max_length=2, choices=TYPE_CHOICES, default=ARTICLE, verbose_name=_('Type'))
    time_in = models.DateTimeField(auto_now_add=True, verbose_name=_('Time In'))
    category = models.ManyToManyField(Category, through='PostCategory', verbose_name=_('Category'))
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    text = models.TextField(verbose_name=_('Text'))
    rating = models.IntegerField(default=0, verbose_name=_('Rating'))

    class Meta:
        verbose_name = _('Пост')
        verbose_name_plural = _('Посты')

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return f'{self.text[:124]}...'

    def __str__(self):
        return f'{self.title} ({self.author.user.username})'

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'post-{self.pk}')


# --- 4. Модель PostCategory (Промежуточная таблица) ---
class PostCategory(models.Model):
    # Связь "один ко многим" с Post
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # Связь «один ко многим» с Category
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

# --- 5. Модель Comment ---
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name=_('Post'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    text = models.TextField(verbose_name=_('Comment Text'))
    time_in = models.DateTimeField(auto_now_add=True, verbose_name=_('Time Created'))
    rating = models.IntegerField(default=0, verbose_name=_('Rating'))

    class Meta:
        verbose_name = _('Комментарий')
        verbose_name_plural = _('Комментарии')

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f'{self.user.username}:{self.text[:50]}...'

class Article(models.Model):
    title=models.CharField(max_length=200)
    content=models.TextField()
    pub_date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title



