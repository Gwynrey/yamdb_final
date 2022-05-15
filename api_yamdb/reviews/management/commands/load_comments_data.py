import csv

from django.core.management.base import BaseCommand, CommandError

from reviews.models import Comment, Review
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Add csv files to Django Models.'

    def handle(self, *args, **kwargs):
        try:
            with open(
                'comments.csv',
                newline='',
                encoding='utf-8'
            ) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                next(spamreader)
                for row in spamreader:
                    if (Review.objects.filter(pk=int(row[1]))
                            and CustomUser.objects.filter(pk=int(row[3]))):
                        Comment.objects.update_or_create(
                            review=Review.objects.get(pk=int(row[1])),
                            text=row[2],
                            author=CustomUser.objects.get(pk=int(row[3])),
                            pub_date=row[4]
                        )
                self.stdout.write(self.style.SUCCESS('Comments записан.'))
        except FileNotFoundError:
            raise CommandError("Неудалось открыть файл comments.csv.")
        except Exception:
            raise CommandError("Неудалось записать модель Comments.")
