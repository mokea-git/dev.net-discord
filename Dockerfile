# Node.js 공식 이미지 사용
FROM node:20-slim

# ffmpeg 설치 (음악 기능에 필요)
RUN apk add --no-cache ffmpeg python3 make g++

# 작업 디렉토리 설정
WORKDIR /app

# package.json과 package-lock.json 복사
COPY package*.json ./

# 의존성 설치
RUN npm install --production

# 소스 코드 복사
COPY . .

# 봇 실행
CMD ["node", "index.js"]