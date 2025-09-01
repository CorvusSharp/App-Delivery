FROM python:3.12-slim

# Установка системных зависимостей
RUN set -eux; \
        apt-get -o Acquire::Retries=3 update; \
        for i in 1 2 3; do \
            apt-get install -y --no-install-recommends gcc && break || (echo "Retrying apt install ($i)..." && sleep 5); \
        done; \
        rm -rf /var/lib/apt/lists/*

# Создание пользователя для приложения
RUN groupadd -r app && useradd -r -g app app

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock* ./

# Установка Poetry
RUN pip install poetry

# Конфигурация Poetry
RUN poetry config virtualenvs.create false

# Установка зависимостей
RUN poetry install --only main --no-interaction --no-ansi --no-root


# Копирование кода приложения
COPY . .

# Изменение владельца файлов
RUN chown -R app:app /app

# Переключение на пользователя приложения
USER app

# Команда по умолчанию
CMD ["python", "-m", "bootstrap.main"]
