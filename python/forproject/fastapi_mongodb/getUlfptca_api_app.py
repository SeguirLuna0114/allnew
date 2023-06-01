from fastapi import FastAPI #FastAPI와 MongoDB를 사용하여 API를 구현
from pymongo import mongo_client
from pymongo import InsertOne
import pydantic
import requests
from bson.objectid import ObjectId
import os.path
import requests
import json
import pandas as pd 
import numpy as np
from datetime import datetime, timedelta
from typing import Union
from bson.objectid import ObjectId

pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str # ENCODERS_BY_TYPE: pydantic의 JSON 인코더가 MongoDB [ObjectId]를 문자열(str)로 인코딩할 수 있도록 설정

app = FastAPI() #FastAPI 애플리케이션을 생성

#MongoDB Atlas 접속시 비밀정보를 로드하고 가져오기 위한 함수 정의
BASE_DIR = os.path.dirname(os.path.dirname(os.path.relpath("./"))) #재 스크립트의 상위 디렉토리 경로를 BASE_DIR 변수에 할당
secret_file = os.path.join(BASE_DIR, '../../secret.json') #BASE_DIR과 상대 경로를 조합하여 비밀 정보가 저장된 파일의 경로를 secret_file 변수에 할당

with open(secret_file) as f: #secret_file을 열고 파일 객체 f를 생성
    secrets = json.loads(f.read()) #파일의 내용을 읽어와 JSON 형식으로 디코딩하여 secrets 변수에 할당
def get_secret(setting, secrets=secrets): #비밀 정보를 가져오기 위한 함수
    try:
        return secrets[setting] #setting 매개변수로 설정 이름을 받음 -> secrets 딕셔너리에서 해당 설정 이름에 해당하는 값을 찾아 반환
    except KeyError: #secrets에 존재하지 않는 경우
        errorMsg = "Set the {} environment variable.".format(setting)
        return errorMsg #환경 변수를 설정하라는 오류 메시지를 반환

#정의한 get_secret()함수 사용 => Mongodb 호스트이름, 사용자이름, 비밀번호를 가져와 MongoDB에 연결
#HOSTNAME = get_secret("ATLAS_Hostname")
#USERNAME = get_secret("ATLAS_Username")
#PASSWORD = get_secret("ATLAS_Password")
#호스트 이름, 사용자 이름, 비밀번호를 사용하여 mongo_client.MongoClient를 초기화 -> 해당 클라이언트를 사용하여 MongoDB에 연결
#client = mongo_client.MongoClient(f'mongodb+srv://{USERNAME}:{PASSWORD}@{HOSTNAME}')
#print('Connected to Mongodb ATLAS....') #연결에 성공

#MongoDB Ubuntu 접속
HOSTNAME = '192.168.1.189:27017'
#해당 클라이언트를 사용하여 MongoDB에 연결
client = mongo_client.MongoClient(f'mongodb://{HOSTNAME}')
print('Connected to Mongodb Ubuntu....') #연결에 성공하면 "Connected to Mongodb...." 메시지를 출력

# 이전에 초기화한 client 객체를 사용=>MongoDB의 'test' 데이터베이스에 접속하고, 'testdb' 컬렉션을 선택
mydb = client['test'] # 'test' 데이터베이스에 접속
mycol = mydb['AllUlfptcaAlarms'] # 컬렉션을 선택

# 애플리케이션 상태 확인
@app.get('/')
async def healthCheck():
    return "OK_readytoRequest"

#mongocollectionlist: 2018~2023ParticleDatas, AllParticleDatas
#FabData Collection: FabCapa_All_Trans, FabCapa_Trans
@app.get('/getMongoColData_30')
async def getMongoColData_30(collectionName: str = None):
    get_mycol = mydb[collectionName] # 컬렉션을 선택
    return list(get_mycol.find().limit(30))

@app.get('/getMongoColData_ALL')
async def getMongoColData_ALL(collectionName: str = None):
    get_mycol = mydb[collectionName] # 컬렉션을 선택
    return list(get_mycol.find())

