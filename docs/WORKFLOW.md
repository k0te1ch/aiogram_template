# Workflow: как это всё работает

Документ описывает полный цикл — от первого `git commit` до GitHub Release — и
как организовать командную работу через feature-ветки.

> Все диаграммы написаны на [Mermaid](https://mermaid.js.org/). GitHub
> рендерит их автоматически. Локально посмотреть можно в VS Code с плагином
> *Markdown Preview Mermaid Support*.

---

## 1. Большая картина

```mermaid
flowchart TD
    A[Локальные правки] --> B[git commit]
    B --> C{pre-commit hooks}
    C -- ruff/end-of-file --> C
    C -- commit-msg<br/>commitizen --> D{Conventional<br/>Commits?}
    D -- нет --> X[Коммит отклонён<br/>исправить сообщение]
    D -- да --> E[Commit создан локально]
    E --> F[git push в feature-ветку]
    F --> G[Pull Request на GitHub]
    G --> H[CI: python-app.yml<br/>pre-commit + pytest]
    H -- зелёный + approve --> I[Squash/merge в main]
    I --> J[poetry run cz bump<br/>+ git push --follow-tags]
    J --> K[Tag v* запушен]
    K --> L[CI: release.yml<br/>git-cliff]
    L --> M[GitHub Release<br/>+ CHANGELOG.md commit в main]

    classDef bad fill:#fee,stroke:#c33;
    class X bad;
```

Главное: **сообщения коммитов — это и есть «исходник» changelog'а**. Поэтому их
формат жёстко проверяется на этапе `git commit`, до того как код вообще
попадает на сервер.

---

## 2. Conventional Commits — формат сообщений

```
<type>(<scope>)!: <subject>

<body>

<footer>
```

`type` обязателен, остальное опционально. `!` после типа/скоупа означает
breaking change.

| Type       | Когда использовать                              | Попадает в CHANGELOG как |
|------------|--------------------------------------------------|--------------------------|
| `feat`     | Новая функциональность                          | **Features**             |
| `fix`      | Исправление бага                                 | **Bug Fixes**            |
| `perf`     | Улучшение производительности                     | **Performance**          |
| `refactor` | Рефакторинг без изменения поведения              | **Refactor**             |
| `docs`     | Только документация                              | **Documentation**        |
| `test`     | Добавление/правка тестов                         | **Tests**                |
| `build`    | Сборка, зависимости (pyproject.toml, poetry.lock)| **Build System**         |
| `ci`       | GitHub Actions, pre-commit                       | **CI**                   |
| `style`    | Форматирование, точки с запятой и т.п.           | **Styling**              |
| `chore`    | Рутина, без влияния на код                       | **Miscellaneous**        |
| `revert`   | Откат прошлого коммита                           | **Revert**               |

**Примеры:**

```bash
git commit -m "feat(auth): add JWT refresh endpoint"
git commit -m "fix(logger): correct rotation when file is locked"
git commit -m "feat(api)!: drop v1 endpoints"          # breaking
git commit -m "refactor: extract config loader into module"
```

Для breaking change можно либо `!`, либо футер:

```
feat(api): switch to httpx

BREAKING CHANGE: requests dependency removed; clients must use httpx.
```

`cz bump` смотрит на эти типы и решает, как менять версию:

- `BREAKING CHANGE` → **major** (1.2.3 → 2.0.0)
- `feat:` → **minor** (1.2.3 → 1.3.0)
- `fix:` / `perf:` → **patch** (1.2.3 → 1.2.4)
- остальное → версия не меняется (нужно `--increment` руками)

> Пока в `pyproject.toml` стоит `major_version_zero = true` (версия `0.x.y`),
> breaking change поднимет minor, а не major — это нормально для проекта,
> ещё не выпустившего `1.0.0`.

---

## 3. Локальный цикл разработки

```mermaid
sequenceDiagram
    autonumber
    participant Dev as Разработчик
    participant Git as git (local)
    participant PC as pre-commit
    participant CZ as commitizen
    Dev->>Git: git add .
    Dev->>Git: git commit -m "feat: ..."
    Git->>PC: запуск pre-commit hooks
    PC->>PC: ruff, end-of-file-fixer, check-yaml
    alt хук поправил файлы
        PC-->>Dev: commit отклонён,<br/>перезапусти git add + commit
    end
    Git->>CZ: запуск commit-msg hook
    CZ->>CZ: парсинг сообщения
    alt не соответствует формату
        CZ-->>Dev: ошибка с примером корректного сообщения
    else всё ок
        CZ-->>Git: ok
        Git-->>Dev: commit создан
    end
```

Если запутался в формате — есть интерактивный режим:

```bash
poetry run cz commit     # пройдёт по шагам и соберёт сообщение
```

---

## 4. Ветки — какие стратегии бывают

Три популярных модели:

### GitHub Flow (рекомендую для этого шаблона)

```mermaid
gitGraph
    commit id: "init"
    commit id: "feat: logger"
    branch feature/auth
    checkout feature/auth
    commit id: "feat(auth): login"
    commit id: "test(auth): cover edge cases"
    checkout main
    merge feature/auth tag: "PR #12"
    commit id: "fix: typo in README"
    branch feature/cache
    checkout feature/cache
    commit id: "feat(cache): in-memory"
    checkout main
    merge feature/cache tag: "PR #15"
    commit id: "bump: 0.1.0 -> 0.2.0" tag: "v0.2.0"
```

- Одна долгоживущая ветка: `main`.
- Любая работа — короткая feature-ветка, обычно 1–3 дня.
- Merge через PR с code review и зелёным CI.
- Релиз = тег на `main`.
- Подходит для small/medium команд, SaaS, шаблонов, OSS-библиотек.

### Git Flow (классика, тяжеловесная)

```mermaid
gitGraph
    commit id: "init"
    branch develop
    commit
    branch feature/x
    commit
    checkout develop
    merge feature/x
    branch release/1.0
    commit id: "prep 1.0"
    checkout main
    merge release/1.0 tag: "v1.0.0"
    checkout develop
    merge release/1.0
    branch hotfix/1.0.1
    checkout hotfix/1.0.1
    commit id: "fix prod"
    checkout main
    merge hotfix/1.0.1 tag: "v1.0.1"
    checkout develop
    merge hotfix/1.0.1
```

- Ветки: `main`, `develop`, `feature/*`, `release/*`, `hotfix/*`.
- Имеет смысл, когда у тебя **версионируемый продукт с несколькими
  поддерживаемыми мажорными версиями** (типа Django LTS).
- Для большинства проектов — overkill. Дольше merge'ить, легче запутаться.

### Trunk-Based Development

```mermaid
gitGraph
    commit
    commit id: "feat A (за фичефлагом)"
    commit id: "feat B"
    commit id: "включили flag A"
    commit
```

- Все коммитят прямо в `main` (или через очень короткие ветки на часы).
- Незаконченные фичи прячутся за feature flags.
- Требует мощного CI и фича-флагов. Хорошо для команд 50+ с continuous
  deployment. Для шаблона — преждевременная оптимизация.

### Сводка

| Критерий                     | GitHub Flow | Git Flow      | Trunk-Based |
|------------------------------|-------------|---------------|-------------|
| Долгоживущие ветки           | 1 (`main`)  | 2+            | 1 (`main`)  |
| Сложность                    | Низкая      | Высокая       | Средняя     |
| Размер команды               | 2–20        | 5+            | 10+         |
| Нужны feature flags          | Опционально | Нет           | Да          |
| Continuous deployment        | Подходит    | Не очень      | Идеально    |
| **Подходит этому шаблону**   | **Да**      | Нет           | Нет         |

---

## 5. Командный workflow по шагам (GitHub Flow)

Допустим, нас двое: **Алиса** (автор) и **Боб** (ревьюер).

```mermaid
sequenceDiagram
    autonumber
    participant A as Алиса
    participant Local as Локально (Алиса)
    participant Remote as origin/main
    participant CI as GitHub CI
    participant B as Боб

    A->>Local: git switch main && git pull
    A->>Local: git switch -c feature/jwt-refresh
    Note over A,Local: пишет код, коммитит<br/>feat(auth): add /refresh
    A->>Remote: git push -u origin feature/jwt-refresh
    A->>Remote: gh pr create
    Remote->>CI: запуск python-app.yml
    CI-->>Remote: ✅ зелёный
    Remote->>B: уведомление о PR
    B->>Remote: комменты в Files Changed
    B-->>A: запрос правок
    A->>Local: правки + git commit --fixup / amend
    A->>Remote: git push
    Remote->>CI: повторный прогон
    CI-->>Remote: ✅
    B->>Remote: Approve
    A->>Remote: Squash & merge
    Remote->>Remote: удаление feature-ветки
    A->>Local: git switch main && git pull && git branch -d feature/jwt-refresh
```

**Конкретные команды у Алисы:**

```bash
# 1. Свежий main
git switch main
git pull --ff-only

# 2. Новая ветка
git switch -c feature/jwt-refresh

# 3. Работа + коммиты
# ... правки ...
git add app/auth/
git commit -m "feat(auth): add /refresh endpoint"
git commit -m "test(auth): cover refresh edge cases"

# 4. Пуш и PR
git push -u origin feature/jwt-refresh
gh pr create --title "feat(auth): JWT refresh" --body "Closes #42"

# 5. После ревью — правки
git commit -am "fix(auth): handle expired refresh tokens"
git push

# 6. После merge — уборка
git switch main
git pull --ff-only
git branch -d feature/jwt-refresh
```

### Несколько правил, которые сильно экономят нервы

1. **Маленькие PR.** Лучше три PR по 200 строк, чем один на 600. Ревью качественнее, конфликты реже.
2. **Одна тема на ветку.** Не смешивай рефакторинг с фичей.
3. **Имена веток:** `feature/<кратко>`, `fix/<кратко>`, `chore/<кратко>`. Например `feature/jwt-refresh`, `fix/logger-rotation`.
4. **Защити main.** В Settings → Branches: require PR, require CI green, require 1 approval, dismiss stale reviews on push.
5. **Squash merge по умолчанию.** Тогда история `main` остаётся одной строкой коммитов в Conventional-формате и changelog получается чистым. Сообщение squash-коммита редактируй вручную в формате CC.
6. **Никогда не push --force в main.** В свою feature-ветку — можно (после rebase), но согласуй с ревьюером, если он уже смотрит.

---

## 6. Rebase или merge?

```mermaid
flowchart LR
    A[main ушёл вперёд<br/>пока ты работал] --> B{Что делать?}
    B -- "ветка только твоя" --> C[git pull --rebase origin main]
    B -- "на ветке<br/>работают ещё люди" --> D[git merge origin/main]
    C --> E[Чистая линейная история<br/>force-push в свою ветку]
    D --> F[Merge-коммит<br/>безопасно для соавторов]
```

Правило: **rebase для своих веток, merge для общих**. После rebase нужен
`git push --force-with-lease` (безопаснее `--force`: не перезапишет чужие
коммиты, которые ты ещё не видел).

---

## 7. Релиз — что происходит после `cz bump`

```mermaid
sequenceDiagram
    autonumber
    participant Dev as Разработчик
    participant Local as Local repo
    participant GH as GitHub
    participant CI as release.yml
    participant Rel as GitHub Releases

    Dev->>Local: poetry run cz bump
    Local->>Local: читает коммиты с прошлого тега
    Local->>Local: определяет bump: patch/minor/major
    Local->>Local: правит pyproject.toml<br/>создаёт коммит "bump: ..."<br/>создаёт тег vX.Y.Z
    Dev->>GH: git push --follow-tags
    GH->>CI: триггер по тегу v*
    CI->>CI: checkout с fetch-depth: 0
    CI->>CI: git-cliff --latest<br/>→ RELEASE_NOTES.md
    CI->>CI: git-cliff --output CHANGELOG.md<br/>(полный)
    CI->>Rel: создание GitHub Release<br/>с RELEASE_NOTES.md
    CI->>GH: commit обновлённого<br/>CHANGELOG.md в main
```

Что увидит пользователь:
- На вкладке **Releases** — новый релиз с группированным списком изменений и ссылками на PR/авторов.
- В корне репо — обновлённый [CHANGELOG.md](../CHANGELOG.md) с полной историей.
- Тег `vX.Y.Z` в `git tag`.

---

## 8. Хотфикс на проде

Если на `main` уже накопились незавершённые `feat:`, а на проде нужно срочно
поправить один баг:

```mermaid
gitGraph
    commit id: "v1.2.0" tag: "v1.2.0"
    commit id: "feat: WIP-1"
    commit id: "feat: WIP-2"
    branch hotfix/1.2.1
    checkout hotfix/1.2.1
    commit id: "fix: critical bug"
    checkout main
    merge hotfix/1.2.1 tag: "v1.2.1"
    commit id: "feat: WIP-3"
```

Если незавершённые фичи на `main` **не deployable** — придётся откатиться к
тегу, создать ветку от него, пофиксить, выпустить, потом мержить в `main`:

```bash
git switch -c hotfix/1.2.1 v1.2.0
# ... фикс ...
git commit -m "fix(api): null pointer in /users"
poetry run cz bump --increment PATCH
git push --follow-tags origin hotfix/1.2.1
# дальше PR hotfix/1.2.1 -> main
```

Это редкий сценарий, и если он у тебя случается часто — пора смотреть в
сторону feature flags или Git Flow.

---

## 9. Что лежит за этим в репо

| Файл                                      | Что делает                                                       |
|-------------------------------------------|------------------------------------------------------------------|
| [.pre-commit-config.yaml](../.pre-commit-config.yaml) | Запускает ruff и commitizen на каждом `git commit`               |
| [pyproject.toml](../pyproject.toml) (`[tool.commitizen]`) | Конфиг bump и формата тегов                                      |
| [cliff.toml](../cliff.toml)               | Шаблон changelog и правила группировки коммитов                  |
| [.github/workflows/python-app.yml](../.github/workflows/python-app.yml) | CI на каждый PR: lint + tests                                    |
| [.github/workflows/release.yml](../.github/workflows/release.yml) | CI на тег `v*`: changelog + GitHub Release                       |
| [CHANGELOG.md](../CHANGELOG.md)           | Авто-сгенерированная история. Руками **не редактировать**.       |

---

## TL;DR

1. Commit-сообщения пишем по Conventional Commits — без этого коммит не пройдёт.
2. Каждая задача — отдельная короткая ветка `feature/...`, через PR в `main`.
3. На `main` всегда зелёный CI, всегда deployable.
4. Релиз: `poetry run cz bump && git push --follow-tags` — всё остальное делает CI.
5. CHANGELOG.md и Release Notes никто руками не пишет — они генерируются из истории коммитов.
