# Diagram Types — 図タイプ別リファレンス

## 1. システム概要図 (System Overview)

コンポーネント間の関係と全体構成を示す。

- **指示**: `graph TB`
- **用途**: プロジェクト全体のアーキテクチャ俯瞰
- **特徴**: subgraphで階層的にグループ化、ネスト2階層まで

### テンプレート

```mermaid
graph TB
    subgraph External["External Services"]
        SvcA["Service A\nAPI"]
        SvcB["Service B\nHosting"]
    end

    subgraph System["Project Name"]
        subgraph Frontend["Web Frontend"]
            App["Framework\nUI Library"]
        end
        subgraph Backend["Backend"]
            API["API Server\nLanguage"]
        end
    end

    DB[("Database\nEngine")]
    User["User / Browser"]

    SvcA -->|"data"| API
    SvcB -->|"deploy"| App
    API -->|"read/write"| DB
    App -->|"read"| DB
    User -->|"access"| App

    style External fill:#f0f0f0,stroke:#999
    style System fill:#e8f4fd,stroke:#1DA1F2
    style Frontend fill:#dbeafe,stroke:#2563eb
    style Backend fill:#dcfce7,stroke:#16a34a
    style DB fill:#fce7f3,stroke:#db2777
```

### 実例（reverve-X-analysis）

```mermaid
graph TB
    subgraph External["External Services"]
        X["X (Twitter)\nGraphQL API"]
        Vercel["Vercel\nHosting"]
        GHA["GitHub Actions\nCI/CD"]
    end

    subgraph System["reverve-X-analysis"]
        subgraph Dashboard["Web Dashboard"]
            NextJS["Next.js 15\nTailwind CSS v4\nChart.js"]
        end
        subgraph Scraper["Scraper"]
            PW["Python\nPlaywright"]
        end
        subgraph MCP["MCP Server"]
            FastMCP["Python\nFastMCP"]
        end
    end

    DB[("Supabase\nPostgreSQL")]
    User["User / Browser"]
    Claude["Claude Code"]

    GHA -->|"daily cron"| PW
    PW -->|"intercept GraphQL"| X
    PW -->|"write"| DB
    NextJS -->|"read"| DB
    FastMCP -->|"read"| DB
    Vercel -->|"deploy"| NextJS
    User -->|"access"| NextJS
    Claude -->|"MCP protocol"| FastMCP

    style External fill:#f0f0f0,stroke:#999
    style System fill:#e8f4fd,stroke:#1DA1F2
    style Dashboard fill:#dbeafe,stroke:#2563eb
    style Scraper fill:#dcfce7,stroke:#16a34a
    style MCP fill:#fef3c7,stroke:#d97706
    style DB fill:#fce7f3,stroke:#db2777
```

---

## 2. データフロー図 (Data Flow)

入力→処理→出力のパイプラインを示す。

- **指示**: `flowchart LR`
- **用途**: データの変換・流れの可視化
- **特徴**: 左から右への流れ、ノードにブランドカラー適用

### テンプレート

```mermaid
flowchart LR
    A["Data Source\n(origin)"] -->|"raw data"| B["Processor\nTool"]
    B -->|"parsed\ndata"| C["Transformer"]
    C -->|"store"| D[("Database\nEngine")]
    D -->|"query"| E["Consumer A"]
    D -->|"query"| F["Consumer B"]

    style A fill:#1DA1F2,color:#fff,stroke:#0d8ecf
    style D fill:#3ECF8E,color:#fff,stroke:#2ea872
```

### 実例（reverve-X-analysis）

```mermaid
flowchart LR
    A["X Profile Page\n(x.com)"] -->|"GraphQL\nResponse"| B["Playwright\nScraper"]
    B -->|"Parse Tweets\n+ Metrics"| C["Data Parser"]
    C -->|"upsert_tweet"| D[("Supabase\nPostgreSQL")]
    C -->|"take_snapshots\n(delta calc)"| D
    C -->|"upsert_account\n_snapshot"| D
    D -->|"Supabase Client\n(Lazy Proxy)"| E["Next.js\nDashboard"]
    D -->|"Supabase Client"| F["MCP Server"]
    E -->|"Charts\n& KPIs"| G["User\nBrowser"]
    F -->|"Analysis\nResults"| H["Claude\nCode"]

    style A fill:#1DA1F2,color:#fff,stroke:#0d8ecf
    style D fill:#3ECF8E,color:#fff,stroke:#2ea872
    style E fill:#000,color:#fff,stroke:#333
    style G fill:#f0f0f0,stroke:#999
    style H fill:#d4a574,stroke:#b8864a
```

