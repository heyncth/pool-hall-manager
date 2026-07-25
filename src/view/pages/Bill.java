package view.pages;

import javax.swing.*;
import java.awt.*;

public class Bill {
    private JFrame frame;

    public Bill(String tableId, String playTime, String drinks, int quantities, double totalAmount) {
        frame = new JFrame("Hóa đơn");
        frame.setSize(400, 300);
        frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
        frame.setResizable(false);

        // Đặt cửa sổ giữa màn hình
        frame.setLocationRelativeTo(null);

        // Sử dụng null layout để tùy chỉnh vị trí các thành phần
        JPanel panel = new JPanel(null);
        panel.setBackground(Color.WHITE);

        // Font mặc định
        Font labelFont = new Font("Tahoma", Font.PLAIN, 14);
        Font headerFont = new Font("Tahoma", Font.BOLD, 18);

        // Tiêu đề hóa đơn
        JLabel titleLabel = new JLabel("HÓA ĐƠN", SwingConstants.CENTER);
        titleLabel.setFont(headerFont);
        titleLabel.setForeground(new Color(0, 102, 204)); // Màu xanh nhạt
        titleLabel.setBounds(100, 10, 200, 30); // Đặt vị trí và kích thước
        panel.add(titleLabel);

        // Thông tin hóa đơn
        JLabel tableIdLabel = new JLabel("Mã bàn: " + tableId);
        tableIdLabel.setFont(new Font("Tahoma", Font.BOLD, 14));
        tableIdLabel.setBounds(20, 60, 360, 25);
        panel.add(tableIdLabel);

        JLabel playTimeLabel = new JLabel("Thời gian chơi: " + playTime + " tiếng");
        playTimeLabel.setFont(new Font("Tahoma", Font.BOLD, 14));
        playTimeLabel.setBounds(20, 90, 360, 25);
        panel.add(playTimeLabel);

        if (drinks != null) {
            JLabel drinksLabel = new JLabel("Nước uống gọi kèm: " + drinks);
            drinksLabel.setFont(labelFont);
            drinksLabel.setBounds(20, 120, 360, 25);
            panel.add(drinksLabel);
        }

        JLabel quantitiesLabel = new JLabel("Số lượng: " + quantities);
        quantitiesLabel.setFont(new Font("Tahoma", Font.BOLD, 14));
        quantitiesLabel.setBounds(20, 150, 360, 25);
        panel.add(quantitiesLabel);

        JLabel totalLabel = new JLabel("Tổng tiền cần thanh toán: " + String.format("%.2f", totalAmount) + " VND");
        totalLabel.setFont(new Font("Tahoma", Font.BOLD | Font.ITALIC, 14));
        totalLabel.setForeground(new Color(255, 51, 51)); // Màu đỏ
        totalLabel.setBounds(20, 180, 360, 25);
        panel.add(totalLabel);

        // Nút đóng hóa đơn
        JButton closeButton = new JButton("Đóng");
        closeButton.setFont(new Font("Tahoma", Font.BOLD, 12));
        closeButton.setBackground(new Color(220, 220, 220));
        closeButton.setBounds(150, 220, 100, 30); // Đặt vị trí ở giữa
        closeButton.addActionListener(e -> frame.dispose());
        panel.add(closeButton);

        // Thêm panel vào frame
        frame.getContentPane().add(panel);
        frame.setVisible(true);
    }
}
