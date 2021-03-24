# Finance-Modeling

### 0. Goal
20일 동안 주가가 120일 이평선 위에 있는 종목 선별

### 1. Process
- 키움API에서 유가증권시장 종목 일봉 데이터 호출
- 120일 동안의 주가 데이터 여부 확인
- 120일 이평선 그리기
- 20일 동안 주가가 120일 이평선 위에 있는 종목 선별

### 2. Model
- 120일 단순 이동평균선 = 120일 종가 데이터 총합 / 120

### 3. Result
- 투자 최소 조건을 만족시키는 종목 선별
