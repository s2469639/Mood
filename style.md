# 🎨 Moodify Style & Design System Guide (style.md)

> 사람들의 감정과 일상의 순간을 음악으로 이어주는 **Moodify**의 디자인 시스템 및 스타일 가이드입니다.  
> 부드럽고 몽환적인 감성 그라데이션, 포근한 글래스모피즘(Glassmorphism), 직관적인 모바일 퍼스트 뷰를 지향합니다.

---

## 🌈 1. Color Palette (색상 시스템)

Moodify의 컬러는 **새벽과 노을 사이의 감성적인 하늘빛**을 모티브로 하여, 몽환적인 퍼플/핑크와 편안한 파스텔톤을 조화롭게 사용합니다.

### 🎨 Primary & Accent Colors
| Role | Color Name | Hex Code | Preview | Usage |
| :--- | :--- | :--- | :---: | :--- |
| **Primary** | Moodify Purple | `#8A52F3` | 🟣 | 로고, 메인 액션 버튼(시작/전송), 활성 탭 |
| **Accent / Gradient** | Vivid Magenta / Pink | `#E040FB` | 🌺 | 메인 CTA 버튼 그라데이션 끝점, 하이라이트 뱃지 |
| **Calendar Active** | Active Purple | `#BA3EB8` | 🪻 | 캘린더 선택일 배경(원형 하이라이트) |
| **Text Primary** | Deep Indigo | `#2D1457` | 🍆 | 메인 타이틀, 헤더, 볼드 텍스트 |
| **Text Secondary** | Soft Purple Gray | `#7E6E90` | 🫐 | 서브 타이틀, 안내 문구, 날짜 헤더 |
| **Text Muted** | Placeholder Gray | `#A396B2` | 🔘 | 인풋 플레이스홀더, 비활성 텍스트 |

### 🌁 Background & Gradients
| Type | Gradient CSS Value | Description |
| :--- | :--- | :--- |
| **App Background** | `linear-gradient(180deg, #F5E9FF 0%, #FFF4F8 45%, #FFFFFF 75%, #F0FFF4 100%)` | 상단 라벤더에서 하단 소프트 민트로 자연스럽게 이어지는 오로라 무드 |
| **CTA Button** | `linear-gradient(90deg, #9C4FF7 0%, #EB3BA7 100%)` | '찾아보기 →' 메인 유도 버튼 그라데이션 |
| **Card / Surface** | `rgba(255, 255, 255, 0.72)` with `backdrop-filter: blur(16px)` | 반투명 글래스 효과의 카드 및 입력 컨테이너 |
| **Selected Chip** | `linear-gradient(135deg, #8A52F3 0%, #B86BFA 100%)` | 선택된 무드 칩 배경 |

---

## 🏷️ 2. Mood Tags Color Matrix (감정 칩 시스템)

각 상황과 감정 칩은 고유의 파스텔 배경 및 아이콘/텍스트 매칭을 가집니다.

| Mood Tag | Icon | Background | Text Color | Border / Accent |
| :--- | :---: | :---: | :---: | :---: |
| **러닝 / 에너지** | 🏃 | `#F3E8FF` (Soft Lavender) | `#7E22CE` | `rgba(126, 34, 206, 0.15)` |
| **새벽 감성** | 🌙 | `#EDE9FE` (Night Violet) | `#6D28D9` | `rgba(109, 40, 217, 0.15)` |
| **카페 / 일상** | ☕ | `#F5EEFA` (Warm Mauve) | `#5B21B6` | `rgba(91, 33, 182, 0.15)` |
| **봄 산책** | 🌸 | `#FCE7F3` (Pastel Pink) | `#BE185D` | `rgba(190, 24, 93, 0.15)` |
| **힐링 / 휴식** | 💫 / 🪽 | `#EDE9FE` (Lilac) | `#6D28D9` | `rgba(109, 40, 217, 0.15)` |
| **출근길** | 🥯 | `#FEF3C7` (Warm Amber) | `#B45309` | `rgba(180, 83, 9, 0.15)` |
| **퇴근 후** | 🌙 | `#EEF2FF` (Twilight Indigo) | `#4338CA` | `rgba(67, 56, 202, 0.15)` |

---

## 🔤 3. Typography (타이포그래피)

사용자의 감성을 부드럽게 감싸안는 라운드 계열 고딕 및 모던 산세리프 서체를 권장합니다.

