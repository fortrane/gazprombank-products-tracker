<?php
$templates = new Templates();
$templates->documentHead("Reviews");
?>
<body>
    <?php 
    $templates->gazprombankHeader("Reviews"); 
?>
<main class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
    <div class="bg-white rounded-xl border border-gray-100 p-6 mb-6">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div class="flex flex-col sm:flex-row sm:items-center gap-4">
                <div class="relative">
                    <div id="status-badge" class="inline-flex items-center px-3 py-1.5 rounded-lg bg-green-50 border border-green-200">
                        <span class="relative flex h-2 w-2 mr-2">
                            <span id="status-ping" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                            <span id="status-dot" class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                        </span>
                        <span id="status-text" class="text-sm font-medium text-green-700">Загрузка...</span>
                    </div>
                </div>
                <div class="text-sm text-gray-500">
                    Последний парсинг: <span id="last-parse-date" class="font-medium text-gray-900">-</span>
                </div>
            </div>
            <div class="flex flex-wrap gap-3">
                <button id="collect-reviews-btn" class="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-500 transition-all text-sm font-medium">
                    Собрать отзывы
                </button>
                <button id="add-review-btn" class="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-500 transition-all text-sm font-medium">
                    Добавить отзыв
                </button>
                <button id="bulk-add-btn" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 transition-all text-sm font-medium">
                    Массовое добавление
                </button>
            </div>
        </div>
    </div>

    <div class="bg-white rounded-xl border border-gray-100 p-6">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4 lg:mb-0">Все отзывы</h2>
            <div class="flex flex-col sm:flex-row gap-3">
                <div class="relative">
                    <input type="text" id="reviews-daterange" class="px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent cursor-pointer bg-white" readonly placeholder="Выберите период">
                </div>
                <select id="reviews-products-filter" class="px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent" multiple>
                </select>
                <div class="relative">
                    <input type="text" id="themes-input" placeholder="Темы (Enter)" class="px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent">
                </div>
                <button id="apply-reviews-filters" class="px-6 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-500 transition-all text-sm font-medium cursor-pointer">
                    Применить
                </button>
            </div>
        </div>
        <div id="themes-tags" class="flex flex-wrap gap-2 mb-4"></div>
        
        <div id="reviews-list" class="space-y-4"></div>
        
        <div class="mt-6 flex items-center justify-between">
            <div class="text-sm text-gray-600">
                Показано <span id="showing-count">0</span> из <span id="total-count">0</span> отзывов
            </div>
            <div id="pagination" class="flex items-center space-x-2"></div>
        </div>
    </div>
</main>

<div id="collect-modal" class="fixed inset-0 bg-black/40 hidden items-center justify-center z-50">
    <div class="bg-white rounded-xl p-6 max-w-md w-full mx-4 transform transition-all scale-95 opacity-0">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Запуск сбора отзывов</h3>
        <p class="text-sm text-gray-600 mb-6">Вы уверены, что хотите запустить процесс сбора отзывов? Это может занять некоторое время.</p>
        <div class="flex space-x-3">
            <button id="confirm-collect" class="flex-1 px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-500 transition-all text-sm font-medium">
                Запустить
            </button>
            <button class="cancel-modal flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all text-sm font-medium">
                Отмена
            </button>
        </div>
    </div>
</div>

<div id="add-review-modal" class="fixed inset-0 bg-black/40 hidden items-center justify-center z-50">
    <div class="bg-white rounded-xl p-6 max-w-lg w-full mx-4 transform transition-all scale-95 opacity-0">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Добавить отзыв</h3>
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Продукт</label>
                <select id="review-product" class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500">
                </select>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Дата отзыва</label>
                <input type="text" id="review-date" class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 cursor-pointer" readonly>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Текст отзыва</label>
                <textarea id="review-text" rows="4" class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 resize-none"></textarea>
            </div>
        </div>
        <div class="flex space-x-3 mt-6">
            <button id="submit-review" class="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-500 transition-all text-sm font-medium">
                Добавить
            </button>
            <button class="cancel-modal flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all text-sm font-medium">
                Отмена
            </button>
        </div>
    </div>
</div>

<div id="bulk-add-modal" class="fixed inset-0 bg-black/40 hidden items-center justify-center z-50">
    <div class="bg-white rounded-xl p-6 max-w-2xl w-full mx-4 transform transition-all scale-95 opacity-0">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Массовое добавление отзывов</h3>
        <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">JSON данные</label>
            <textarea id="bulk-json" rows="10" class="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 font-mono text-sm" placeholder='{"data": [{"id": 1, "text": "..."}, ...]}'></textarea>
        </div>
        <div class="flex space-x-3">
            <button id="submit-bulk" class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 transition-all text-sm font-medium">
                Добавить
            </button>
            <button class="cancel-modal flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all text-sm font-medium">
                Отмена
            </button>
        </div>
    </div>
</div>
<?php
    $templates->gazprombankFooter();
    $templates->documentJavascript("Reviews");
?>
</body>
</html>