import csv

from django.core.management.base import BaseCommand, CommandError

from reviews.models import Category


class Command(BaseCommand):
    help = 'Add csv files to Django Models.'

    def handle(self, *args, **kwargs):
        try:
            with open(
                'category.csv',
                newline='',
                encoding='utf-8'
            ) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                next(spamreader)
                for row in spamreader:
                    if not Category.objects.filter(slug=row[2]):
                        Category.objects.update_or_create(
                            name=row[1],
                            slug=row[2]
                        )
                self.stdout.write(self.style.SUCCESS('Category записан.'))
        except FileNotFoundError:
            raise CommandError("Неудалось открыть файл category.csv.")
        except Exception:
            raise CommandError("Неудалось записать модель Category.")
