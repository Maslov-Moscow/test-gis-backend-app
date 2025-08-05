FROM python:3.13-alpine

# Установим зависимости для Rust и Uv
RUN apk add --no-cache curl libffi-dev gcc musl-dev cargo

WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем uv, используя переменные окружения, не модифицируя shell
RUN curl -LsSf https://astral.sh/uv/install.sh \
    | env UV_NO_MODIFY_PATH=1 UV_UNMANAGED_INSTALL="/root/.local/bin" sh \
 && mv /root/.local/bin/uv /usr/local/bin/uv

# Добавим uv в PATH (с учётом установки)
ENV PATH="/usr/local/bin:${PATH}"

# Синхронизация зависимостей без установки проекта
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-editable

# Копируем исходники
COPY src/ ./src

# Финальная установка зависимостей без dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

CMD ["uv", "run", "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0"]
