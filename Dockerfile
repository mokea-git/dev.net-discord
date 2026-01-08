# Node.js 공식 이미지 사용
FROM node:20-slim

# ffmpeg 설치 (음악 기능에 필요)
RUN apt-get update && apt-get install -y ffmpeg python3 make g++ && rm -rf /var/lib/apt/lists/*

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