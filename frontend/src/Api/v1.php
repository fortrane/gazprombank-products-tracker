<?php

include_once __DIR__ . '/../Custom/Medoo/connect.php';
include_once __DIR__ . '/../Functions/utility.class.php';

@session_start();

$utilityClass = new UtilityClass();

$apiUrl = "BACKEND_URL";
$secretKey = "SECRET_KEY_1";

if (isset($_GET['authUser'])) {

    if (!empty($_POST['login']) && !empty($_POST['password'])) {

        $login = $utilityClass->sanitizeParam($_POST['login']);
        $password = $utilityClass->sanitizeParam($_POST['password']);

        $databaseCallback = $database->get("gb_users", ["id", "login", "role"], ["login" => $login, "password" => md5($password)]);

        if (empty($databaseCallback['id'])) {
            $utilityClass->addJavaScript('addNotification("Ошибка авторизации", "Введенные данные неверны. Повторите попытку!", "Danger")');
            exit();
        }

        $_SESSION['id'] = $databaseCallback['id'];
        $_SESSION['login'] = $login;
        $_SESSION['role'] = $databaseCallback['role'];

        exit($utilityClass->changeLocationViaHTML('0', './review'));
    }
}

if (isset($_GET['saveNewPassword'])) {

    $utilityClass->checkSessions("dashboardAccess", $database);

    $oldPassword = $utilityClass->sanitizeParam($_POST['oldPassword']);
    $newPassword = $utilityClass->sanitizeParam($_POST['newPassword']);

    $databasePassword = $database->get("gb_users", "password", ["id" => $_SESSION["id"]]);

    if ($databasePassword != md5($oldPassword)) {
        $utilityClass->addJavaScript('addNotification("Ошибка сохранения", "Старый пароль не совпадает с введенным, повторите попытку!", "Danger")');
        exit();
    }

    $databaseCallback = $database->update("gb_users", [
        "password" => md5($newPassword)
    ], ["id" => $_SESSION["id"]]);

    $response = [
        "response" => "success"
    ];

    echo json_encode($response);
}

if (isset($_GET['getProducts'])) {

    $utilityClass->checkSessions("dashboardAccess", $database);
    
    $response = $utilityClass->fetchDataFromExternalServer($apiUrl . '/products', $secretKey);
    
    echo $response;
    exit();
}

if (isset($_GET['getStatistics'])) {

    $utilityClass->checkSessions("dashboardAccess", $database);
    
    $response = $utilityClass->fetchDataFromExternalServer($apiUrl . '/statistics', $secretKey);
    
    echo $response;
    exit();
}

if (isset($_GET['getChartData'])) {

    $utilityClass->checkSessions("dashboardAccess", $database);

    $input = json_decode(file_get_contents('php://input'), true);
    
    $requestData = [
        "start" => $input['start'] ?? '',
        "end" => $input['end'] ?? '',
        "products" => $input['products'] ?? [],
        "include" => $input['include'] ?? ['positive', 'negative', 'neutral']
    ];
    
    $response = $utilityClass->sendDataToExternalServer($apiUrl . '/chart_data', $requestData, $secretKey);
    
    echo $response;
    exit();
}

if (isset($_GET['getReviews'])) {

    $utilityClass->checkSessions("dashboardAccess", $database);

    $input = json_decode(file_get_contents('php://input'), true);
    
    $requestData = [
        "limit" => $input['limit'] ?? 10,
        "index" => $input['index'] ?? 0,
        "themes" => $input['themes'] ?? [],
        "products" => $input['products'] ?? [],
        "start" => $input['start'] ?? '',
        "end" => $input['end'] ?? ''
    ];
    
    $response = $utilityClass->sendDataToExternalServer($apiUrl . '/reviews', $requestData, $secretKey);
    
    echo $response;
    exit();
}

if (isset($_GET['getParseStatus'])) {
    $utilityClass->checkSessions("dashboardAccess", $database);
    
    $response = $utilityClass->fetchDataFromExternalServer($apiUrl . '/parse_status', $secretKey);
    
    echo $response;
    exit();
}

if (isset($_GET['startCollecting'])) {
    $utilityClass->checkSessions("dashboardAccess", $database);
    
    $response = $utilityClass->sendDataToExternalServer($apiUrl . '/start_collecting', [], $secretKey);
    
    echo $response;
    exit();
}

if (isset($_GET['addSingleReview'])) {
    $utilityClass->checkSessions("dashboardAccess", $database);
    
    $input = json_decode(file_get_contents('php://input'), true);
    
    $requestData = [
        "product" => $input['product'] ?? '',
        "date" => $input['date'] ?? '',
        "text" => $input['text'] ?? ''
    ];

    $response = $utilityClass->sendDataToExternalServer($apiUrl . '/add_single_review', $requestData, $secretKey);
    
    echo $response;
    exit();
}

if (isset($_GET['bulkAddReviews'])) {
    $utilityClass->checkSessions("dashboardAccess", $database);
    
    $input = json_decode(file_get_contents('php://input'), true);
    
    $response = $utilityClass->sendDataToExternalServer($apiUrl . '/bulk_add_reviews', $input, $secretKey);
    
    echo $response;
    exit();
}

if (isset($_GET['getLastReviewId'])) {
    $utilityClass->checkSessions("dashboardAccess", $database);
    
    $response = $utilityClass->fetchDataFromExternalServer($apiUrl . '/last_review_id', $secretKey);
    
    echo $response;
    exit();
}

if (isset($_GET['getReviewsPaginated'])) {
    $utilityClass->checkSessions("dashboardAccess", $database);
    
    $input = json_decode(file_get_contents('php://input'), true);
    
    $requestData = [
        "page" => $input['page'] ?? 1,
        "products" => $input['products'] ?? [],
        "themes" => $input['themes'] ?? [],
        "start" => $input['start'] ?? '',
        "end" => $input['end'] ?? ''
    ];
    
    $response = $utilityClass->sendDataToExternalServer($apiUrl . '/reviews_paginated', $requestData, $secretKey);
    
    echo $response;
    exit();
}