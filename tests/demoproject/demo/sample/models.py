from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="books",
    )
    previous = models.OneToOneField(
        'Book',
        null=True,
        on_delete=models.SET_NULL,
        related_name="next",
    )

    def __str__(self):
        return self.name


class ChildrensBook(Book):
    max_age = models.PositiveIntegerField()


class Stats(models.Model):
    book = models.OneToOneField(
        Book,
        on_delete=models.CASCADE,
    )
    approve = models.PositiveIntegerField()
    disapprove = models.PositiveIntegerField()

    def __str__(self):
        return self.name
