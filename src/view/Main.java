package view;

import javax.swing.*;
import net.miginfocom.swing.MigLayout;
import view.pages.Login;
import java.awt.Toolkit;

public class Main extends JFrame {
    private JPanel contentPane;

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            try {
                showLoginWindow(); // Hiển thị cửa sổ đăng nhập trước
            } catch (Exception e) {
                e.printStackTrace();
            }
        });
    }

    /**
     * Hiển thị cửa sổ đăng nhập.
     */
    private static void showLoginWindow() {
        JFrame loginFrame = new JFrame("Login");
        loginFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        loginFrame.setSize(350, 250);
        loginFrame.setResizable(false);
        loginFrame.getContentPane().setLayout(new MigLayout("fill", "[fill]", "[fill]"));

        Login loginPanel = new Login(() -> {
            loginFrame.dispose(); // Đóng cửa sổ đăng nhập
            showMainWindow(); // Mở giao diện chính
        });

        loginFrame.getContentPane().add(loginPanel, "grow");
        loginFrame.setLocationRelativeTo(null); // Hiển thị giữa màn hình
        loginFrame.setVisible(true);
    }

    /**
     * Hiển thị giao diện chính sau khi đăng nhập thành công.
     */
    private static void showMainWindow() {
        Main mainFrame = new Main();
        mainFrame.setVisible(true);
    }

    public Main() {
        setIconImage(Toolkit.getDefaultToolkit().getImage(Main.class.getResource("/images/icon.png")));
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setBounds(-5, 0, 1554, 680);
        setTitle("Billards Shop Management");
        setResizable(false);

        contentPane = new JPanel(new MigLayout("fillx, filly", "[220!]0[fill, 100%]0", "0[fill]0"));
        setContentPane(contentPane);

        // Tạo Body trước, sau đó truyền vào Sidebar để Sidebar có thể tương tác với Body
        Body body = new Body();
        Sidebar sidebar = new Sidebar(body);  // Chuyển đối tượng body vào Sidebar

        // Thêm Sidebar và Body vào contentPane
        contentPane.add(sidebar, "width 220:220:220"); // Sidebar nằm bên trái với chiều rộng 220px
        contentPane.add(body, "grow"); // Body chiếm phần còn lại
    }
}
