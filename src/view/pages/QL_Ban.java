package view.pages;

import javax.swing.JPanel;
import javax.swing.JLabel;
import javax.swing.JOptionPane;

import java.awt.Font;
import javax.swing.SwingConstants;
import javax.swing.JTable;
import javax.swing.table.DefaultTableModel;
import java.awt.Color;

import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
import javax.swing.JScrollPane;
import controller.QLBanController;
import model.Model_Ban;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.swing.JButton;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;

public class QL_Ban extends JPanel {

    private Model_Ban model;
    public JTable table;
    private int selectedTableId = -1; // Biến lưu lại tableId của bàn được chọn

    public QL_Ban() {
        setBackground(new Color(255, 255, 255));
        setSize(1050, 660);
        setLayout(null);

        QLBanController controller = new QLBanController(this);

        // Tạo các JLabel tượng trưng cho các bàn
        JLabel bt_ban01 = createTableLabel(0, 11, controller, 1);
        JLabel bt_ban02 = createTableLabel(284, 11, controller, 2);
        JLabel bt_ban06 = createTableLabel(568, 11, controller, 3);
        JLabel bt_ban03 = createTableLabel(0, 211, controller, 4);
        JLabel bt_ban04 = createTableLabel(284, 211, controller, 5);
        JLabel bt_ban05 = createTableLabel(568, 211, controller, 6);

        // Tạo các nhãn cho tên bàn
        JLabel banText_1 = createLabel("BÀN 01", 82, 155);
        JLabel banText_2 = createLabel("BÀN 02", 360, 155);
        JLabel banText_3 = createLabel("BÀN 03", 643, 155);
        JLabel banText_4 = createLabel("BÀN 04", 82, 365);
        JLabel banText_5 = createLabel("BÀN 05", 360, 365);
        JLabel banText_6 = createLabel("BÀN 06", 643, 365);
        
        Map<Integer, JLabel> tableLabels = new HashMap<>();
        tableLabels.put(1, createLabel("BÀN 01", 82, 155));
        tableLabels.put(2, createLabel("BÀN 02", 360, 155));

        // Tạo bảng hiển thị thông tin bàn
        table = new JTable();
        table.setFont(new Font("Tahoma", Font.BOLD, 17));
        table.setModel(new DefaultTableModel(
            new Object[][] {},
            new String[] {
                "Mã số bàn", "Thời gian bắt đầu", "Thức uống gọi kèm", "Số lượng"
            }
        ));
        JScrollPane scrollPane = new JScrollPane(table);
        scrollPane.setBounds(10, 408, 941, 241);
        styleScrollPane(scrollPane);
        add(scrollPane);

        // Nút "Chỉnh sửa thông tin bàn"
        JButton editDatabase = new JButton("Sửa");
        editDatabase.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                if (selectedTableId != -1) { // Kiểm tra nếu có bàn được chọn
                    showEditDialog(selectedTableId);
                } else {
                    // Thông báo nếu chưa chọn bàn
                    JOptionPane.showMessageDialog(null, "Vui lòng chọn bàn cần chỉnh sửa.", "Lỗi", JOptionPane.ERROR_MESSAGE);
                }
            }
        });
        editDatabase.setBounds(961, 450, 92, 35);
        styleButton(editDatabase);
        add(editDatabase);

        // Các nút khác
        JButton refreshButton = new JButton("Làm mới");
        refreshButton.addActionListener(new ActionListener() {
        	public void actionPerformed(ActionEvent e) {
        		controller.loadDataForTable(selectedTableId);
        	}
        });
        refreshButton.setBounds(961, 496, 92, 35);
        styleButton(refreshButton);
        add(refreshButton);

        JButton thanhToan = new JButton("Bill");
        thanhToan.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                if (selectedTableId != -1) {
                    // Hiển thị hộp thoại xác nhận
                    int confirm = JOptionPane.showConfirmDialog(
                        null, 
                        "Bạn có chắc chắn muốn thanh toán bàn " + selectedTableId + "?", 
                        "Xác nhận thanh toán", 
                        JOptionPane.YES_NO_OPTION
                    );

                    // Nếu người dùng chọn "YES"
                    if (confirm == JOptionPane.YES_OPTION) {
                        double totalAmount = controller.thanhToanTien(selectedTableId); // Lấy số tiền cần thanh toán
                        String playTime = String.valueOf(controller.calculateTimeDifference(controller.getStartTime(selectedTableId))); // Thời gian chơi

                        // Lấy danh sách nước uống và số lượng từ database
                        String drinks = controller.getDrinksForTable(selectedTableId);
                        int quantities = controller.getDrinkQuantitiesForTable(selectedTableId);

                        // Hiển thị hóa đơn
                        new Bill(String.valueOf(selectedTableId), playTime, drinks, quantities, totalAmount);
                        
                        // Reset bàn
                        controller.doneBill(selectedTableId);

                        // Cập nhật lại dữ liệu bàn
                        controller.loadDataForTable(selectedTableId);
                    }
                } else {
                    JOptionPane.showMessageDialog(null, "Vui lòng chọn bàn cần thanh toán.", "Lỗi", JOptionPane.ERROR_MESSAGE);
                }
            }
        });



        thanhToan.setBounds(961, 542, 92, 35);
        styleButton(thanhToan);
        add(thanhToan);

        this.setVisible(true);
        
        JButton editCost = new JButton("");
        editCost.setIcon(new ImageIcon(QL_Ban.class.getResource("/images/edit.png")));
        editCost.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                // Mở lớp EditCost khi nhấn nút
                EditCost editCostWindow = new EditCost();
                editCostWindow.frameedit.setVisible(true);  // Mở cửa sổ EditCost
            }
        });
        editCost.setBounds(916, 138, 67, 62);
        add(editCost);
    }
    // Hiển thị cửa sổ chỉnh sửa thông tin bàn
    private void showEditDialog(int tableId) {
        // Tạo cửa sổ chỉnh sửa và truyền tableId
        EditTableDialog dialog = new EditTableDialog(this, "Chỉnh sửa thông tin bàn", tableId);
        dialog.setVisible(true);
    }

    // Tạo một JLabel cho bàn và gán sự kiện click
    private JLabel createTableLabel(int x, int y, QLBanController controller, int tableId) {
        JLabel label = new JLabel("New label");
        label.setIcon(new ImageIcon(QL_Ban.class.getResource("/images/bàn bia.png")));
        label.setBounds(x, y, 248, 143);
        label.setOpaque(true); // Đảm bảo label có thể hiển thị màu nền

        // Màu nền ban đầu và không có border
        label.setBackground(new Color(75, 0, 130));
        label.setBorder(null);

        // Sự kiện khi chuột di vào
        label.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseEntered(MouseEvent e) {
                // Đổi màu nền khi chuột vào
                label.setBackground(new Color(34, 133, 205)); // Màu xanh khi hover
                // Thêm border để tạo hiệu ứng "nổi lên"
                label.setBorder(javax.swing.BorderFactory.createLineBorder(new Color(255, 255, 255), 3));
            }

            @Override
            public void mouseExited(MouseEvent e) {
                // Đổi lại màu nền khi chuột rời đi
                label.setBackground(new Color(75, 0, 130)); // Quay lại màu ban đầu
                // Xóa border khi chuột rời đi
                label.setBorder(null);
            }

            @Override
            public void mouseClicked(MouseEvent e) {
                // Lưu tableId khi bàn được chọn
                selectedTableId = tableId;

                // Kiểm tra dữ liệu trong cơ sở dữ liệu
                boolean hasData = controller.checkDataForTable(selectedTableId);

                if (hasData) {
                    // Nếu có dữ liệu, tải thông tin và hiển thị
                    controller.loadDataForTable(selectedTableId);
                } else {
                    // Nếu không có dữ liệu, hiển thị hộp thoại xác nhận mở bàn
                    int confirm = JOptionPane.showConfirmDialog(
                        null,
                        "Bàn chưa được mở. Bạn có muốn mở bàn không?",
                        "Xác nhận mở bàn",
                        JOptionPane.YES_NO_OPTION
                    );

                    if (confirm == JOptionPane.YES_OPTION) {
                        // Mở hộp thoại chỉnh sửa để nhập dữ liệu mới
                        controller.addNewBan(selectedTableId);
                    }
                }
            }
        });

        add(label);
        return label;
    }

    // Tạo một JLabel cho tên bàn
    private JLabel createLabel(String text, int x, int y) {
        JLabel label = new JLabel(text);
        label.setHorizontalAlignment(SwingConstants.CENTER);
        label.setForeground(Color.RED);
        label.setFont(new Font("Tahoma", Font.BOLD, 20));
        label.setBounds(x, y, 107, 45);
        add(label);
        return label;
    }

    // Phương thức cập nhật bảng sau khi thay đổi thông tin bàn
    public void updateTableAfterEdit(int tableId, String thucUong, int soLuong, String note) {
        // Cập nhật dữ liệu trong cơ sở dữ liệu thông qua controller
        QLBanController controller = new QLBanController(this);
        controller.updateBanInDatabase(tableId, thucUong, soLuong, note);

        // Sau khi cập nhật, tải lại dữ liệu từ cơ sở dữ liệu
        controller.loadDataForTable(tableId);
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
}
