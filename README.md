# Ворота WFH в Home Assistant (hoas-gate-wfh-localtuya)

Локальное управление воротами с контроллером **WFH** (Tuya, Wi-Fi) в Home Assistant — без облака.
Версия конфигурации: **v1.1** (22.11.2026)

**Стек:** Home Assistant OS + HACS + форк [xZetsubou/hass-localtuya](https://github.com/xZetsubou/hass-localtuya), протокол **Tuya 3.5**.

> ⚠️ **Ключевые факты:**
> - Контроллер WFH работает **только по протоколу Tuya 3.5** (проверено tinytuya).
> - Оригинальная LocalTuya (rospogrigio) 3.5 **не поддерживает** — нужен форк **xZetsubou**.
> - Команды — платформа `button` (momentary); концевики — строго `binary_sensor`.
> - Перед публикацией/использованием подставьте свои `IP`, `Device ID` и `Local Key` вместо плейсхолдеров. **Не коммитьте реальный local key!**

---

## Карта устройства (DP)

| DP | code | Доступ | Назначение | Платформа |
|---|---|---|---|---|
| 101 | wfh_open | rw | Открыть (импульс) | `button` |
| 102 | wfh_close | rw | Закрыть (импульс) | `button` |
| 103 | wfh_stop | rw | Стоп (импульс) | `button` |
| 104 | wfh_lock | rw | **Калитка** — частичное открытие ~1 м (не блокировка!) | `button` |
| 105 | return_state | ro | Код состояния: 2=открывается, 3=открыто, 4=закрывается, 5=закрыто, **6=калитка, 11=остановлен** | `sensor` |
| 106 | l_close | ro | Концевик «закрыто» | `binary_sensor` |
| 107 | l_open | ro | Концевик «открыто» | `binary_sensor` |
| 110 | fast_op | rw | Быстрое открытие | `switch` |
| 112 | wfh_rssi | ro | Уровень Wi-Fi, dBm | `sensor` |
| 108, 109, 111 | inrf, fsw, hidden_state | ro | Служебные — в сущности не выводятся | — |

Производные сущности:
- `cover.gate_wfh` — ворота целиком: open / opening / closing / closed + команды (блок `cover:` в `configuration.yaml`)
- `sensor.gate_return_state_text` — расшифровка кода привода текстом (UI-помощник)
- `sensor.gate_status_text` — «Открыты полностью / Закрыты полностью / Открыты частично» (UI-помощник; «частично» = калитка или остановка посреди хода)

> Имена сущностей в файлах — с префиксом `dvor_gate_wfh_` (так назвала интеграция по имени устройства/зоны). У вас префикс будет свой — замените во всех файлах или переименуйте сущности в HA.

---

## Установка

### Шаг 1. HACS и форк LocalTuya

1. Если стоит оригинальная LocalTuya (rospogrigio) — удалить (настройки устройств сохранятся).
2. **HACS → ⋮ → Пользовательские репозитории:** `https://github.com/xZetsubou/hass-localtuya`, тип **Integration**.
3. Установить → **перезапустить HA**.

### Шаг 2. Резервирование IP

В роутере привяжите IP контроллера к его MAC (Static DHCP / Address Reservation).

### Шаг 3. Добавление устройства

**Настройки → Устройства и службы → + Добавить интеграцию → LocalTuya → Add a new device:**

| Поле | Значение |
|---|---|
| Name | `GATE-WFH` |
| Host | `192.168.x.x` (локальный IP контроллера) |
| Device ID | `YOUR_DEVICE_ID` |
| Local Key | `YOUR_LOCAL_KEY` |
| **Protocol version** | **`3.5`** |
| Manual DPS to add | `101,102,103,104,105,106,107,108,109,110,111,112` |
| DPIDs for RESET command | пусто |

> «no datapoints found» → выгрузите Smart Life из памяти на всех телефонах (устройство держит одно локальное подключение) и/или обесточьте контроллер на 15 секунд.

### Шаг 4. Сущности

Добавляйте по одной (галочка «Add another entity»):

| Platform | DP | Friendly Name | Доп. поля |
|---|---|---|---|
| **button** | 101 | Gate Open | по умолчанию |
| **button** | 102 | Gate Close | по умолчанию |
| **button** | 103 | Gate Stop | по умолчанию |
| **button** | 104 | Gate Wicket | калитка (wfh_lock) |
| **binary_sensor** | 106 | Gate Closed Limit | по умолчанию |
| **binary_sensor** | 107 | Gate Open Limit | по умолчанию |
| **sensor** | 105 | Gate Return State | по умолчанию |
| **sensor** | 112 | Gate WiFi RSSI | device class: Signal strength, ед.: `dBm` |
| **switch** | 110 | Gate Fast Open | без галочек «Restore…» и «Passive…» |

> ⚠️ Концевики 106/107 — read-only, **только binary_sensor**. Команды 101–104 — **только button**.

### Шаг 5. Текстовые сенсоры (UI-помощники)

**Настройки → Устройства и службы → Вспомогательные элементы → + Создать → Template → Датчик шаблона** (не «бинарный датчик»!).

**Gate Return State Text** — шаблон состояния:
```jinja
{% set s = states('sensor.dvor_gate_wfh_gate_return_state') | float(-1) %}
{% set code = (s * 10) | round(0) | int if 0 <= s < 1 else s | int %}
{% set map = {2: 'Открывается', 3: 'Открыто', 4: 'Закрывается', 5: 'Закрыто', 6: 'Калитка', 11: 'Остановлен'} %}
{{ map.get(code, 'Неизвестно (' ~ s ~ ')') }}
```

**Gate Status Text** — шаблон состояния:
```jinja
{% if is_state('binary_sensor.dvor_gate_wfh_gate_open_limit', 'on') %}Открыты полностью
{% elif is_state('binary_sensor.dvor_gate_wfh_gate_closed_limit', 'on') %}Закрыты полностью
{% else %}Открыты частично{% endif %}
```

Остальные поля пустыми. «Неизвестно (N)» — ловушка для нерасшифрованных кодов привода.

### Шаг 6. Блок cover (единственная правка YAML)

1. `configuration.yaml` → в конец вставьте **только блок `cover:`** из `gate_wfh_localtuya.yaml`.
2. Настройки → Система → ⋮ → **Проверить конфигурацию** → **Перезапустить**.

Результат: `cover.gate_wfh` со статусами open / opening / closing / closed (по DP 105, резерв — концевики).

### Шаг 7. Карточка дашборда

Дашборд → ⋮ → Изменить → + Добавить карточку → **Вручную (Manual)** → вставить всё из `gate_wfh_lovelace.yaml`.

> `gate_wfh_localtuya.yaml` → в `configuration.yaml`; `gate_wfh_lovelace.yaml` → в карточку. Ошибка «No card type configured» = перепутаны файлы.

### Шаг 8. Проверка

1. **Открыть** → `opening` → `open`, концевик открытия = on.
2. **Стоп** посреди хода → «Состояние привода» = Остановлен (код 11).
3. **Калитка** → открытие ~1 м → «Состояние привода» = Калитка (код 6), «Статус ворот» = Открыты частично.
4. **Закрыть** → `closing` → `closed`.

### Шаг 9 (опционально). Автоматизация «ворота забыли закрыть»

```yaml
alias: Gate left open
triggers:
  - trigger: state
    entity_id: binary_sensor.dvor_gate_wfh_gate_closed_limit
    to: "off"
    for: "00:10:00"
actions:
  - action: notify.notify
    data:
      title: "Ворота"
      message: "Ворота не закрыты уже 10 минут!"
mode: single
```

---

## Диагностика

| Симптом | Решение |
|---|---|
| `no datapoints found` | Закрыть Smart Life везде; перезагрузить контроллер по питанию; проверить форк xZetsubou и версию 3.5 |
| Сущности «Недоступно» | Перезагрузка контроллера; устройство занято Smart Life; проверить IP/пинг |
| «Объект не найден» в карточке | Сличить фактические ID (Настройки → Объекты) с кодом карточки |
| Концевики — переключатели | Пересоздать 106/107 как binary_sensor |
| Команды не работают | Проверить, что 101–104 созданы как button; журнал: Настройки → Система → Журналы → `localtuya` |
| `Error 28841002: IoT Core subscription expired` | На локальную работу не влияет |
| Перепривязка в Smart Life сломала всё | Сменился local key → обновить в Edit device |
| Тест протокола | `pip install tinytuya && python3 test_gate.py <IP>` |

## Файлы

| Файл | Назначение |
|---|---|
| `gate_wfh_localtuya.yaml` | Справочник DP + блок `cover:` для configuration.yaml |
| `gate_wfh_lovelace.yaml` | Карточка дашборда |
| `test_gate.py` | Тест связи с контроллером (перебор версий протокола) |

## История версий

- **v1.1** (22.11.2026) — коды return_state 6=калитка, 11=остановлен; в cover они дают статус `open`.
- **v1.0** (22.11.2026) — первая рабочая версия: форк xZetsubou, протокол 3.5, button + binary_sensor, UI-помощники, cover, карточка.
