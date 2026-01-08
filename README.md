# DISBOT - DEV.NET Discord Bot 🎉

**Python → Node.js 완전 마이그레이션 완료!**

## 🚀 시작하기

### 환경 변수 설정

Docker Compose를 사용하는 경우 `stack.env` 파일에 다음 변수를 설정하세요:

```env
BOT_TOKEN=your_bot_token_here
CLIENT_ID=your_client_id_here
```

### 로컬 개발

```bash
# 의존성 설치
npm install

# 슬래시 커맨드 등록
node deploy-commands.js

# 봇 실행
npm start

# 개발 모드 (자동 재시작)
npm run dev
```

### Docker로 실행

```bash
# 이미지 빌드
docker-compose build

# 봇 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

## 📁 프로젝트 구조

```
DISBOT/
├── index.js              # 메인 엔트리 포인트
├── config.js             # 설정 파일
├── deploy-commands.js    # 슬래시 커맨드 등록 스크립트
├── package.json
├── Dockerfile
├── docker-compose.yml
├── events/               # 이벤트 핸들러
│   ├── ready.js
│   ├── interactionCreate.js
│   ├── guildMemberAdd.js
│   └── ...
└── commands/             # 슬래시 커맨드
    ├── general/          # 일반 명령어
    ├── admin/            # 관리자 명령어
    ├── music/            # 음악 명령어
    └── ...
```

## ⚡ 주요 기능

- ✅ 일반 명령어 (핑, 정보, 유저정보, 서버정보 등)
- ✅ 관리 명령어 (추방, 밴, 타임아웃, 경고 등)
- ✅ 음악 시스템 (play-dl 사용)
- ✅ 이벤트 로깅 (메시지 삭제/수정, 멤버 입퇴장, 음성 채널 등)

## 🎵 음악 기능

`play-dl` 라이브러리를 사용한 안정적인 음악 재생!

```
/music action:on              - 봇을 음성 채널에 입장 (관리자)
/music action:play url:링크    - 음악 재생
/music action:skip            - 다음 곡
/music action:queue           - 재생목록 확인
/music action:off             - 봇 퇴장 (관리자)
```

## 👨‍💻 개발자

mokea - [https://mokea.dev](https://mokea.dev)