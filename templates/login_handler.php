<?php
// Start the session
session_start();

// Include the database connection file
include_once 'config.php';

// Check if the form is submitted
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Get form data
    $email = $_POST['email'];
    $password = $_POST['password']; // Note: You should hash the password before storing it in the database
    
    // Prepare and execute the SQL query
    $stmt = $conn->prepare("SELECT * FROM users WHERE email = ? AND password = ?");
    $stmt->bind_param("ss", $email, $password);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        // Authentication successful
        // Start a new session and store user data
        $user = $result->fetch_assoc();
        $_SESSION['user_id'] = $user['id']; // Assuming 'id' is the primary key column in your 'users' table
        $_SESSION['username'] = $user['username']; // Assuming 'username' is a column in your 'users' table
        // Redirect to the home page or any other authenticated page
        header("Location: home.html");
        exit();
    } else {
        // Authentication failed
        echo "Invalid email or password. Please try again.";
    }
}

// Close the database connection
$conn->close();
?>