- **Primary Font Family**: `'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Branding / Display Font**: `'Plus Jakarta Sans'`, `'Outfit'` (영문 타이틀 로고)

### Font Scale & Hierarchy
| Level | Font Size | Weight | Line Height | Tracking | Class / Target |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Hero Title** | `26px (1.625rem)` | 700 (Bold) | `1.3` | `-0.02em` | `"What's your mood now?"` |
| **Section Title**| `18px (1.125rem)` | 700 (Bold) | `1.4` | `-0.01em` | `"나의 음악 기록"`, 메인 헤더 |
| **Body Large** | `15px (0.9375rem)`| 500 (Medium)| `1.5` | `-0.01em` | 입력창 텍스트, 안내 서브타이틀 |
| **Body Medium** | `14px (0.875rem)` | 600 (SemiBold)| `1.4` | `0` | 곡명(Title), 검색 필터 칩 |
| **Body Small** | `12px (0.75rem)` | 400 (Regular)| `1.4` | `0` | 아티스트명, 타임스탬프, 도움말 |
| **Caption / Tag**| `11px (0.6875rem)`| 500 (Medium)| `1.3` | `+0.01em` | 캘린더 요일, 타임라인 태그 |

---

## 🧩 4. UI Components Specification (컴포넌트 가이드)

### 1) Main Input Card (상황 입력창)
- **Background**: `rgba(255, 255, 255, 0.8)`
- **Border Radius**: `24px` (`rounded-3xl`)
- **Border**: `1px solid rgba(255, 255, 255, 0.9)`
- **Box Shadow**: `0 10px 25px -5px rgba(138, 82, 243, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.02)`
- **Padding**: `20px 18px`

### 2) Filter Capsule Buttons (듣고 싶은 가수 / 장르)
- **Shape**: 필(Pill) 스타일 (`rounded-full`)
- **Background**: `rgba(255, 255, 255, 0.85)`
- **Border**: `1px solid rgba(230, 220, 248, 0.7)`
- **Typography**: `13px`, Text `#6E5A88`
- **Icon**: `Lucide-react` (`User`, `Music`, `Headphones`)

### 3) Mood Tag Chips (추천 무드 칩)
- **Shape**: 캡슐형 태그 (`rounded-full`, `padding: 6px 14px`)
- **Default State**: 파스텔톤 배경 (`#F3E8FF`), `transition: all 0.2s ease`
- **Hover/Active**: 살짝 커지는 스케일 효과 (`scale-[1.03]`), 퍼플 테두리 강조

### 4) Primary CTA Button (찾아보기 버튼)
- **Background**: `linear-gradient(90deg, #8A52F3 0%, #DE359D 100%)`
- **Height**: `56px`
- **Border Radius**: `22px`
- **Typography**: `16px`, Bold 700, Text `#FFFFFF`
- **Shadow**: `0 8px 20px -3px rgba(222, 53, 157, 0.35)`
- **Interaction**: 클릭 시 `active:scale-[0.98]` 피드백

### 5) Calendar & Timeline List (음악 기록 캘린더 및 리스트)
- **Calendar Grid**: 일~토 7컬럼 그리드, 폰트 `13px`
  - 일요일/공휴일: 핑크 레드 (`#E11D48`)
  - 토요일: 바이올렛 블루 (`#7C3AED`)
  - 평일: 다크 그레이 (`#374151`)
  - 당일/선택일: 보라색 원형 배경 (`#BA3EB8`), 흰색 텍스트
- **Timeline Card Item**:
  - `Background`: `rgba(255, 255, 255, 0.88)`
  - `Border Radius`: `18px`
  - `Padding`: `14px 16px`
  - `Item Structure`: [시간 `07:32`] + [도트 포인트 `●`] + [곡명 / 아티스트] + [무드 뱃지 우측 정렬]

---

## 📐 5. Layout & Spacing (레이아웃 규격)

- **Target Device Frame**: 모바일 뷰포트 기준 (`375px ~ 430px` 너비 권장)
- **Container Max-Width**: `max-w-md` (`448px`), 중앙 정렬 (`mx-auto`)
- **Screen Padding**:
  - Horizontal: `20px` (좌우 여백)
  - Top Safe Area: `16px` + 상태바 여백 (`pt-12`)
  - Bottom Safe Area: `32px` (`pb-8`)
- **Stack Spacing**: 컴포넌트 간 간격은 `12px` / `16px` / `24px` 8배수 기반 그리드 적용

---

## 💬 6. DJ & Curator Tone & Voice (보이스 앤 톤)

- **정체성**: 감성과 트렌드를 아는 나만의 센스 있는 플레이리스트 DJ
- **대화 톤**:
  - 따뜻하고 다정하며 격려하는 친구 같은 말투 (~해요, ~해볼까요?)
  - 단순 기능적 음악 정보 나열이 아닌, **'그 순간의 공기'**를 읽어주는 감성적 서술
  - 음악 큐레이션 시 장르와 BPM, 보컬의 질감을 감각적인 형용사로 설명