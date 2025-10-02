$(document).ready(function() {
    let reviewsChart = null;
    let currentReviewsIndex = 0;
    let selectedThemes = [];
    let chartFilters = {
        start: '',
        end: '',
        products: [],
        include: ['positive', 'negative', 'neutral']
    };
    let reviewsFilters = {
        start: '',
        end: '',
        products: [],
        themes: []
    };
    
    function initDateRangePickers() {
        const today = moment();
        const weekAgo = moment().subtract(7, 'days');
        
        $('#daterange').daterangepicker({
            startDate: weekAgo,
            endDate: today,
            locale: {
                format: 'DD.MM.YYYY',
                applyLabel: 'Применить',
                cancelLabel: 'Отмена',
                fromLabel: 'От',
                toLabel: 'До',
                customRangeLabel: 'Свой период',
                weekLabel: 'Н',
                daysOfWeek: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
                monthNames: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
                firstDay: 1
            },
            ranges: {
                'Сегодня': [moment(), moment()],
                'Вчера': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
                'Последние 7 дней': [moment().subtract(6, 'days'), moment()],
                'Последние 30 дней': [moment().subtract(29, 'days'), moment()],
                'Этот месяц': [moment().startOf('month'), moment().endOf('month')],
                'Прошлый месяц': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
            },
            alwaysShowCalendars: true,
            showDropdowns: true,
            minYear: 2020,
            maxYear: parseInt(moment().format('YYYY'), 10),
            opens: 'left'
        });
        
        $('#reviews-daterange').daterangepicker({
            autoUpdateInput: false,
            locale: {
                format: 'DD.MM.YYYY',
                applyLabel: 'Применить',
                cancelLabel: 'Очистить',
                fromLabel: 'От',
                toLabel: 'До',
                customRangeLabel: 'Свой период',
                weekLabel: 'Н',
                daysOfWeek: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
                monthNames: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
                firstDay: 1
            },
            ranges: {
                'Сегодня': [moment(), moment()],
                'Вчера': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
                'Последние 7 дней': [moment().subtract(6, 'days'), moment()],
                'Последние 30 дней': [moment().subtract(29, 'days'), moment()],
                'Этот месяц': [moment().startOf('month'), moment().endOf('month')],
                'Прошлый месяц': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
            },
            alwaysShowCalendars: true,
            showDropdowns: true,
            minYear: 2020,
            maxYear: parseInt(moment().format('YYYY'), 10),
            opens: 'left'
        });
        
        $('#reviews-daterange').on('apply.daterangepicker', function(ev, picker) {
            $(this).val(picker.startDate.format('DD.MM.YYYY') + ' - ' + picker.endDate.format('DD.MM.YYYY'));
        });
        
        $('#reviews-daterange').on('cancel.daterangepicker', function(ev, picker) {
            $(this).val('');
        });
        
        chartFilters.start = weekAgo.format('YYYY-MM-DD');
        chartFilters.end = today.format('YYYY-MM-DD');
    }
    
    function loadProducts() {
        $.ajax({
            url: './src/Api/v1.php?getProducts=true',
            method: 'GET',
            success: function(response) {
                const data = JSON.parse(response);
                $('#products-filter, #reviews-products-filter').empty();
                
                Object.entries(data).forEach(([key, value]) => {
                    $('#products-filter, #reviews-products-filter').append(
                        `<option value="${key}">${value}</option>`
                    );
                });
                
                $('#products-filter').select2({
                    placeholder: 'Все продукты',
                    allowClear: true,
                    width: '200px'
                });
                
                $('#reviews-products-filter').select2({
                    placeholder: 'Все продукты',
                    allowClear: true,
                    width: '200px'
                });
            }
        });
    }
    
    function loadStatistics() {
        $.ajax({
            url: './src/Api/v1.php?getStatistics=true',
            method: 'GET',
            success: function(response) {
                const data = JSON.parse(response);
                
                $('#total-reviews').text(data.total_reviews);
                $('#positive-count').text(data.positive_count);
                $('#positive-percent').text(`${Math.round(data.positive * 100)}%`);
                $('#negative-count').text(data.negative_count);
                $('#negative-percent').text(`${Math.round(data.negative * 100)}%`);
                $('#neutral-count').text(data.neutral_count);
                $('#neutral-percent').text(`${Math.round(data.neutral * 100)}%`);
            }
        });
    }
    
    function loadChartData() {
        $.ajax({
            url: './src/Api/v1.php?getChartData=true',
            method: 'POST',
            data: JSON.stringify(chartFilters),
            contentType: 'application/json',
            success: function(response) {
                const data = JSON.parse(response);
                renderChart(data);
                renderSummary(data.summary);
            }
        });
    }
    
    function renderChart(data) {
        const ctx = document.getElementById('reviewsChart').getContext('2d');
        
        if (reviewsChart) {
            reviewsChart.destroy();
        }
        
        const labels = data.candles.map(c => {
            const date = new Date(c.date);
            return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
        });
        
        const datasets = [];
        
        if (chartFilters.include.includes('positive')) {
            datasets.push({
                label: 'Позитивные',
                data: data.candles.map(c => parseInt(c.positive_count)),
                backgroundColor: 'rgba(16, 185, 129, 0.7)',
                borderColor: 'rgba(16, 185, 129, 1)',
                borderWidth: 0,
                borderRadius: 4
            });
        }
        
        if (chartFilters.include.includes('neutral')) {
            datasets.push({
                label: 'Нейтральные',
                data: data.candles.map(c => parseInt(c.neutral_count)),
                backgroundColor: 'rgba(156, 163, 175, 0.5)',
                borderColor: 'rgba(156, 163, 175, 1)',
                borderWidth: 0,
                borderRadius: 4
            });
        }
        
        if (chartFilters.include.includes('negative')) {
            datasets.push({
                label: 'Негативные',
                data: data.candles.map(c => parseInt(c.negative_count)),
                backgroundColor: 'rgba(244, 63, 94, 0.7)',
                borderColor: 'rgba(244, 63, 94, 1)',
                borderWidth: 0,
                borderRadius: 4
            });
        }
        
        reviewsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true,
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 11
                            }
                        }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        grid: {
                            display: false
                        },
                        ticks: {
                            stepSize: 10,
                            font: {
                                size: 11
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            afterTitle: function(context) {
                                const dataIndex = context[0].dataIndex;
                                const candle = data.candles[dataIndex];
                                return `Всего отзывов: ${candle.total_reviews}`;
                            },
                            label: function(context) {
                                const dataIndex = context.dataIndex;
                                const candle = data.candles[dataIndex];
                                let percentage = 0;
                                
                                if (context.dataset.label === 'Позитивные') {
                                    percentage = Math.round(candle.positive * 100);
                                } else if (context.dataset.label === 'Нейтральные') {
                                    percentage = Math.round(candle.neutral * 100);
                                } else if (context.dataset.label === 'Негативные') {
                                    percentage = Math.round(candle.negative * 100);
                                }
                                
                                return `${context.dataset.label}: ${context.parsed.y} (${percentage}%)`;
                            }
                        },
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        titleColor: '#1f2937',
                        bodyColor: '#4b5563',
                        borderColor: '#e5e7eb',
                        borderWidth: 1,
                        titleFont: {
                            size: 13,
                            weight: 600
                        },
                        bodyFont: {
                            size: 12
                        },
                        padding: 12,
                        displayColors: true,
                        boxWidth: 12,
                        boxHeight: 12,
                        cornerRadius: 8
                    }
                },
                interaction: {
                    mode: 'index',
                    intersect: false
                }
            }
        });
    }
    
    function renderSummary(summary) {
        if (!summary) return;
        
        $('#chart-summary').removeClass('hidden');
        $('#summary-period').text(summary.period);
        
        let filteredTotal = 0;
        let filteredPositive = 0;
        let filteredNeutral = 0;
        let filteredNegative = 0;
        
        if (chartFilters.include.includes('positive')) {
            filteredPositive = summary.positive;
            filteredTotal += summary.positive * summary.total_reviews;
        }
        if (chartFilters.include.includes('neutral')) {
            filteredNeutral = summary.neutral;
            filteredTotal += summary.neutral * summary.total_reviews;
        }
        if (chartFilters.include.includes('negative')) {
            filteredNegative = summary.negative;
            filteredTotal += summary.negative * summary.total_reviews;
        }
        
        filteredTotal = Math.round(filteredTotal);
        
        const total = filteredPositive + filteredNeutral + filteredNegative;
        if (total > 0) {
            filteredPositive = Math.round((filteredPositive / total) * 100);
            filteredNeutral = Math.round((filteredNeutral / total) * 100);
            filteredNegative = Math.round((filteredNegative / total) * 100);
        }
        
        $('#summary-total').text(filteredTotal);
        $('#summary-positive').text(chartFilters.include.includes('positive') ? `${filteredPositive}%` : '—');
        $('#summary-neutral').text(chartFilters.include.includes('neutral') ? `${filteredNeutral}%` : '—');
        $('#summary-negative').text(chartFilters.include.includes('negative') ? `${filteredNegative}%` : '—');
        
        if (summary.positive_aspects && summary.positive_aspects.length > 0 && chartFilters.include.includes('positive')) {
            $('#positive-aspects-block').removeClass('hidden');
            $('#positive-aspects').empty();
            summary.positive_aspects.forEach(aspect => {
                $('#positive-aspects').append(
                    `<span class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">${aspect}</span>`
                );
            });
        } else {
            $('#positive-aspects-block').addClass('hidden');
        }
        
        if (summary.negative_aspects && summary.negative_aspects.length > 0 && chartFilters.include.includes('negative')) {
            $('#negative-aspects-block').removeClass('hidden');
            $('#negative-aspects').empty();
            summary.negative_aspects.forEach(aspect => {
                $('#negative-aspects').append(
                    `<span class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200">${aspect}</span>`
                );
            });
        } else {
            $('#negative-aspects-block').addClass('hidden');
        }
    }
    
    function loadReviews(reset = false) {
        if (reset) {
            currentReviewsIndex = 0;
            $('#reviews-list').empty();
        }
        
        const filters = {
            limit: 10,
            index: currentReviewsIndex,
            themes: reviewsFilters.themes,
            products: reviewsFilters.products,
            start: reviewsFilters.start,
            end: reviewsFilters.end
        };
        
        $.ajax({
            url: './src/Api/v1.php?getReviews=true',
            method: 'POST',
            data: JSON.stringify(filters),
            contentType: 'application/json',
            success: function(response) {
                const data = JSON.parse(response);
                renderReviews(data.reviews);
                
                if (data.reviews.length < 10) {
                    $('#load-more-reviews').hide();
                } else {
                    $('#load-more-reviews').show();
                    currentReviewsIndex += 10;
                }
            }
        });
    }
    
    function renderReviews(reviews) {
        reviews.forEach(review => {
            let polarityColor = 'gray';
            let polarityBg = 'gray';
            let polarityText = 'Нейтральный';
            let polarityIcon = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>`;
            
            if (review.polarity === 'positive') {
                polarityColor = 'green';
                polarityBg = 'green';
                polarityText = 'Позитивный';
                polarityIcon = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                </svg>`;
            } else if (review.polarity === 'negative') {
                polarityColor = 'rose';
                polarityBg = 'rose';
                polarityText = 'Негативный';
                polarityIcon = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14H5.764a2 2 0 01-1.789-2.894l3.5-7A2 2 0 019.265 3h4.017c.163 0 .326.02.485.06L17 4m-7 10v5a2 2 0 002 2h.095c.5 0 .905-.405.905-.905 0-.714.211-1.412.608-2.006L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
                </svg>`;
            }
            
            const reviewHtml = `
                <div class="border-l-4 border-${polarityColor}-400 bg-white p-5 rounded-lg border border-gray-100 hover:border-gray-200 transition-all">
                    <div class="flex items-start justify-between mb-3">
                        <div class="flex items-center space-x-3">
                            <div class="text-${polarityColor}-600">
                                ${polarityIcon}
                            </div>
                            <div>
                                <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-${polarityBg}-50 text-${polarityBg}-700">
                                    ${polarityText}
                                </span>
                            </div>
                        </div>
                        <span class="text-xs text-gray-500">${new Date(review.date).toLocaleDateString('ru-RU')}</span>
                    </div>
                    ${review.products && review.products.length > 0 ? `
                        <div class="mb-3">
                            <div class="flex flex-wrap items-center gap-2">
                                ${review.products.map((product, index) => `
                                    <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
                                        ${product}
                                    </span>
                                    ${index < review.products.length - 1 ? `
                                        <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                                    ` : ''}
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    <p class="text-gray-700 text-sm leading-relaxed mb-3">${review.review_text}</p>
                    
                    ${review.themes && review.themes.length > 0 ? `
                        <div class="mb-3">
                            <div class="flex flex-wrap gap-2">
                                ${review.themes.map(theme => `
                                    <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-sky-50 text-sky-700 border border-sky-200">
                                        ${theme}
                                    </span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                        ${review.positive_aspects && review.positive_aspects.length > 0 ? `
                            <div>
                                <div class="text-xs font-semibold text-emerald-700 mb-2">Положительные аспекты:</div>
                                <div class="flex flex-wrap gap-1.5">
                                    ${review.positive_aspects.map(aspect => `
                                        <span class="inline-flex items-center px-2 py-1 rounded-md text-xs bg-emerald-50 text-emerald-700">
                                            ${aspect}
                                        </span>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                        
                        ${review.negative_aspects && review.negative_aspects.length > 0 ? `
                            <div>
                                <div class="text-xs font-semibold text-rose-700 mb-2">Отрицательные аспекты:</div>
                                <div class="flex flex-wrap gap-1.5">
                                    ${review.negative_aspects.map(aspect => `
                                        <span class="inline-flex items-center px-2 py-1 rounded-md text-xs bg-rose-50 text-rose-700">
                                            ${aspect}
                                        </span>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
            
            $('#reviews-list').append(reviewHtml);
        });
    }
    
    function setupThemesInput() {
        $('#themes-input').on('keypress', function(e) {
            if (e.which === 13) {
                e.preventDefault();
                const theme = $(this).val().trim();
                if (theme && !selectedThemes.includes(theme)) {
                    selectedThemes.push(theme);
                    renderThemeTags();
                    $(this).val('');
                }
            }
        });
    }
    
    function renderThemeTags() {
        $('#themes-tags').empty();
        selectedThemes.forEach((theme, index) => {
            $('#themes-tags').append(`
                <span class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-sky-50 text-sky-700 border border-sky-200">
                    ${theme}
                    <button class="ml-2 text-sky-600 hover:text-sky-800" onclick="removeTheme(${index})">
                        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                    </button>
                </span>
            `);
        });
    }
    
    window.removeTheme = function(index) {
        selectedThemes.splice(index, 1);
        renderThemeTags();
    };
    
    $('.polarity-checkbox').on('change', function() {
        const include = [];
        $('.polarity-checkbox:checked').each(function() {
            include.push($(this).val());
        });
        chartFilters.include = include;
    });
    
    $('#apply-chart-filters').on('click', function() {
        const dateRange = $('#daterange').data('daterangepicker');
        chartFilters.start = dateRange.startDate.format('YYYY-MM-DD');
        chartFilters.end = dateRange.endDate.format('YYYY-MM-DD');
        chartFilters.products = $('#products-filter').val() || [];
        loadChartData();
    });
    
    $('#apply-reviews-filters').on('click', function() {
        const dateRangeValue = $('#reviews-daterange').val();
        if (dateRangeValue) {
            const dates = dateRangeValue.split(' - ');
            reviewsFilters.start = moment(dates[0], 'DD.MM.YYYY').format('YYYY-MM-DD');
            reviewsFilters.end = moment(dates[1], 'DD.MM.YYYY').format('YYYY-MM-DD');
        } else {
            reviewsFilters.start = '';
            reviewsFilters.end = '';
        }
        reviewsFilters.products = $('#reviews-products-filter').val() || [];
        reviewsFilters.themes = selectedThemes;
        loadReviews(true);
    });
    
    $('#load-more-reviews').on('click', function() {
        loadReviews(false);
    });
    
    initDateRangePickers();
    loadProducts();
    loadStatistics();
    loadChartData();
    loadReviews(true);
    setupThemesInput();
});