<?php
$templates = new Templates();

$templates->documentHead("Review");
?>
<body>
    <?php 
    $templates->gazprombankHeader("Review"); 
?>
<main class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div class="bg-white rounded-xl p-6 border border-gray-100">
                <div class="flex items-start space-x-4">
                    <div class="flex-shrink-0 mt-1">
                        <div class="w-10 h-10 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl flex items-center justify-center">
                            <svg class="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                        </div>
                    </div>
                    <div class="flex-1">
                        <div class="text-2xl font-bold text-gray-900" id="total-reviews">-</div>
                        <p class="text-sm text-gray-500 mt-1">Всего отзывов</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl p-6 border border-gray-100">
                <div class="flex items-start space-x-4">
                    <div class="flex-shrink-0 mt-1">
                        <div class="w-10 h-10 bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl flex items-center justify-center">
                            <svg class="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                            </svg>
                        </div>
                    </div>
                    <div class="flex-1">
                        <div class="flex items-baseline space-x-2">
                            <div class="text-2xl font-bold text-gray-900" id="positive-count">-</div>
                            <div class="text-sm font-medium text-emerald-600" id="positive-percent">--%</div>
                        </div>
                        <p class="text-sm text-gray-500 mt-1">Позитивные</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl p-6 border border-gray-100">
                <div class="flex items-start space-x-4">
                    <div class="flex-shrink-0 mt-1">
                        <div class="w-10 h-10 bg-gradient-to-br from-rose-50 to-rose-100 rounded-xl flex items-center justify-center">
                            <svg class="w-5 h-5 text-rose-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14H5.764a2 2 0 01-1.789-2.894l3.5-7A2 2 0 019.265 3h4.017c.163 0 .326.02.485.06L17 4m-7 10v5a2 2 0 002 2h.095c.5 0 .905-.405.905-.905 0-.714.211-1.412.608-2.006L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
                            </svg>
                        </div>
                    </div>
                    <div class="flex-1">
                        <div class="flex items-baseline space-x-2">
                            <div class="text-2xl font-bold text-gray-900" id="negative-count">-</div>
                            <div class="text-sm font-medium text-rose-600" id="negative-percent">--%</div>
                        </div>
                        <p class="text-sm text-gray-500 mt-1">Негативные</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl p-6 border border-gray-100">
                <div class="flex items-start space-x-4">
                    <div class="flex-shrink-0 mt-1">
                        <div class="w-10 h-10 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl flex items-center justify-center">
                            <svg class="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                    </div>
                    <div class="flex-1">
                        <div class="flex items-baseline space-x-2">
                            <div class="text-2xl font-bold text-gray-900" id="neutral-count">-</div>
                            <div class="text-sm font-medium text-gray-600" id="neutral-percent">--%</div>
                        </div>
                        <p class="text-sm text-gray-500 mt-1">Нейтральные</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-xl border border-gray-100 p-6 mb-8">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
                <h2 class="text-lg font-semibold text-gray-900 mb-4 lg:mb-0">Динамика отзывов</h2>
                <div class="flex flex-col sm:flex-row gap-3">
                    <div class="relative">
                        <input type="text" id="daterange" class="px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent cursor-pointer bg-white" readonly placeholder="Выберите период">
                    </div>
                    <select id="products-filter" class="px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent" multiple>
                        <option value="">Все продукты</option>
                    </select>
                    <button id="apply-chart-filters" class="px-6 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-500 transition-all text-sm font-medium cursor-pointer">
                        Применить
                    </button>
                </div>
            </div>
            
            <div class="mb-4">
                <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                    <span class="text-sm font-medium text-gray-700">Включить в статистику:</span>
                    <div class="flex flex-wrap gap-4">
                        <label class="flex items-center cursor-pointer">
                            <input type="checkbox" class="polarity-checkbox mr-2 w-4 h-4 text-emerald-600 bg-gray-100 border-gray-300 rounded focus:ring-emerald-500 focus:ring-2" value="positive" checked>
                            <span class="text-sm text-gray-700">Положительные</span>
                        </label>
                        <label class="flex items-center cursor-pointer">
                            <input type="checkbox" class="polarity-checkbox mr-2 w-4 h-4 text-rose-600 bg-gray-100 border-gray-300 rounded focus:ring-rose-500 focus:ring-2" value="negative" checked>
                            <span class="text-sm text-gray-700">Негативные</span>
                        </label>
                        <label class="flex items-center cursor-pointer">
                            <input type="checkbox" class="polarity-checkbox mr-2 w-4 h-4 text-gray-600 bg-gray-100 border-gray-300 rounded focus:ring-gray-500 focus:ring-2" value="neutral" checked>
                            <span class="text-sm text-gray-700">Нейтральные</span>
                        </label>
                    </div>
                </div>
            </div>
            
            <div class="relative h-96">
                <canvas id="reviewsChart"></canvas>
            </div>
            <div id="chart-summary" class="mt-8 hidden">
                <div>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                        <div class="text-center bg-gradient-to-r from-gray-50 to-white rounded-xl p-6 border border-gray-100">
                            <p class="text-sm text-gray-500 mb-1">Период анализа</p>
                            <p class="text-base font-semibold text-gray-900" id="summary-period">-</p>
                        </div>
                        <div class="text-center bg-gradient-to-r from-gray-50 to-white rounded-xl p-6 border border-gray-100">
                            <p class="text-sm text-gray-500 mb-1">Всего аспектов</p>
                            <p class="text-2xl font-bold text-gray-900" id="summary-total">-</p>
                        </div>
                        <div class="text-center bg-gradient-to-r from-gray-50 to-white rounded-xl p-6 border border-gray-100">
                            <p class="text-sm text-gray-500 mb-2">Распределение</p>
                            <div class="flex justify-center space-x-6">
                                <div>
                                    <div class="flex items-center space-x-2">
                                        <div class="w-3 h-3 bg-emerald-400 rounded-full"></div>
                                        <span class="text-sm font-medium text-gray-700" id="summary-positive">-</span>
                                    </div>
                                </div>
                                <div>
                                    <div class="flex items-center space-x-2">
                                        <div class="w-3 h-3 bg-gray-400 rounded-full"></div>
                                        <span class="text-sm font-medium text-gray-700" id="summary-neutral">-</span>
                                    </div>
                                </div>
                                <div>
                                    <div class="flex items-center space-x-2">
                                        <div class="w-3 h-3 bg-rose-400 rounded-full"></div>
                                        <span class="text-sm font-medium text-gray-700" id="summary-negative">-</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="bg-gradient-to-r from-gray-50 to-white rounded-xl p-6 border border-gray-100">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div id="positive-aspects-block" class="hidden">
                            <h3 class="text-sm font-semibold text-emerald-700 mb-3 flex items-center">
                                <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                                </svg>
                                Положительные аспекты
                            </h3>
                            <div id="positive-aspects" class="flex flex-wrap gap-2"></div>
                        </div>
                        <div id="negative-aspects-block" class="hidden">
                            <h3 class="text-sm font-semibold text-rose-700 mb-3 flex items-center">
                                <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                                </svg>
                                Отрицательные аспекты
                            </h3>
                            <div id="negative-aspects" class="flex flex-wrap gap-2"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-xl border border-gray-100 p-6">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
                <h2 class="text-lg font-semibold text-gray-900 mb-4 lg:mb-0">Последние отзывы</h2>
                <div class="flex flex-col sm:flex-row gap-3">
                    <div class="relative">
                        <input type="text" id="reviews-daterange" class="px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent cursor-pointer bg-white" readonly placeholder="Выберите период">
                    </div>
                    <select id="reviews-products-filter" class="px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent" multiple>
                        <option value="">Все продукты</option>
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
            
            <div id="reviews-list" class="space-y-4">
            </div>
            
            <div class="mt-8 flex justify-center">
                <button id="load-more-reviews" class="px-8 py-3 bg-gradient-to-r from-gray-50 to-gray-100 text-gray-700 rounded-lg hover:from-gray-100 hover:to-gray-200 transition-all text-sm font-medium border border-gray-200">
                    Загрузить больше
                </button>
            </div>
        </div>
    </main>
<?
    $templates->gazprombankFooter();
    $templates->documentJavascript("Review");
    ?>
</body>
</html>