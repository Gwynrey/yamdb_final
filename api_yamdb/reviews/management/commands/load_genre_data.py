import csv

from django.core.management.base import BaseCommand, CommandError

from reviews.models import Genre


class Command(BaseCommand):
    help = 'Add csv files to Django Models.'

    def handle(self, *args, **kwargs):
        try:
            with open(
                'genre.csv',
                newline='',
                encoding='utf-8'
            ) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                next(spamreader)
                for row in spamreader:
                    if not Genre.objects.filter(slug=row[2]):
                        Genre.objects.update_or_create(
                            name=row[1],
                            slug=row[2]
                        )
                self.stdout.write(self.style.SUCCESS('Genres записан.'))
        except FileNotFoundError:
            raise CommandError("Неудалось открыть файл Genre.csv.")
        except Exception:
            raise CommandError("Неудалось записать модель Genres.")
