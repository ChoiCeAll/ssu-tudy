FROM node:22.1.0

WORKDIR /app

# 의존성 설치
COPY package*.json ./
RUN npm install

# 소스 코드 복사 (src 포함 전체)
COPY . .

# Vite 개발 서버 실행
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