---

## 3. デプロイ構成図 (Deployment)

インフラ階層とホスティングトポロジを示す。

- **指示**: `graph TB`
- **用途**: 各コンポーネントの稼働場所と通信経路
- **特徴**: subgraphでデプロイ先（Cloud/CI/Local等）をグループ化、ブランドカラーをsubgraphに適用

### テンプレート

```mermaid
graph TB
    subgraph CloudA["Cloud Service A"]
        App["Application\nConfig details"]
    end

    subgraph CI["CI/CD Platform"]
        Worker["Worker\nSchedule info"]
    end

    subgraph Local["Local Machine"]
        Tool["Local Tool"]
        Agent["Local Agent"]
    end

    subgraph CloudB["Cloud DB"]
        DB[("Database\nTier info")]
    end

    Worker -->|"write data"| DB
    App -->|"read data"| DB
    Tool -->|"read data"| DB
    Agent <-->|"protocol"| Tool

    style CloudA fill:#000,color:#fff,stroke:#333
    style CI fill:#24292e,color:#fff,stroke:#555
    style Local fill:#f0f0f0,stroke:#999
    style CloudB fill:#3ECF8E,color:#fff,stroke:#2ea872
```

### 実例（reverve-X-analysis）

```mermaid
graph TB
    subgraph Vercel["Vercel (Cloud)"]
        Dashboard["Next.js 15\nWeb Dashboard\nstandalone output"]
    end

    subgraph GitHub["GitHub Actions"]
        Scraper["Python Scraper\nDaily 0:00 JST\nubuntu-latest\ntimeout: 15min"]
    end

    subgraph Local["Local Machine"]
        MCP["MCP Server\nFastMCP (stdio)"]
        Claude["Claude Code"]
    end

    subgraph SupabaseCloud["Supabase (Cloud)"]
        PG[("PostgreSQL\n6 Tables\nFree Tier")]
    end

    subgraph GHRepo["GitHub Repository"]
        Repo["OndaMasashi/\nreverve-X-analysis"]
    end

    Scraper -->|"write data"| PG
    Dashboard -->|"read data"| PG
    MCP -->|"read data"| PG
    Claude <-->|"stdio"| MCP
    Repo -->|"push triggers\nauto deploy"| Vercel
    GHRepo -->|"cron / dispatch"| GitHub

    style Vercel fill:#000,color:#fff,stroke:#333
    style GitHub fill:#24292e,color:#fff,stroke:#555
    style Local fill:#f0f0f0,stroke:#999
    style SupabaseCloud fill:#3ECF8E,color:#fff,stroke:#2ea872
    style GHRepo fill:#24292e,color:#fff,stroke:#555
```

---

## 4. ER図 (Entity-Relationship)

データベーススキーマとエンティティ間の関係を示す。

- **指示**: `erDiagram`
- **用途**: テーブル設計、リレーション定義
- **特徴**: Mermaidネイティブ構文、カーディナリティ表記

### 構文リファレンス

```
テーブル名 {
    データ型 フィールド名 属性 "説明"
}
```

属性: `PK`（主キー）、`FK`（外部キー）、`UK`（ユニークキー）

カーディナリティ:
| 記号 | 意味 |
|------|------|
| `\|\|--o{` | 1対多 |
| `\|\|--\|\|` | 1対1 |
| `o{--o{` | 多対多 |
| `\|\|--o\|` | 1対0または1 |

### テンプレート

```mermaid
erDiagram
    parent_table {
        text id PK "Primary key"
        text name
        timestamptz created_at
    }

    child_table {
        bigserial id PK "Auto increment"
        text parent_id FK "References parent_table"
        text value
    }

    parent_table ||--o{ child_table : "has many"
```

### 実例（reverve-X-analysis）

```mermaid
erDiagram
    tweets {
        text id PK "Tweet ID"
        text text "Tweet body"
        timestamptz created_at
        integer impressions
        integer likes
        integer retweets
        real engagement_rate
        boolean has_media
        timestamptz updated_at
    }

    tweet_snapshots {
        bigserial id PK "Auto increment"
        text tweet_id FK "References tweets"
        date snapshot_date "UNIQUE with tweet_id"
        integer impressions
        integer likes_delta
        integer impressions_delta
    }

    tweet_hashtags {
        text tweet_id PK "Composite PK + FK"
        text hashtag PK "Composite PK"
    }

    tweets ||--o{ tweet_snapshots : "daily snapshots"
    tweets ||--o{ tweet_hashtags : "has hashtags"
```

---

## 5. シーケンス図 (Sequence)

コンポーネント間の時系列インタラクションを示す。

