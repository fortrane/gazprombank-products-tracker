<?php
$templates = new Templates();

$templates->documentHead("Settings");
?>
<body>
    <?php $templates->gazprombankHeader("Settings"); ?>
    <main>
        <div class="relative isolate overflow-hidden bg-white">
            
            <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 sm:py-12 lg:py-16">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
                    <div class="w-full">
                        <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-gray-900">
                            Настройки
                        </h1>
                        <p class="mt-4 sm:mt-6 text-base sm:text-lg text-gray-600">
                            Измените свой пароль для обеспечения безопасности аккаунта
                        </p>
                        
                        <div class="mt-8 bg-white p-4 sm:p-6 rounded-lg shadow-sm ring-1 ring-gray-900/5">
                            <form class="space-y-6">
                                <div>
                                    <label for="old-password" class="block text-sm font-medium leading-6 text-gray-900">
                                        Текущий пароль
                                    </label>
                                    <div class="mt-2">
                                        <input type="password" 
                                            class="old-password block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-sky-600 sm:text-sm sm:leading-6 old-password" 
                                            placeholder="Введите текущий пароль">
                                    </div>
                                </div>

                                <div>
                                    <label for="new-password" class="block text-sm font-medium leading-6 text-gray-900">
                                        Новый пароль
                                    </label>
                                    <div class="mt-2">
                                        <input type="password" 
                                            class="new-password block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-sky-600 sm:text-sm sm:leading-6 new-password" 
                                            placeholder="Введите новый пароль">
                                    </div>
                                </div>

                                <div class="flex items-center justify-end pt-4">
                                    <button type="button" 
                                            class="save-button w-full sm:w-auto rounded-md bg-sky-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-sky-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-600 save-button">
                                        Сохранить изменения
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>

                    <div class="w-full">
                        <div class="h-auto bg-gray-50 rounded-lg p-4 sm:p-6 lg:p-8 ring-1 ring-gray-900/5">
                            <div class="max-w-full">
                                <div class="flex flex-col gap-4 rounded-xl">
                                    <h3 class="font-semibold text-xl text-gray-900">Рекомендации по безопасности</h3>
                                    <ul class="text-gray-600 list-disc space-y-3 pl-5">
                                        <li>Используйте минимум 8 символов</li>
                                        <li>Комбинируйте буквы, цифры и специальные символы</li>
                                        <li>Не используйте личную информацию</li>
                                        <li>Регулярно меняйте пароль</li>
                                        <li>Не используйте один и тот же пароль для разных сервисов</li>
                                        <li>Избегайте очевидных комбинаций (123456, qwerty)</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>
    <?php
    $templates->gazprombankFooter();
    $templates->documentJavascript("Settings");
    ?>
</body>
</html>