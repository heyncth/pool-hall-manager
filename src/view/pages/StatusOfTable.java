package view.pages;

import javax.swing.*;
import java.awt.*;
import javax.swing.table.DefaultTableModel;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.ActionEvent;
import controller.BanInfo;
import java.util.List;

public class StatusOfTable extends JPanel {
    
    private JTable table;
    
    public StatusOfTable() {
        setBackground(new Color(255, 255, 255));
        setSize(1050, 660);
        setLayout(null);
        
        // Tạo bảng hiển thị trạng thái của các bàn
        table = new JTable();
        table.setFont(new Font("Tahoma", Font.BOLD, 17));
        table.setModel(new DefaultTableModel(
            new Object[][] {}, // Dữ liệu sẽ được thêm sau khi lấy từ cơ sở dữ liệu
            new String[] {
                "Mã bàn", "Trạng thái", "Loại bàn","Giá tiền"
            }
        ));
        
        // Tạo JScrollPane để bọc bảng
        JScrollPane scrollPane = new JScrollPane(table);
        scrollPane.setBounds(10, 10, 941, 400); // Vị trí và kích thước của JScrollPane
        styleScrollPane(scrollPane);
        add(scrollPane);
        
        // Nút làm mới bảng
        JButton refreshButton = new JButton("Làm mới");
        refreshButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                refreshTableData();
            }
        });
        refreshButton.setBounds(958, 28, 92, 35); // Vị trí và kích thước nút
        styleButton(refreshButton);
        add(refreshButton);
        
        // Hiển thị JPanel
        this.setVisible(true);
    }
    
    // Phương thức để làm mới dữ liệu trong bảng (sử dụng lại controller để load dữ liệu)
    public void refreshTableData() {
        // Sử dụng BanInfo để lấy dữ liệu từ cơ sở dữ liệu
        BanInfo banInfo = new BanInfo();
        List<String[]> banStatusList = banInfo.getBanStatus();
        
        // Cập nhật bảng với dữ liệu mới
        DefaultTableModel model = (DefaultTableModel) table.getModel();
        model.setRowCount(0); // Xóa dữ liệu cũ trong bảng
        for (String[] row : banStatusList) {
            model.addRow(row); // Thêm từng dòng dữ liệu vào bảng
        }
    }
    private void styleScrollPane(JScrollPane scrollPane) {
        // Đặt màu nền cho bảng trong JScrollPane
        JTable table = (JTable) scrollPane.getViewport().getView();
        table.setBackground(new Color(240, 240, 240));  // Màu nền cho bảng
        table.setSelectionBackground(new Color(0, 102, 204));  // Màu nền khi chọn dòng
        table.setSelectionForeground(Color.WHITE);  // Màu chữ khi chọn dòng
        table.setGridColor(new Color(200, 200, 200));  // Màu đường kẻ trong bảng
        table.setRowHeight(30);  // Chiều cao của mỗi dòng
        table.setFont(new Font("Tahoma", Font.BOLD, 14));  // Đặt font chữ cho bảng
    }
    private void styleButton(JButton button) {
        button.setFont(new Font("Tahoma", Font.BOLD, 12));  // Đặt font chữ
        button.setBackground(new Color(34, 133, 205)); // Màu nền ban đầu
        button.setForeground(Color.WHITE); // Màu chữ
        button.setFocusPainted(false);  // Loại bỏ đường viền khi nhấn
        button.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));  // Thêm lề cho nút

        // Hiệu ứng hover (di chuột vào)
        button.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseEntered(MouseEvent e) {
                button.setBackground(new Color(0, 102, 204)); // Màu khi hover
            }

            @Override
            public void mouseExited(MouseEvent e) {
                button.setBackground(new Color(34, 133, 205)); // Quay lại màu ban đầu
            }
        });
    }
}
