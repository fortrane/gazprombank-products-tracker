$(document).ready(function() {
    let currentPage = 1;
    let lastReviewId = null;
    let statusCheckInterval;
    let reviewCheckInterval;
    let selectedThemes = [];
    let reviewsFilters = {
        start: '',
        end: '',
        products: [],
        themes: []
    };
    
    function initDateRangePickers() {
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
        
        $('#review-date').daterangepicker({
            singleDatePicker: true,
            locale: {
                format: 'YYYY-MM-DD',
                applyLabel: 'Выбрать',
                cancelLabel: 'Отмена',
                daysOfWeek: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
                monthNames: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
                firstDay: 1
            },
            startDate: moment(),
            maxDate: moment()
        });
    }
    
    function loadProducts() {
        $.ajax({
            url: './src/Api/v1.php?getProducts',
            method: 'GET',
            success: function(response) {
                const data = typeof response === 'string' ? JSON.parse(response) : response;
                
                Object.entries(data).forEach(([key, value]) => {
                    $('#reviews-products-filter').append(`<option value="${key}">${value}</option>`);
                    $('#review-product').append(`<option value="${key}">${value}</option>`);
                });
                
                $('#reviews-products-filter').select2({
                    placeholder: 'Все продукты',
                    allowClear: true,
                    width: '200px'
                });
                
                $('#review-product').select2({
                    placeholder: 'Выберите продукт',
                    width: '100%'
                });
            }
        });
    }
    
    function checkParseStatus() {
        $.ajax({
            url: './src/Api/v1.php?getParseStatus',
            method: 'GET',
            success: function(response) {
                const data = typeof response === 'string' ? JSON.parse(response) : response;
                updateStatusBadge(data.is_task);
                updateLastParseDate(data.last_parse_date);
                
                const $collectBtn = $('#collect-reviews-btn');
                if (data.is_task) {
                    $collectBtn.prop('disabled', true).addClass('opacity-50 cursor-not-allowed');
                } else {
                    $collectBtn.prop('disabled', false).removeClass('opacity-50 cursor-not-allowed');
                }
            }
        });
    }
    
    function updateStatusBadge(isTask) {
        const $badge = $('#status-badge');
        const $text = $('#status-text');
        const $ping = $('#status-ping');
        const $dot = $('#status-dot');
        
        if (isTask) {
            $badge.removeClass('bg-green-50 border-green-200').addClass('bg-yellow-50 border-yellow-200');
            $text.removeClass('text-green-700').addClass('text-yellow-700').text('Идет сбор');
            $ping.removeClass('bg-green-400').addClass('bg-yellow-400');
            $dot.removeClass('bg-green-500').addClass('bg-yellow-500');
        } else {
            $badge.removeClass('bg-yellow-50 border-yellow-200').addClass('bg-green-50 border-green-200');
            $text.removeClass('text-yellow-700').addClass('text-green-700').text('Готов');
            $ping.removeClass('bg-yellow-400').addClass('bg-green-400');
            $dot.removeClass('bg-yellow-500').addClass('bg-green-500');
        }
    }
    
    function updateLastParseDate(date) {
        if (date) {
            const parsedDate = moment(date);
            $('#last-parse-date').text(parsedDate.format('DD.MM.YYYY, HH:mm'));
        }
    }
    
    function checkLastReview() {
        $.ajax({
            url: './src/Api/v1.php?getLastReviewId',
            method: 'GET',
            success: function(response) {
                const data = typeof response === 'string' ? JSON.parse(response) : response;
                if (data.last_id && lastReviewId && data.last_id !== lastReviewId) {
                    addNotification("Добавлены новые отзывы!", "Обновите страницу, добавлены новые отзывы", "Information");
                }
                if (data.last_id) {
                    lastReviewId = data.last_id;
                }
            }
        });
    }
    
    function loadReviews() {
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
        
        const requestData = {
            page: currentPage,
            products: reviewsFilters.products,
            themes: reviewsFilters.themes,
            start: reviewsFilters.start,
            end: reviewsFilters.end
        };
        
        $.ajax({
            url: './src/Api/v1.php?getReviewsPaginated',
            method: 'POST',
            data: JSON.stringify(requestData),
            contentType: 'application/json',
            success: function(response) {
                const data = typeof response === 'string' ? JSON.parse(response) : response;
                renderReviews(data.reviews);
                renderPagination(data.pagination);
                updateCounters(data.pagination);
            }
        });
    }
    
    function renderReviews(reviews) {
        $('#reviews-list').empty();
        
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
                        <span class="text-xs text-gray-500">${moment(review.date).format('DD.MM.YYYY')}</span>
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
                                <div class="text-xs font-semibold text-green-700 mb-2">Положительные аспекты:</div>
                                <div class="flex flex-wrap gap-1.5">
                                    ${review.positive_aspects.map(aspect => `
                                        <span class="inline-flex items-center px-2 py-1 rounded-md text-xs bg-green-50 text-green-700">
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
    
    function renderPagination(pagination) {
        const $container = $('#pagination');
        $container.empty();
        
        const maxVisible = 5;
        let startPage = Math.max(1, pagination.current_page - Math.floor(maxVisible / 2));
        let endPage = Math.min(pagination.total_pages, startPage + maxVisible - 1);
        
        if (endPage - startPage < maxVisible - 1) {
            startPage = Math.max(1, endPage - maxVisible + 1);
        }
        
        if (pagination.current_page > 1) {
            $container.append(`<button class="page-btn px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50" data-page="${pagination.current_page - 1}">←</button>`);
        }
        
        if (startPage > 1) {
            $container.append(`<button class="page-btn px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50" data-page="1">1</button>`);
            if (startPage > 2) {
                $container.append(`<span class="px-2 text-gray-400">...</span>`);
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const isActive = i === pagination.current_page;
            $container.append(`<button class="page-btn px-3 py-1 text-sm border ${isActive ? 'bg-sky-600 text-white border-sky-600' : 'border-gray-300 hover:bg-gray-50'} rounded-md" data-page="${i}">${i}</button>`);
        }
        
        if (endPage < pagination.total_pages) {
            if (endPage < pagination.total_pages - 1) {
                $container.append(`<span class="px-2 text-gray-400">...</span>`);
            }
            $container.append(`<button class="page-btn px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50" data-page="${pagination.total_pages}">${pagination.total_pages}</button>`);
        }
        
        if (pagination.current_page < pagination.total_pages) {
            $container.append(`<button class="page-btn px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50" data-page="${pagination.current_page + 1}">→</button>`);
        }
    }
    
    function updateCounters(pagination) {
        const showingStart = Math.min((pagination.current_page - 1) * pagination.per_page + 1, pagination.total_count);
        const showingEnd = Math.min(pagination.current_page * pagination.per_page, pagination.total_count);
        
        $('#showing-count').text(`${showingStart}-${showingEnd}`);
        $('#total-count').text(pagination.total_count);
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
                    <button class="remove-theme ml-2 text-sky-600 hover:text-sky-800" data-index="${index}">
                        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                        </svg>
                    </button>
                </span>
            `);
        });
    }
    
    function showModal($modal) {
        $modal.removeClass('hidden').addClass('flex');
        setTimeout(() => {
            $modal.find('.transform').removeClass('scale-95 opacity-0').addClass('scale-100 opacity-100');
        }, 10);
    }
    
    function hideModal($modal) {
        $modal.find('.transform').removeClass('scale-100 opacity-100').addClass('scale-95 opacity-0');
        setTimeout(() => {
            $modal.addClass('hidden').removeClass('flex');
        }, 300);
    }
    
    function startCollecting() {
        $.ajax({
            url: './src/Api/v1.php?startCollecting',
            method: 'POST',
            contentType: 'application/json',
            success: function(response) {
                const data = typeof response === 'string' ? JSON.parse(response) : response;
                addNotification("Процесс запущен", data.message, "Success");
                hideModal($('#collect-modal'));
                checkParseStatus();
            },
            error: function() {
                addNotification("Ошибка", "Не удалось запустить процесс", "Danger");
            }
        });
    }
    
    function submitReview() {
        const product = $('#review-product').val();
        const date = $('#review-date').val();
        const text = $('#review-text').val();
        
        if (!product || !date || !text) {
            addNotification("Ошибка", "Заполните все поля", "Warning");
            return;
        }
        
        $.ajax({
            url: './src/Api/v1.php?addSingleReview',
            method: 'POST',
            data: JSON.stringify({product, date, text}),
            contentType: 'application/json',
            success: function(response) {
                const data = typeof response === 'string' ? JSON.parse(response) : response;
                addNotification("Успешно", data.message, "Success");
                hideModal($('#add-review-modal'));
                $('#review-product').val('').trigger('change');
                $('#review-text').val('');
                loadReviews();
            },
            error: function() {
                addNotification("Ошибка", "Не удалось добавить отзыв", "Danger");
            }
        });
    }
    
    function submitBulk() {
        const jsonText = $('#bulk-json').val();
        
        if (!jsonText) {
            addNotification("Ошибка", "Введите JSON данные", "Warning");
            return;
        }
        
        try {
            $.ajax({
                url: './src/Api/v1.php?bulkAddReviews',
                method: 'POST',
                data: JSON.stringify(jsonText),
                contentType: 'application/json',
                success: function(response) {
                    const data = typeof response === 'string' ? JSON.parse(response) : response;
                    addNotification("Успешно", `${data.message}. Добавлено: ${data.count}`, "Success");
                    hideModal($('#bulk-add-modal'));
                    $('#bulk-json').val('');
                    loadReviews();
                },
                error: function() {
                    addNotification("Ошибка", "Не удалось добавить отзывы", "Danger");
                }
            });
        } catch (e) {
            addNotification("Ошибка", "Неверный формат JSON", "Danger");
        }
    }
    
    $(document).on('click', '.page-btn', function() {
        currentPage = $(this).data('page');
        loadReviews();
        $('html, body').animate({scrollTop: 0}, 'smooth');
    });
    
    $(document).on('click', '.remove-theme', function() {
        const index = $(this).data('index');
        selectedThemes.splice(index, 1);
        renderThemeTags();
    });
    
    $('#apply-reviews-filters').on('click', function() {
        currentPage = 1;
        loadReviews();
    });
    
    $('#collect-reviews-btn').on('click', function() {
        showModal($('#collect-modal'));
    });
    
    $('#add-review-btn').on('click', function() {
        showModal($('#add-review-modal'));
    });
    
    $('#bulk-add-btn').on('click', function() {
        showModal($('#bulk-add-modal'));
    });
    
    $('.cancel-modal').on('click', function() {
        hideModal($(this).closest('.fixed'));
    });
    
    $('#confirm-collect').on('click', startCollecting);
    $('#submit-review').on('click', submitReview);
    $('#submit-bulk').on('click', submitBulk);
    
    initDateRangePickers();
    loadProducts();
    loadReviews();
    checkParseStatus();
    setupThemesInput();
    
    statusCheckInterval = setInterval(checkParseStatus, 5000);
    reviewCheckInterval = setInterval(checkLastReview, 15000);
});