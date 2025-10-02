<?

    global $database;

    require __DIR__ . '/vendor/autoload.php';
 
    use Medoo\Medoo;

    try {
        $pdo = new PDO('mysql:dbname=db_test;host=localhost', 'db_usr', 'db_pwd');
    } catch (PDOException $e) {
        die('Database Connection failed');
    }
    $database = new Medoo([
        'pdo' => $pdo,
        'database_type' => 'mysql'
    ]);

?>