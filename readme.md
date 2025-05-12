# SSU-TUDY 📚

SSU-TUDY는 스터디 그룹을 만들고, 관리하고, 참여할 수 있는 웹 애플리케이션입니다.  
Flask + Vue.js + MySQL을 기반으로 구성된 풀스택 프로젝트입니다.

## 🚀 실행 방법 (개발용)

### 1. `.env` 설정

`.env.example` 파일을 참고하여 `.env` 파일을 생성하고 필요한 값을 채워주세요:

### 2. .env 예시

```env
# .env 예시
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=ssu_tudy
MYSQL_USER=ssu
MYSQL_PASSWORD=ssupw

---

### ❓ `.env.example`을 자동으로 `.env`로 바꾸냐?

> **아니요**, 자동으로 변환되지 않습니다.

`.env.example`은 단지 예시 파일일 뿐이고, **사용자가 수동으로 복사해서 `.env`로 바꿔야 합니다.**

#### ✅ 보통 이런 명령어를 사용합니다:

```bash
cp .env.example .env

## 도커 실행 방법

docker-compose up --build

백엔드: http://localhost:5000

프론트엔드: http://localhost:5173