@app.get('/dropMongoCol')
async def dropMongoCol(collectionName: str = None):
    drop_mycol = mydb[collectionName] #drop 컬렉션 선택
    drop_mycol.drop()
    return 'Drop selected collection...'

#url에 http get요청을 보내고, 응답을 딕셔너리객체로 변환하는 함수
def getRequestData(url):
    try:
        response = requests.get(url)  # URL에 HTTP GET 요청을 보냄
        response.raise_for_status()  # 2xx 이외의 상태 코드가 반환되면 예외 발생
        contents = response.text  # 응답에서 JSON 형식의 문자열 추출
        data_dict = json.loads(contents)  # JSON 문자열을 딕셔너리 객체로 변환
        return data_dict
    except requests.exceptions.RequestException as e:
        print(f"{url}에서 데이터를 요청하는 중 오류가 발생했습니다: {str(e)}")
        return None

#공공데이터포털에서 '한국환경공단_에어코리아_미세먼지 경보 발령 현황'데이터를 가져와 JSON 형식으로 저장
@app.get('/getUlfptcaAlarmInfo_year') #연도별 데이터 끌어오게 하는 방법
def getUlfptcaAlarmInfo_year(year: int = None):
    if year is None: # year 변수가 None인 경우 현재 년도를 할당하도록 함
        now = datetime.now()
        current_year = now.year
        year = current_year
        #return year
    if year < 2018 or year > 2023:
        return '입력한 연도 관련 데이터가 존재하지 않습니다.'

    end_point = 'https://apis.data.go.kr/B552584/UlfptcaAlarmInqireSvc/getUlfptcaAlarmInfo'
    # API 호출에 필요한 파라미터들을 저장하기 위함
    parameters = ''
    parameters += '?serviceKey=' + get_secret("data_apiKey")
    parameters += '&returnType=json'
    parameters += '&numOfRows=500'
    parameters += '&pageNo=1'
    parameters += '&year=' + str(year) #측정연도
    
    url = end_point + parameters

    response = getRequestData(url)# getRequestUrl(url) 함수를 사용 => 생성한 URL로 API 요청을 보내고, 응답을 받음
    if (response == None):  # 응답이 None인 경우, None을 반환
        return {'error': 'API 요청에 실패하였습니다.'}
    else:  # 응답이 None이 아닌 경우
        print(f"{year}년도 데이터")
        return response  # 응답을 JSON 형식으로 변환하여 반환

@app.get('/getUlfptcaAlarmInfo_ALL') #all을 입력할 경우, 모든연도에 해당하는 데이터를 끌어오는 코드를 알려줘
def getUlfptcaAlarmInfo_ALL(year: Union[int, str] = None):
    if isinstance(year, int):
        return getUlfptcaAlarmInfo_year(year)
    
    if isinstance(year, str) and year.lower() == 'all':
        response = []
        for y in range(2018, 2024): #2018~2024
            result = getUlfptcaAlarmInfo_year(y)
            if (result['response']['header']['resultCode'] == '00'):
                totalCount = result['response']['body']['totalCount']
                print('데이터 총 개수 : ', totalCount)
                for item in result['response']['body']['items']:
                    response.append(item) #추가되는 연도별 데이터를 jsonResponse에 추가
                if totalCount == 0:
                    break
            else:
                break
        return response

def makeJSON(year: str = None):
    if year == 'all':
        result = getUlfptcaAlarmInfo_ALL('all')
    else:
        try:
            year = int(year)
            result = getUlfptcaAlarmInfo_year(year)
        except ValueError:
            return {'error': 'Invalid year format'}

    if result is not None:
        with open('data.json', 'w', encoding='utf-8') as file:
                json.dump(result, file, ensure_ascii=False, indent=4)
        return {'message': 'JSON file created successfully'}
    else:
        return {'message': 'Failed to fetch data'}