- **指示**: `sequenceDiagram`
- **用途**: API呼び出しフロー、ユーザーインタラクション、処理タイミング
- **特徴**: participant定義、ループ・ノート注釈

### 構文リファレンス

| 要素 | 構文 |
|------|------|
| 参加者定義 | `participant ID as "表示名"` |
| 同期リクエスト | `->>` |
| レスポンス | `-->>` |
| 注釈 | `Note over A,B: テキスト` |
| ループ | `loop 説明` ... `end` |
| 条件分岐 | `alt 条件` ... `else` ... `end` |
| オプション | `opt 条件` ... `end` |

### テンプレート

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant DB as Database

    C->>S: Request (params)
    S->>DB: Query
    DB-->>S: Result set
    S-->>C: Response (JSON)

    loop Polling
        C->>S: Status check
        S-->>C: Status response
    end

    Note over C,S: Connection closed
```

### 実例（reverve-X-analysis）

```mermaid
sequenceDiagram
    participant GHA as GitHub Actions
    participant SC as Scraper (run.py)
    participant PW as Playwright
    participant X as X.com
    participant DB as Supabase

    GHA->>SC: Trigger (daily cron / manual)
    SC->>PW: Launch Chromium (headless)
    PW->>PW: Set cookies (auth_token, ct0)
    PW->>X: Navigate to profile page
    Note over PW,X: wait_until="domcontentloaded" + 3s wait

    PW->>X: Register response interceptor
    X-->>PW: UserTweets GraphQL response
    PW->>SC: Parse tweets + metrics

    loop Scroll pagination
        PW->>X: Scroll down
        X-->>PW: Additional UserTweets responses
        PW->>SC: Collect new tweets
    end

    SC->>DB: upsert_tweet (each tweet)
    Note over SC,DB: Extract hashtags & mentions
    SC->>DB: take_snapshots (delta calculation)
    SC->>DB: upsert_account_snapshot
    SC->>DB: log_scrape_session (status)
```

---

## 6. C4コンテキスト図 (C4 Context)

エンタープライズレベルのシステム境界を示す。複数システム間の関係を俯瞰する場合に使用。

- **指示**: `C4Context`
- **用途**: 大規模システムの外部境界、利用者とシステムの関係
- **特徴**: `Person`, `System`, `System_Ext`, `Boundary` キーワード
- **注意**: 小規模プロジェクトでは「1. システム概要図」で十分。C4は複数チーム・複数システムが絡む場合に有効

### テンプレート

```mermaid
C4Context
    title System Context Diagram

    Person(user, "User", "End user of the system")
    System(sys, "Target System", "Main application")
    System_Ext(ext1, "External API", "Third-party service")
    SystemDb_Ext(db, "Database", "Cloud database")

    Rel(user, sys, "Uses", "HTTPS")
    Rel(sys, ext1, "Calls", "REST API")
    Rel(sys, db, "Reads/Writes", "SQL")
```

---

## 7. Gitグラフ (Git Graph)

ブランチ戦略とマージフローの可視化。

- **指示**: `gitGraph`
- **用途**: ブランチ戦略の説明、開発フロー文書

### テンプレート

```mermaid
gitGraph
    commit id: "init"
    branch develop
    checkout develop
    commit id: "feature-a"
    commit id: "feature-b"
    checkout main
    merge develop id: "v1.0"
    branch hotfix
    commit id: "fix-bug"
    checkout main
    merge hotfix id: "v1.0.1"
```

---

## 8. ガントチャート (Gantt)

タイムラインとマイルストーンの可視化。

- **指示**: `gantt`
- **用途**: プロジェクトスケジュール、フェーズ管理

### テンプレート

```mermaid
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    axisFormat %m/%d

    section Phase 1
        Requirements     :a1, 2025-01-01, 14d
        Design           :a2, after a1, 7d

    section Phase 2
        Implementation   :b1, after a2, 21d
        Testing          :b2, after b1, 14d

    section Release
        Deployment       :milestone, after b2, 0d
```

---

## 図タイプ選択ガイド

| やりたいこと | 推奨タイプ |
|-------------|-----------|
| システム全体の構成を見せたい | 1. システム概要図 |
| データの流れを追いたい | 2. データフロー図 |
| どこで何が動いているか示したい | 3. デプロイ構成図 |
| DB設計を文書化したい | 4. ER図 |
| 処理の順序・タイミングを示したい | 5. シーケンス図 |
| 複数システムの境界を俯瞰したい | 6. C4コンテキスト図 |
| ブランチ戦略を説明したい | 7. Gitグラフ |
| スケジュールを示したい | 8. ガントチャート |
