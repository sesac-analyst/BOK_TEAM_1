## 데이터 수집 및 초기 로드
CSV 데이터:

News_U.csv: '금리' 키워드의 뉴스 기사 데이터
cleaned_bond.csv: 채권 데이터
call_rates_3.csv: 콜 금리 데이터
cleaned_MPB.csv: 통화정책회의 의사록(Monetary Policy Board, MPB) 데이터

위 데이터들을 결합하여 통합 데이터프레임(df_corp)을 생성

## 데이터 레이블링

각 데이터의 출처와 날짜를 기준으로 주요 키(primary key)를 생성
콜금리 데이터를 기반으로 당일 기준금리 변동 여부에 따라 '1', '0', 또는 결측치(NaN)로 레이블을 지정

## 토큰화 및 정규화
eKoNLPy와 Mecab을 사용하여 텍스트 데이터를 토큰화하고, 각 단어의 품사 정보를 추가


## 정규화
n-그램 분석에 필요한 품사를 필터링

필터링 품사:

NNG (일반명사)
VA (형용사)
MAG (일반부사)
VV (동사)
VCN (부정 지정사)