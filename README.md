# Cloud24 Resource Calculator

Веб‑приложение для анализа потребления облачных ресурсов и генерации отчетов по Hyper‑V, Exchange и S3.

## Быстрый старт

```bash
docker compose up -d --build
```

- Frontend: http://localhost:3000
- Backend (Swagger): http://localhost:8000/docs

## Что реализовано
- Загрузка Excel: `/api/upload/hyperv`, `/api/upload/exchange`, `/api/upload/s3`, `/api/upload/bin-mapping`
- Получение отчетов: `/api/reports/hyperv`, `/api/reports/exchange`, `/api/reports/s3`, `/api/reports/summary`
- Экспорт отчета в Excel: `/api/export/{reportType}` где `reportType` ∈ `hyperv|exchange|s3|summary`
- Валидация форматов, фильтрация, округление размера дисков вверх (Hyper‑V CapacityGB)
- Кеширование результатов в памяти процесса
- Совместимость с кириллицей в Excel (openpyxl)
- Drag&drop загрузка, превью и вкладки отчетов на фронте

## Форматы входных файлов

### Hyper‑V (hyper-v.xlsx)
Обязательные столбцы:
- `VMOwner` — владелец ВМ
- `CPUCount` — количество CPU
- `MemoryGB` — RAM
- `IOPS` — тип диска (500 или 5000)
- `CapacityGB` — размер диска (округляется **вверх** к целому)

**Исключить** строки, где `VMOwner` содержит (регистронезависимо): `id.kz`, `cloud24.kz`, `test`, `demo`.

### Exchange (mail.xlsx)
Обязательные столбцы:
- `CustomerName` — имя тенанта
- `LineDescription` — тариф
- `CurrentPeriod` — количество ящиков

**Исключить** клиентов: `Service Provider`, `test customer`, `Belltower Group`, `Demo Company 1`, `FTP TEST`.

### S3 (s3.xlsx)
- Колонка **B** — владелец тенанта (owner)
- Колонка **C** — должна содержать `"Tenants"`
- Колонка **E** — объем в ГБ

**Исключить** владельцев (B) при совпадении (регистронезависимо):
`admin@demo1.kz, admin@demo2.kz, dbaioralov@id.kz, nextcloud-prod, nextcloud.demo1, nextcloud.demo2, nextcloud.test1, nextcloud.testnew, s-veeam@id.kz, test`.

### Mapping (BIN-*.xlsx)
Файлы соответствий:
- `BIN-Hyper-V.xlsx` — ключ: значения из `VMOwner`
- `BIN-Exchange.xlsx` — ключ: значения из `CustomerName`
- `BIN-S3.xlsx` — ключ: значения из столбца **B** S3
Столбцы: `Наименование компании`, `БИН`, `Ключ` (опционально; если нет — используется первый столбец как ключ).

## Наименования услуг
- Hyper‑V:
  - диск (IOPS 500): «Аренда Дискового пространства SAS, 1Гб (500 IOPS)»
  - диск (IOPS 5000): «Аренда Дискового пространства SSD, 1Гб (5000 IOPS)»
  - CPU: «Аренда виртуального CPU»
  - RAM: «Аренда Оперативной памяти, 1Гб»
- Exchange:
  - Тарифы `Standard-100GB|Standard-50GB|Maximum|Express` → «Аренда Microsoft Exchange Standard (50ГБ почтовый ящик)»
  - Тарифы `Startup|Basic-2GB` → «Аренда Microsoft Exchange Basic (2ГБ почтовый ящик)»
- S3:
  - Если владелец содержит `nextcloud` → «Облачное хранилище Nextcloud, 1 Гб»
  - Иначе → «Объектное хранилище S3»

## Пример запросов
```bash
# Загрузка Hyper‑V
curl -F "file=@hyper-v.xlsx" http://localhost:8000/api/upload/hyperv

# Отчет Hyper‑V
curl http://localhost:8000/api/reports/hyperv

# Экспорт
curl -OJ http://localhost:8000/api/export/hyperv
```

## Примечание
Состояние хранится в памяти процесса бэкенда. Для продакшена можно заменить на PostgreSQL/SQLite хранилище.
