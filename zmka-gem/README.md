# ZM_KA GEM — сайт

Одностраничный лендинг tooth gem artist из Вильнюса (@zm_ka_gem) с формой записи.
Next.js 15 (App Router) · TypeScript · Tailwind CSS 4 · framer-motion (только появление секций).

## Запуск

```bash
cd zmka-gem
npm install
cp .env.example .env.local   # заполнить ключи, см. ниже
npm run dev                  # http://localhost:3000
npm run build && npm start   # продакшен-сборка локально
npm run lint                 # проверка типов
```

Маршруты: `/` — EN (по умолчанию), `/lt` — LT. API: `POST /api/booking`.

## Переменные окружения

| Переменная | Нужна | Что это |
|---|---|---|
| `NEXT_PUBLIC_SITE_URL` | да | Боевой адрес сайта (canonical, OG, JSON-LD, sitemap) |
| `RESEND_API_KEY` | да* | Ключ [Resend](https://resend.com) для писем о записи |
| `BOOKING_TO_EMAIL` | да* | Куда приходят заявки (можно несколько через запятую) |
| `BOOKING_FROM_EMAIL` | нет | Отправитель; домен должен быть подтверждён в Resend. По умолчанию `onboarding@resend.dev` (только для теста) |
| `TELEGRAM_BOT_TOKEN` | нет | Токен бота от @BotFather — дублировать заявки в Telegram |
| `TELEGRAM_CHAT_ID` | нет | Чат, куда бот пишет (личный id или id группы) |

\* Нужен хотя бы один канал: Resend или Telegram. В продакшене без каналов форма
честно вернёт ошибку (и предложит написать в DM), а не «съест» заявку. В `npm run dev`
без ключей заявка просто печатается в консоль.

## Где менять контент

| Что | Файл |
|---|---|
| Адрес, телефон, депозит, ссылки, флаги секций | `content/site.ts` |
| Цены услуг | `content/services.ts` |
| Фото работ, подписи `set 01…`, alt-тексты | `content/work.ts` + `public/work/` |
| Обучение: формат, длительность, цена, даты, фото | `content/training.ts` |
| Все тексты | `messages/en.json`, `messages/lt.json` |

Плейсхолдеры в `[скобках]` показываются на сайте как есть — их видно сразу.

Секции `Feedback` и `Warranty` уже в коде (якоря `#feedback`, `#warranty`), но скрыты
флагами `site.sections.feedback / warranty`. Включать только с реальными отзывами и
готовыми условиями гарантии. `Training` включена.

## Ассеты

Исходники лежат в `source-assets/` (не в git):
`butterfly.jpg` (бабочка маджента на белом), `wordmark.png` (надпись, чёрная на прозрачном),
`work/set-NN.jpg`, `work/training.jpg` (можно `.HEIC`, нужен `pip install pillow-heif`).

```bash
pip install pillow        # один раз
npm run assets            # = python3 scripts/prepare_assets.py
```

Скрипт собирает:
- `public/brand/butterfly-{440,600,880}.webp` и `butterfly-light-*` — бабочка с прозрачностью
  (альфа из зелёного канала: у маджента G=0, у белого G=255 — без белой каймы) и светлая
  версия для тёмных блоков. Lossless WebP с квантованной альфой: точки чёткие, 880px ≈ 32 КБ;
- `public/brand/butterfly-sprite-{16,32,48}.{png,svg}` — пиксельные спрайты, показываются
  только в целых масштабах с `image-rendering: pixelated`;
- `public/brand/wordmark-{black,white}.png`;
- `app/icon.svg`, `app/apple-icon.png` (фавикон-бабочка), `app/opengraph-image.png`;
- `public/work/*.jpg` (до 1600px по длинной стороне).

## Анимации и доступность

- Бабочки: внешний слой `drift` (9–14 с, `steps(60)`), внутренний `flap` (scaleX, `steps(5)`).
- Шлейф курсора — только при `hover: hover` + `pointer: fine`; бабочки при скролле — до 4 штук.
- `prefers-reduced-motion: reduce` и кнопка «Pause Animations» в футере выключают всё
  (состояние кнопки запоминается в `localStorage`).
- Анимируются только `transform`/`opacity`; `mix-blend-mode`/`filter` не используются.

## Деплой на Vercel

1. New Project → импортировать репозиторий.
2. **Root Directory: `zmka-gem`** (в корне репо лежит другой проект).
3. Framework: Next.js (определится сам). Добавить env-переменные из таблицы.
4. Подключить домен и прописать его в `NEXT_PUBLIC_SITE_URL`.

Lighthouse (локально, `next start`): Desktop — Performance 99, Accessibility/Best Practices/SEO 100;
Mobile — Performance 94–96, Accessibility/Best Practices/SEO 100.
