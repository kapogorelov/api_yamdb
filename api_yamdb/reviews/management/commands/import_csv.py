import csv
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

# Порядок важен: сначала таблицы, на которые ссылаются другие.
# (имя файла, модель в формате 'app_label.ModelName' или None для User)
CSV_FILES = (
    ('users.csv', None),
    ('category.csv', 'reviews.Category'),
    ('genre.csv', 'reviews.Genre'),
    ('titles.csv', 'reviews.Title'),
    ('genre_title.csv', 'reviews.GenreTitle'),
    ('review.csv', 'reviews.Review'),
    ('comments.csv', 'reviews.Comment'),
)


class Command(BaseCommand):
    help = (
        'Загружает данные из CSV-файлов (по умолчанию static/data) в БД. '
        'Повторный запуск не создаёт дублей: записи обновляются по id.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            default=str(Path(settings.BASE_DIR) / 'static' / 'data'),
            help='Папка с CSV-файлами.',
        )

    def handle(self, *args, **options):
        data_dir = Path(options['path'])
        if not data_dir.is_dir():
            raise CommandError(f'Папка {data_dir} не найдена.')

        for filename, model_label in CSV_FILES:
            model = self.get_model(model_label)
            if model is None:
                self.stdout.write(self.style.WARNING(
                    f'{filename}: модель {model_label} ещё не создана, '
                    'пропускаю.'
                ))
                continue
            file_path = data_dir / filename
            if not file_path.exists():
                self.stdout.write(self.style.WARNING(
                    f'{filename}: файл не найден, пропускаю.'
                ))
                continue
            self.import_file(file_path, model)

        self.stdout.write(self.style.SUCCESS('Импорт завершён.'))

    @staticmethod
    def get_model(model_label):
        if model_label is None:
            return get_user_model()
        try:
            return apps.get_model(model_label)
        except LookupError:
            return None

    @staticmethod
    def build_column_map(model, columns):
        """Сопоставляет колонки CSV с полями модели.

        Колонка `category` для ForeignKey превращается в `category_id`,
        `author` — в `author_id` и т.д. Неизвестные колонки пропускаются.
        """
        fields = {}
        for field in model._meta.concrete_fields:
            fields[field.name] = field
            fields[field.attname] = field
        return {
            column: fields[column]
            for column in columns
            if column != 'id' and column in fields
        }

    @staticmethod
    def clean_value(field, value):
        if value != '':
            return value
        # Пустая ячейка: NULL, если поле допускает, иначе пустая строка.
        return None if field.null else ''

    def import_file(self, file_path, model):
        with open(file_path, encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            column_map = self.build_column_map(model, reader.fieldnames)
            created = updated = failed = 0
            for line_number, row in enumerate(reader, start=2):
                values = {
                    field.attname: self.clean_value(field, row[column])
                    for column, field in column_map.items()
                }
                try:
                    with transaction.atomic():
                        _, is_created = model.objects.update_or_create(
                            pk=row['id'], defaults=values
                        )
                        # update() не трогает auto_now_add, поэтому даты
                        # (pub_date) сохранятся такими, как в CSV.
                        model.objects.filter(pk=row['id']).update(**values)
                except (IntegrityError, ValueError, ValidationError) as error:
                    failed += 1
                    self.stdout.write(self.style.ERROR(
                        f'{file_path.name}, строка {line_number}: {error}'
                    ))
                    continue
                if is_created:
                    created += 1
                else:
                    updated += 1
        self.stdout.write(
            f'{file_path.name}: создано {created}, обновлено {updated}, '
            f'с ошибками {failed}.'
        )
