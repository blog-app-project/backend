import random

from faker import Faker

from blog_app.models import Post

fake = Faker()


def generate_posts():
    for _ in range(20):
        title = fake.text(30)
        status = random.choice(Post.Status.values)
        Post.objects.create(title=title, slug=fake.slug(title), author_id=1, body=fake.text(1000), status=status)


def generate_tags_for_existing_posts():
    tags = fake.words(10)
    for post in Post.objects.all():
        num_tags = random.randint(0, 3)
        post.tags.add(*random.sample(tags, k=num_tags))
