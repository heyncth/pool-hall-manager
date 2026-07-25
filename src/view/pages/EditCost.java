package view.pages;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.sql.*;

public class EditCost {

    private static final String DB_URL = "jdbc:mysql://localhost:3306/owner";
    private static final String DB_USER = "root";
    private static final String DB_PASSWORD = "Zettc1702!";

    JFrame frameedit;
    private JComboBox<Integer> comboBoxIdBan;
    private JComboBox<String> comboBoxTableType; // ComboBox cho loại bàn
    private JTextField textFieldCost;
    private JButton btnUpdateCost;

    public static void main(String[] args) {
        EventQueue.invokeLater(() -> {
            try {
                EditCost window = new EditCost();
                window.frameedit.setVisible(true);
            } catch (Exception e) {
                e.printStackTrace();
            }
        });
    }

    public EditCost() {
        initialize();
    }

    private Connection getConnection() throws SQLException {
        return DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
    }

    private void initialize() {
        frameedit = new JFrame("Điều chỉnh giá bàn.");
        frameedit.setBounds(100, 100, 450, 300);
        frameedit.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
        frameedit.setResizable(false);
        frameedit.setLocationRelativeTo(null);
        frameedit.getContentPane().setLayout(null); // Không sử dụng layout

        // Label "Chọn mã bàn"
        JLabel lblIdBan = new JLabel("Chọn mã bàn:");
        lblIdBan.setFont(new Font("Tahoma", Font.BOLD, 14));
        lblIdBan.setBounds(50, 30, 120, 30);
        frameedit.getContentPane().add(lblIdBan);

        // ComboBox để chọn mã bàn
        comboBoxIdBan = new JComboBox<>();
        comboBoxIdBan.setFont(new Font("Tahoma", Font.PLAIN, 14));
        comboBoxIdBan.setBounds(180, 30, 200, 30);
        loadIdBanComboBox();
        frameedit.getContentPane().add(comboBoxIdBan);

        // Label "Loại bàn"
        JLabel lblTableType = new JLabel("Loại bàn:");
        lblTableType.setFont(new Font("Tahoma", Font.BOLD, 14));
        lblTableType.setBounds(50, 80, 120, 30);
        frameedit.getContentPane().add(lblTableType);

        // ComboBox cho loại bàn
        comboBoxTableType = new JComboBox<>(new String[]{"Mr Sung", "Samurai 2024", "Aliex"});
        comboBoxTableType.setFont(new Font("Tahoma", Font.PLAIN, 14));
        comboBoxTableType.setBounds(180, 80, 200, 30);
        frameedit.getContentPane().add(comboBoxTableType);

        // Label "Nhập giá"
        JLabel lblCost = new JLabel("Nhập giá:");
        lblCost.setFont(new Font("Tahoma", Font.BOLD, 14));
        lblCost.setBounds(50, 130, 120, 30);
        frameedit.getContentPane().add(lblCost);

        // TextField để nhập giá
        textFieldCost = new JTextField();
        textFieldCost.setFont(new Font("Tahoma", Font.PLAIN, 14));
        textFieldCost.setBounds(180, 130, 200, 30);
        frameedit.getContentPane().add(textFieldCost);

        // Nút cập nhật
        btnUpdateCost = new JButton("Cập nhật");
        btnUpdateCost.setFont(new Font("Tahoma", Font.BOLD, 14));
        btnUpdateCost.setBackground(new Color(64, 155, 255));
        btnUpdateCost.setForeground(Color.WHITE);
        btnUpdateCost.setBounds(163, 187, 114, 30);
        btnUpdateCost.addActionListener(e -> updateCostInDatabase());
        frameedit.getContentPane().add(btnUpdateCost);
    }

    private void loadIdBanComboBox() {
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement("SELECT ID_Ban FROM BanInfo");
             ResultSet rs = stmt.executeQuery()) {

            while (rs.next()) {
                comboBoxIdBan.addItem(rs.getInt("ID_Ban"));
            }
        } catch (SQLException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(frameedit, "Lỗi kết nối cơ sở dữ liệu.", "Lỗi", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void updateCostInDatabase() {
        Integer selectedIdBan = (Integer) comboBoxIdBan.getSelectedItem();
        String selectedTableType = (String) comboBoxTableType.getSelectedItem();
        String costStr = textFieldCost.getText();

        if (selectedIdBan != null && selectedTableType != null && !costStr.isEmpty()) {
            try (Connection conn = getConnection()) {
                String query = "UPDATE BanInfo SET Cost = ?, name_table = ? WHERE ID_Ban = ?";
                PreparedStatement stmt = conn.prepareStatement(query);
                stmt.setFloat(1, Float.parseFloat(costStr));
                stmt.setString(2, selectedTableType);
                stmt.setInt(3, selectedIdBan);

                int rowsUpdated = stmt.executeUpdate();
                if (rowsUpdated > 0) {
                    JOptionPane.showMessageDialog(frameedit, "Cập nhật thành công!", "Thành công", JOptionPane.INFORMATION_MESSAGE);
                } else {
                    JOptionPane.showMessageDialog(frameedit, "Không tìm thấy bàn với ID đó.", "Lỗi", JOptionPane.ERROR_MESSAGE);
                }
            } catch (SQLException e) {
                e.printStackTrace();
                JOptionPane.showMessageDialog(frameedit, "Lỗi khi cập nhật.", "Lỗi", JOptionPane.ERROR_MESSAGE);
            }
        } else {
            JOptionPane.showMessageDialog(frameedit, "Vui lòng chọn ID bàn, loại bàn và nhập giá.", "Lỗi", JOptionPane.WARNING_MESSAGE);
        }
    }
}
