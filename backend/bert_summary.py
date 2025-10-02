from transformers import pipeline
from typing import List, Dict
from deep_translator import GoogleTranslator
import re



class TopicSentimentSummarizer:
    """Суммаризатор отзывов по темам и тональности с использованием BART и перевода"""

    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        """
        Инициализация суммаризатора

        Args:
            model_name: Название модели для суммаризации
        """
        self.summarizer = pipeline("summarization", model=model_name)
        self.translator = GoogleTranslator(source='auto', target='en')
        self.translator_ru = GoogleTranslator(source='en', target='ru')

    def translate_text(self, text: str, to_english: bool = True) -> str:
        """
        Переводит текст между русским и английским

        Args:
            text: Текст для перевода
            to_english: True для перевода на английский, False на русский

        Returns:
            Переведенный текст
        """
        try:
            if not text.strip():
                return text

            translator = self.translator if to_english else self.translator_ru
            return translator.translate(text)
        except Exception:
            return text

    def translate_fragments_to_english(self, fragments: List[str]) -> List[str]:
        """
        Переводит список фрагментов на английский язык

        Args:
            fragments: Список фрагментов на русском

        Returns:
            Список фрагментов на английском
        """
        return [self.translate_text(fragment, to_english=True) for fragment in fragments]

    def extract_fragments_by_topic_sentiment(
            self, reviews: List[Dict], topic: str, sentiment: str
    ) -> List[str]:
        """
        Извлекает фрагменты по определенной теме и тональности из всех отзывов

        Args:
            reviews: Список отзывов
            topic: Название темы
            sentiment: Тип тональности ("positive", "negative", "neutral")

        Returns:
            Список фрагментов текста
        """
        all_fragments = []
        for review in reviews:
            topic_data = review.get('topic_fragments', {}).get(topic)
            if topic_data and topic_data.get('sentiment') == sentiment:
                all_fragments.extend(topic_data.get('fragments', []))
        return all_fragments

    def summarize_fragments(
            self, fragments: List[str], max_length: int = 130, min_length: int = 30
    ) -> str:
        """
        Суммаризирует список фрагментов с переводом RU -> EN -> RU

        Args:
            fragments: Список текстовых фрагментов на русском
            max_length: Максимальная длина суммаризации
            min_length: Минимальная длина суммаризации

        Returns:
            Суммаризированный текст на русском
        """
        if not fragments:
            return "Нет фрагментов для суммаризации"

        english_fragments = self.translate_fragments_to_english(fragments)
        combined_english_text = " ".join(english_fragments)

        if len(combined_english_text.split()) < min_length:
            return self.translate_text(combined_english_text, to_english=False)

        try:
            summary = self.summarizer(
                combined_english_text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            english_summary = summary[0]['summary_text']
            return self.translate_text(english_summary, to_english=False)
        except Exception as e:
            return f"Ошибка при суммаризации: {str(e)}"

    def get_all_topics(self, reviews: List[Dict]) -> set:
        """
        Получает все уникальные темы из всех отзывов

        Args:
            reviews: Список отзывов

        Returns:
            Множество уникальных тем
        """
        topics = set()
        for review in reviews:
            topics.update(review.get('topics_found', []))
            topics.update(review.get('topic_fragments', {}).keys())
        return topics

    def summarize_by_topic_and_sentiment(
            self, reviews: List[Dict], max_length: int = 130, min_length: int = 30
    ) -> Dict[str, Dict[str, Dict]]:
        """
        Создает суммаризацию для всех тем по типам тональности

        Args:
            reviews: Список отзывов
            max_length: Максимальная длина суммаризации
            min_length: Минимальная длина суммаризации

        Returns:
            Словарь с результатами суммаризации по темам и тональности
        """
        results = {}
        topics = self.get_all_topics(reviews)
        sentiments = ["positive", "negative", "neutral"]

        for topic in topics:
            results[topic] = {}
            for sentiment in sentiments:
                all_fragments = self.extract_fragments_by_topic_sentiment(
                    reviews, topic, sentiment
                )

                if all_fragments:
                    summary = self.summarize_fragments(all_fragments, max_length, min_length)
                    results[topic][sentiment] = {
                        'summary': summary,
                        'fragments_count': len(all_fragments),
                        'reviews_count': self._count_reviews_with_topic_sentiment(
                            reviews, topic, sentiment
                        ),
                        'original_fragments': all_fragments
                    }
                else:
                    results[topic][sentiment] = {
                        'summary': f"Нет {sentiment} отзывов по теме '{topic}'",
                        'fragments_count': 0,
                        'reviews_count': 0,
                        'original_fragments': []
                    }

        return results

    def summarize_single_review(
            self, review: Dict, max_length: int = 15, min_length: int = 3
    ) -> Dict[str, Dict[str, str]]:
        """
        Создает краткую суммаризацию (2-3 слова) для каждой темы в одном отзыве

        Args:
            review: Отзыв с полями id, original_text, classification
            max_length: Максимальная длина суммаризации в токенах
            min_length: Минимальная длина суммаризации в токенах

        Returns:
            Словарь с краткими суммаризациями по темам
            Формат: {topic: {"summary": "текст", "sentiment": "positive/negative/neutral"}}
        """
        results = {}
        topic_fragments = review.get('classification', {}).get('topic_fragments', {})

        if not topic_fragments:
            return results

        for topic, data in topic_fragments.items():
            fragments = data.get('fragments', [])
            sentiment = data.get('sentiment', 'neutral')

            if not fragments:
                results[topic] = {'summary': '', 'sentiment': sentiment}
                continue

            english_fragments = self.translate_fragments_to_english(fragments)
            combined_english_text = " ".join(english_fragments)

            try:
                summary = self.summarizer(
                    combined_english_text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                english_summary = summary[0]['summary_text']
                russian_summary = self.translate_text(english_summary, to_english=False)
                russian_summary = self._truncate_to_keywords(russian_summary)

                results[topic] = {'summary': russian_summary, 'sentiment': sentiment}
            except Exception:
                results[topic] = {
                    'summary': self._extract_keywords_fallback(fragments),
                    'sentiment': sentiment
                }

        return results

    def _truncate_to_keywords(self, text: str, max_words: int = 3) -> str:
        """
        Укорачивает текст до max_words значимых слов

        Args:
            text: Исходный текст
            max_words: Максимальное количество слов

        Returns:
            Укороченный текст
        """
        cleaned_text = re.sub(r'[^\w\s]', '', text)
        words = cleaned_text.split()

        stop_words = {
            'и', 'в', 'на', 'с', 'по', 'для', 'о', 'об', 'от', 'к', 'у',
            'а', 'но', 'да', 'же', 'ли', 'бы', 'что', 'как', 'так', 'это',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'
        }

        meaningful_words = [w for w in words if w.lower() not in stop_words]

        if len(meaningful_words) < max_words:
            return ' '.join(words[:max_words])

        return ' '.join(meaningful_words[:max_words])

    def _extract_keywords_fallback(self, fragments: List[str], max_words: int = 3) -> str:
        """
        Извлекает ключевые слова из фрагментов (запасной вариант)

        Args:
            fragments: Список фрагментов
            max_words: Максимальное количество слов

        Returns:
            Строка с ключевыми словами
        """
        combined_text = ' '.join(fragments)
        words = combined_text.split()

        stop_words = {
            'и', 'в', 'на', 'с', 'по', 'для', 'о', 'об', 'от', 'к', 'у',
            'а', 'но', 'да', 'же', 'ли', 'бы', 'что', 'как', 'так', 'это',
            'очень', 'меня', 'мне', 'мой', 'моя', 'мое', 'свой', 'была', 'был', 'было'
        }

        keywords = []
        for word in words:
            cleaned_word = word.strip('.,!?;:').lower()
            if len(cleaned_word) > 4 and cleaned_word not in stop_words:
                keywords.append(cleaned_word)
                if len(keywords) >= max_words:
                    break

        return ' '.join(keywords[:max_words]) if keywords else 'описание'

    def _count_reviews_with_topic_sentiment(
            self, reviews: List[Dict], topic: str, sentiment: str
    ) -> int:
        """
        Подсчитывает количество отзывов с данной темой и тональностью

        Args:
            reviews: Список отзывов
            topic: Тема
            sentiment: Тональность

        Returns:
            Количество отзывов
        """
        count = 0
        for review in reviews:
            topic_data = review.get('topic_fragments', {}).get(topic)
            if topic_data and topic_data.get('sentiment') == sentiment:
                count += 1
        return count

