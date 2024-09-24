
import pandas as pd
import requests
import re

# 엑셀 데이터 로드
food_data = pd.read_csv('health/filtered_food_data.csv')

usda_api_key = "5kOrX3iQ6KoatbYkBegcLBWhsg8v7OUbm0inhuzN"
usda_base_url = "https://api.nal.usda.gov/fdc/v1/foods/search"

# 한글 체크 함수
def is_korean(text):
    return bool(re.search('[가-힣]', text))

# 한국어 음식 영양성분을 엑셀에서 가져오기
def get_korean_food_info(food_name, weight):
    print(food_name)
    food_info = food_data[food_data['식품명'] == food_name]
    print('aa', food_info)
    if not food_info.empty:
        # 100g 당 영양성분 가져오기
        calories_per_100g = food_info['칼로리'].values[0]
        protein_per_100g = food_info['단백질'].values[0]
        fat_per_100g = food_info['지방'].values[0]
        carbs_per_100g = food_info['탄수화물'].values[0]

        # 사용자가 입력한 무게에 맞춰 계산
        scale_factor = weight / 100.0
        calories = calories_per_100g * scale_factor
        protein = protein_per_100g * scale_factor
        fat = fat_per_100g * scale_factor
        carbs = carbs_per_100g * scale_factor

        return {
            'calories': round(calories, 2),
            'protein': round(protein, 2),
            'fat': round(fat, 2),
            'carbs': round(carbs, 2)
        }
    return None

# 영어 음식 영양성분을 USDA API에서 가져오기
def get_english_food_info(food_name, weight):
    params = {
        "query": food_name,
        "api_key": usda_api_key,
        "dataType": ["Branded", "Survey (FNDDS)", "Foundation"]
    }

    # USDA API 요청
    response = requests.get(usda_base_url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"USDA API 요청 실패: {response.status_code}")
    
    data = response.json()

    if not data.get('foods'):
        raise ValueError(f"'{food_name}'에 대한 영양 정보를 찾을 수 없습니다.")

    # 첫 번째 음식 데이터를 가져옴
    nutrition_info = data['foods'][0]
    
    # 필요한 영양소 정보 추출
    nutrients = {nutrient['nutrientName']: nutrient['value'] for nutrient in nutrition_info.get('foodNutrients', [])}

    # 100g당 영양성분 정보 추출
    calories_per_100g = nutrients.get('Energy', 0)  # kcal
    protein_per_100g = nutrients.get('Protein', 0)  # g
    fat_per_100g = nutrients.get('Total lipid (fat)', 0)  # g
    carbs_per_100g = nutrients.get('Carbohydrate, by difference', 0)  # g

    # 사용자가 입력한 무게에 맞춰 계산
    scale_factor = weight / 100.0
    calories = calories_per_100g * scale_factor
    protein = protein_per_100g * scale_factor
    fat = fat_per_100g * scale_factor
    carbs = carbs_per_100g * scale_factor

    # 결과 반환
    return {
        'calories': round(calories, 2),
        'protein': round(protein, 2),
        'fat': round(fat, 2),
        'carbs': round(carbs, 2)
    }

# 음식 영양성분 정보 가져오기
def get_nutritional_info(food_name, weight):
    if is_korean(food_name):
        # 한국어 음식인 경우 엑셀에서 영양성분 가져오기
        return get_korean_food_info(food_name, weight)
    else:
        # 영어 음식인 경우 USDA API에서 영양성분 가져오기
        return get_english_food_info(food_name, weight)
