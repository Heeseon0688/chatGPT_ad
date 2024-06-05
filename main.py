import openai
from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient

openai.api_key = '비밀'

app = FastAPI()

# MongoDB 연결
url = "비밀"
client = MongoClient(url)

database = client['aiproject']
collection = database['ad']

class AdGenerator:
    def __init__(self, engine='gpt-3.5-turbo'):
        self.engine = engine

    def using_engine(self, prompt):
        system_instruction = 'assistant는 마케팅 문구 작성 도우미로 동작한다. user의 내용을 참고하여 마케팅 문구를 작성해라'
        messages = [{'role':'system', 'content': system_instruction},
                    {'role': 'user', 'content': prompt}]
        response = openai.chat.completions.create(model=self.engine, messages=messages)
        result = response.choices[0].message.content.strip()
        return result

    def generate(self, product_name, details, tone_and_manner):
        prompt = f'제품 이름: {product_name}\n주요 내용: {details}\n광고 문구의 스타일: {tone_and_manner} 위 내용을 참고하여 마케팅 문구를 만들어라'
        result = self.using_engine(prompt=prompt)
        return result

class Product(BaseModel):
    product_name: str
    details: str
    tone_and_manner: str

@app.post('/create_ad')
async def create_ad(product: Product):
    # print(product)
    ad_generator = AdGenerator()
    ad = ad_generator.generate(product_name=product.product_name,
                               details=product.details,
                               tone_and_manner=product.tone_and_manner)

    # MongoDB에 데이터 저장
    ad_data = {
        "product_name": product.product_name,
        "details": product.details,
        "tone_and_manner": product.tone_and_manner
        # "ad": ad
    }
    collection.insert_one(ad_data)

    # 저장된 내용 조회하여 JSON 형식으로 반환
    ads_list = list(collection.find({}, {"_id": 0}))  # 모든 광고 조회
    return {"ads": ads_list}
    # return {'ad': ad}



