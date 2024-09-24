import torch
import os
from PIL import Image
import torchvision.transforms as transforms
import torch.nn as nn
from torchvision import models
from torchvision.models import EfficientNet_B0_Weights
from django.conf import settings  # settings.py에서 BASE_DIR 가져오기


class_names = [
    "beef carpaccio", "beef tartare", "beet salad", "beignets", "bibimbap", "bread pudding",
    "breakfast burrito", "bruschetta", "caesar salad", "cannoli", "caprese salad", "carrot cake",
    "ceviche", "cheese plate", "cheesecake", "chicken curry", "chicken quesadilla", "chicken wings",
    "chocolate cake", "chocolate mousse", "churros", "clam chowder", "club sandwich", "crab cakes",
    "creme brulee", "croque madame", "cup cakes", "deviled eggs", "donuts", "dumplings",
    "edamame", "eggs benedict", "escargots", "falafel", "filet mignon", "fish and chips",
    "foie gras", "french fries", "french onion soup", "french toast", "fried calamari", "fried rice",
    "frozen yogurt", "garlic bread", "gnocchi", "greek salad", "grilled cheese sandwich",
    "grilled salmon", "guacamole", "gyoza", "hamburger", "hot and sour soup", "hot dog",
    "huevos rancheros", "hummus", "ice cream", "lasagna", "lobster bisque", "lobster roll sandwich",
    "macaroni and cheese", "macarons", "miso soup", "mussels", "nachos", "omelette",
    "onion rings", "oysters", "pad thai", "paella", "pancakes", "panna cotta", "peking duck",
    "pho", "pizza", "pork chop", "poutine", "prime rib", "pulled pork sandwich", "ramen",
    "ravioli", "red velvet cake", "risotto", "samosa", "sashimi", "scallops", "seaweed salad",
    "shrimp and grits", "spaghetti bolognese", "spaghetti carbonara", "spring rolls", "steak",
    "strawberry shortcake", "sushi", "tacos", "takoyaki", "tiramisu", "tuna tartare",
    "waffles", "가지볶음", "간장게장", "갈비구이", "갈비찜", "갈비탕", "갈치구이", "갈치조림",
    "감자전", "감자조림", "감자채볶음", "감자탕", "갓김치", "건새우볶음", "경단", "계란국",
    "계란말이", "계란찜", "계란후라이", "고등어구이", "고등어조림", "고사리나물", "고추장진미채볶음",
    "고추튀김", "곰탕_설렁탕", "곱창구이", "곱창전골", "과메기", "김밥", "김치볶음밥", "김치전",
    "김치찌개", "김치찜", "깍두기", "깻잎장아찌", "꼬막찜", "꽁치조림", "꽈리고추무침", "꿀떡",
    "나박김치", "누룽지", "닭갈비", "닭계장", "닭볶음탕", "더덕구이", "도라지무침", "도토리묵",
    "동그랑땡", "동태찌개", "된장찌개", "두부김치", "두부조림", "땅콩조림", "떡갈비", "떡국_만두국",
    "떡꼬치", "떡볶이", "라면", "라볶이", "막국수", "만두", "매운탕", "멍게", "메추리알장조림",
    "멸치볶음", "무국", "무생채", "물냉면", "물회", "미역국", "미역줄기볶음", "배추김치",
    "백김치", "보쌈", "부추김치", "북엇국", "불고기", "비빔냉면", "비빔밥", "산낙지", "삼겹살",
    "삼계탕", "새우볶음밥", "새우튀김", "생선전", "소세지볶음", "송편", "수육", "수정과", "수제비",
    "숙주나물", "순대", "순두부찌개", "시금치나물", "시래기국", "식혜", "알밥", "애플파이",
    "애호박볶음", "약과", "약식", "양념게장", "양념치킨", "어묵볶음", "연근조림", "열무국수",
    "열무김치", "오이소박이", "오징어채볶음", "오징어튀김", "우엉조림", "유부초밥", "육개장",
    "육회", "잔치국수", "잡곡밥", "잡채", "장어구이", "장조림", "전복죽", "젓갈", "제육볶음",
    "조개구이", "조기구이", "족발", "주꾸미볶음", "주먹밥", "짜장면", "짬뽕", "쫄면", "찜닭",
    "총각김치", "추어탕", "칼국수", "코다리조림", "콩국수", "콩나물국", "콩나물무침", "콩자반",
    "파김치", "파전", "편육", "폭립", "피자", "한과", "해물찜", "호박전", "호박죽", "홍어무침",
    "황태구이", "회무침", "후라이드치킨", "훈제오리"
]

# 하이퍼파라미터 설정
img_height, img_width = 224, 224
num_classes = 250  # 학습한 클래스 수에 맞춰야 합니다.

# GPU 사용 설정
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'New_best_efficientnet_food_classifier_v100.pth')

# 사전 학습된 모델 불러오기
model = models.efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)

# 모델의 가중치 로드 (GPU에 로드)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
# 모델의 가중치 로드 (GPU에 로드)
# model.load_state_dict(torch.load('New_best_efficientnet_food_classifier_v100.pth'))

model.to(device)  # 모델을 GPU로 이동
model.eval()

def predict_food(image_path):
    # 이미지 전처리
    test_transform = transforms.Compose([
        transforms.Resize((img_height, img_width)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # 이미지 열기
    image = Image.open(image_path)

    # 이미지가 RGB가 아닌 경우 RGB로 변환
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # 이미지 전처리 적용
    image = test_transform(image).unsqueeze(0)  # 배치 차원 추가
    image = image.to(device)  # 이미지를 GPU로 이동

    # 모델에 이미지 입력
    with torch.no_grad():
        output = model(image)

    # 첫 번째 예측된 클래스와 확률만 추출
    _, predicted_idx = torch.max(output, 1)
    predicted_class = class_names[predicted_idx.item()]

    return predicted_class

