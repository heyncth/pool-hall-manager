package view.pages;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.sql.*;

public class Login extends JPanel {
    private Runnable onLoginSuccess; // Callback để thông báo đăng nhập thành công

    public Login(Runnable onLoginSuccess) {
        this.onLoginSuccess = onLoginSuccess;

        setLayout(null); // Sử dụng null layout
        setPreferredSize(new Dimension(350, 250)); // Đặt kích thước cố định cho JPanel

        // Username label và field
        JLabel userLabel = new JLabel("Username:");
        userLabel.setFont(new Font("Arial", Font.PLAIN, 12));
        userLabel.setBounds(50, 30, 100, 20);

        JTextField userField = new JTextField();
        userField.setFont(new Font("Arial", Font.PLAIN, 12));
        userField.setBounds(130, 30, 150, 20);

        // Password label và field
        JLabel passLabel = new JLabel("Password:");
        passLabel.setFont(new Font("Arial", Font.PLAIN, 12));
        passLabel.setBounds(50, 70, 100, 20);

        JPasswordField passField = new JPasswordField();
        passField.setFont(new Font("Arial", Font.PLAIN, 12));
        passField.setBounds(130, 70, 150, 20);

        // Nút login
        JButton loginButton = new JButton("Login");
        loginButton.setBounds(130, 110, 80, 30);
        loginButton.setBackground(new Color(0, 123, 255)); // Màu xanh dương cho nút
        loginButton.setForeground(Color.WHITE);
        loginButton.setFont(new Font("Arial", Font.BOLD, 14));
        loginButton.setFocusPainted(false);
        loginButton.setBorder(BorderFactory.createLineBorder(new Color(0, 123, 255), 2));
        // Thông báo
        JLabel messageLabel = new JLabel("", SwingConstants.CENTER);
        messageLabel.setBounds(50, 138, 250, 30);
        messageLabel.setFont(new Font("Arial", Font.PLAIN, 12));

        JLabel messageLabel2 = new JLabel("", SwingConstants.CENTER);
        messageLabel2.setBounds(50, 162, 250, 30);
        messageLabel2.setFont(new Font("Arial", Font.PLAIN, 12));

        // Thêm các thành phần vào panel
        add(userLabel);
        add(userField);
        add(passLabel);
        add(passField);
        add(loginButton);
        add(messageLabel);
        add(messageLabel2);

        // ActionListener cho nút login
        loginButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                String username = userField.getText().trim();
                String password = new String(passField.getPassword()).trim();

                if (authenticate(username, password)) {
                    messageLabel.setText("Đăng nhập thành công!");
                    messageLabel2.setText("Đang chuyển tới màn hình chính...");
                    messageLabel.setForeground(Color.GREEN);
                    messageLabel2.setForeground(Color.GREEN);

                    // Hiển thị thông báo trong 2 giây, sau đó chuyển giao diện
                    Timer timer = new Timer(1500, new ActionListener() {
                        @Override
                        public void actionPerformed(ActionEvent e) {
                            onLoginSuccess.run(); // Gọi callback để chuyển giao diện
                        }
                    });
                    timer.setRepeats(false); // Chỉ chạy 1 lần
                    timer.start();
                } else {
                    messageLabel.setText("Tài khoản hoặc mật khẩu không chính xác.");
                    messageLabel.setForeground(Color.RED);
                }
            }
        });
    }

    private boolean authenticate(String username, String password) {
        String url = "jdbc:mysql://localhost:3306/owner";
        String dbUser = "root"; // USER Database
        String dbPass = "Zettc1702!"; // Password Database

        String query = "SELECT * FROM users WHERE username = ? AND password = ?";

        try (Connection conn = DriverManager.getConnection(url, dbUser, dbPass);
             PreparedStatement stmt = conn.prepareStatement(query)) {

            stmt.setString(1, username);
            stmt.setString(2, password);

            ResultSet rs = stmt.executeQuery();
            return rs.next();

        } catch (SQLException ex) {
            ex.printStackTrace();
            return false;
        }
    }
}
