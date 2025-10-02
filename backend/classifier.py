import torch
from razdel import sentenize
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from collections import defaultdict
from typing import Dict, Any

topics = [
    "Дебетовые карты", "Кредитные карты", "Акции и бонусы",
    "Кредиты наличными", "Вклады", "Ипотека", "Автокредиты",
    "Рефинансирование кредитов", "Рефинансирование ипотеки",
    "Обмен валют", "Условия", "Денежные переводы",
    "Мобильное приложение", "РКО", "Эквайринг", "Обслуживание",
    "Дистанционное обслуживание", "Техподдержка и чат", "Другие услуги"
]

# ----------- классификатор топиков -----------
class Classifier(torch.nn.Module):
    def __init__(self, embed_dim, num_labels):
        super().__init__()
        self.fc1 = torch.nn.Linear(embed_dim, 128)
        self.relu = torch.nn.ReLU()
        self.fc2 = torch.nn.Linear(128, num_labels)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        return self.fc2(x)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Подгрузка моделей один раз
embedder = SentenceTransformer("distiluse-base-multilingual-cased-v1")
topic_model = Classifier(embed_dim=512, num_labels=len(topics)).to(device)
topic_model.load_state_dict(torch.load("models/model3.pth", map_location=device))
topic_model.eval()

sentiment_model_checkpoint = 'cointegrated/rubert-tiny-sentiment-balanced'
tokenizer = AutoTokenizer.from_pretrained(sentiment_model_checkpoint)
sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_checkpoint).to(device)

def predict_topics(text: str, threshold: float = 0.5):
    emb = embedder.encode([text])
    emb = torch.tensor(emb, dtype=torch.float).to(device)
    with torch.no_grad():
        logits = topic_model(emb)
        probs = torch.sigmoid(logits).cpu().numpy()[0]
    return [t for t, p in zip(topics, probs) if p > threshold]

def get_sentiment(text: str) -> str:
    with torch.no_grad():
        inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True).to(device)
        logits = sentiment_model(**inputs).logits
        probs = torch.sigmoid(logits).cpu().numpy()[0]
    return sentiment_model.config.id2label[probs.argmax()]



async def classify_review(text: str) -> Dict[str, Any]:
    sentences = [s.text for s in sentenize(text)]
    topic_fragments_list = defaultdict(list)

    for sent in sentences:
        found = predict_topics(sent)
        for topic in found:
            topic_fragments_list[topic].append(sent)

    topic_fragments = {}
    for topic, frags in topic_fragments_list.items():
        combined = " ".join(frags)
        sentiment = get_sentiment(combined)
        topic_fragments[topic] = {
            "fragments": frags,
            "sentiment": sentiment
        }

    overall_sentiment = get_sentiment(text)

    return {
        "sentiment": overall_sentiment,
        "topics": list(topic_fragments_list.keys()),
        "topic_fragments": topic_fragments
    }