#mongodb에 Import
@app.get('/mongoImport_JSON')
async def mongoImport_JSON():   
    for year in range(2018, 2024):
        collection = db['{}ParticleDataTests'.format(year)]  # 컬렉션 이름 지정
        makeJSON(year)
    bulk_operations = []
    # 대용량 데이터를 작은 배치로 분할하여 Bulk Write 작업 생성
    for data in json_data:
        bulk_operations.append(InsertOne(data))
        if len(bulk_operations) >= 1000:  # 작은 배치 크기 설정
            collection.bulk_write(bulk_operations, ordered=False)
            bulk_operations = []
    # 남은 데이터에 대해 Bulk Write 작업 실행
    if bulk_operations:
        collection.bulk_write(bulk_operations, ordered=False)
    print(data.json, 'MongoDB imported~!!')
    return {'message': 'Import successful'}

#mongodb에 Export
@app.get('/mongoExport_csv')
async def mongoExport_csv(collectionName: str = None):
    Exportcollection = mydb[collectionName]
    csv_File = 'ExportedCSVFile.csv'
    data = Exportcollection.find()

    with open(csv_File, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        field_names = list(data[0].keys()) # 헤더 작성
        writer.writerow(field_names)

        for document in data: # 데이터 작성
            writer.writerow(list(document.values()))
    print("CSV 파일로 내보내기가 완료되었습니다.")
    return {'message': 'CSV file exported successfully.'}



#MakePlot and Dataframe_Annual
@app.get('/getUlfptca_DataFrame_Annual')
async def getUlfptca_DataFrame_Annual(city: str = None):
    result = []   
    plt.rcParams['font.family'] = 'Malgun Gothic'

    for year in range(2018, 2024):
        end_point = 'https://apis.data.go.kr/B552584/UlfptcaAlarmInqireSvc/getUlfptcaAlarmInfo'
    
        parameters = ''
        parameters += '?serviceKey=' + get_secret("data_apiKey")
        parameters += '&returnType=json'
        parameters += '&numOfRows=500'
        parameters += '&pageNo=1'
        parameters += '&year=' + str(year)
        
        url = end_point + parameters
        print(url)
        response = requests.get(url) #url주소에 HTTP GET요청을 보내고, 서버로부터 응답 받아옴 -> response객체로 반환됨
  
        contents = response.text #response 객체에서 JSON 형식의 데이터를 문자열로 추출
        data_dict = json.loads(contents) #json.loads() 함수를 호출하여 이를 딕셔너리 객체로 변환

        for item in data_dict['response']['body']['items']:
            result.append(item)

    selected_df = DataFrame(result, columns=['districtName', 'issueDate', 'issueGbn', 'issueVal', 'itemCode', 'moveName', 'sn'])
    selected_df = selected_df.set_index('sn')
    selected_df['issueVal'] = selected_df['issueVal'].astype(int)
    selected_df['issueDate'] = pd.to_datetime(selected_df['issueDate'])
    selected_df.fillna(0, inplace=True)

    #citylist = selected_df['districtName'].unique()
    listData = ['PM25', 'PM10']
    result_data = []
    for PMdata in listData:
        print(f'{city}의 {PMdata} 농도 추세')
        df_PMdata = selected_df.loc[(selected_df['districtName'] == city) & (selected_df['itemCode'] == PMdata), ['itemCode', 'issueDate', 'issueVal']]
        for year in range(2018, 2024):
            print(f'{year}년도 데이터')
            df_YearPMdata = df_PMdata[df_PMdata['issueDate'].dt.year == year]
            avg_issueVal_year = np.round(df_YearPMdata['issueVal'].mean(skipna=True))
            print(avg_issueVal_year)
            print('-' * 40)
            result_data.append([city, PMdata, year, avg_issueVal_year])
    Df_Result = pd.DataFrame(result_data, columns=['발령 지역 명', '미세먼지 항목 구분', '발령 연도', '평균 미세먼지 농도'])
    print(Df_Result)

    return Df_Result






if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)