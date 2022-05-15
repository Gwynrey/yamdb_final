import csv

from django.core.management.base import BaseCommand, CommandError

from reviews.models import Category, Title


class Command(BaseCommand):
    help = 'Add csv files to Django Models.'

    def handle(self, *args, **kwargs):
        try:
            with open(
                'titles.csv',
                newline='',
                encoding='utf-8'
            ) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                next(spamreader)
                for row in spamreader:
                    if Category.objects.filter(pk=int(row[3])):
                        Title.objects.update_or_create(
                            name=row[1],
                            year=row[2],
                            category=Category.objects.get(pk=int(row[3]))
                        )
                self.stdout.write(self.style.SUCCESS('Titles записан.'))
        except FileNotFoundError:
            raise CommandError("Неудалось открыть файл Titles.csv.")
        except Exception:
            raise CommandError("Неудалось записать модель Titles.")
