<?php
// Start the session
session_start();

// Include the database connection file
include_once 'config.php';

// Check if the form is submitted
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Get form data
    $fullname = $_POST['fullname'];
    $email = $_POST['email'];
    $password = $_POST['password']; // Note: You should hash the password before storing it in the database
    
    // Check if the email is already registered
    $sql = "SELECT * FROM users WHERE email='$email'";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        // Email already exists
        echo "Email already exists. Please try with a different email.";
    } else {
        // Insert new user data into the database
        $sql = "INSERT INTO users (fullname, email, password) VALUES ('$fullname', '$email', '$password')";
        
        if ($conn->query($sql) === TRUE) {
            // Registration successful
            $_SESSION['message'] = "Registration successful. Please login to continue.";
            header("Location: login.html");
            exit();
        } else {
            // Registration failed
            echo "Error: " . $sql . "<br>" . $conn->error;
        }
    }

    // Close the database connection
    $conn->close();
}
?>
