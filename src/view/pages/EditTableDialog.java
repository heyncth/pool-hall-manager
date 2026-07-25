package view.pages;

import javax.swing.JDialog;
import javax.swing.JPanel;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JTextField;
import javax.swing.JButton;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.Color;
import java.awt.Font;
import controller.QLBanController;
import javax.swing.ImageIcon;
import javax.swing.JList;
import javax.swing.JComboBox;

public class EditTableDialog extends JDialog {
    private JTextField txtnote;
    private JComboBox<String> thucUong;
    private JComboBox<String> soLuong;
    private int maBan;

    public EditTableDialog(QL_Ban parentPanel, String title, int maBan) {
        setTitle(title);
        setBounds(100, 100, 419, 366);
        setModal(true);
        setResizable(false);
        setLocationRelativeTo(null);

        this.maBan = maBan;

        JPanel contentPanel = new JPanel();
        contentPanel.setLayout(null);
        contentPanel.setBackground(new Color(255, 255, 255));
        setContentPane(contentPanel);

        JLabel lblThucUong = new JLabel("Thức uống:");
        lblThucUong.setFont(new Font("Tahoma", Font.PLAIN, 14));
        lblThucUong.setBounds(20, 165, 120, 30);
        contentPanel.add(lblThucUong);

        JLabel lblSoLuong = new JLabel("Số lượng:");
        lblSoLuong.setFont(new Font("Tahoma", Font.PLAIN, 14));
        lblSoLuong.setBounds(20, 206, 120, 30);
        contentPanel.add(lblSoLuong);

        JLabel lblnote = new JLabel("Ghi chú:");
        lblnote.setFont(new Font("Tahoma", Font.PLAIN, 14));
        lblnote.setBounds(20, 247, 120, 30);
        contentPanel.add(lblnote);

        txtnote = new JTextField();
        txtnote.setFont(new Font("Tahoma", Font.PLAIN, 14));
        txtnote.setBounds(150, 248, 200, 30);
        contentPanel.add(txtnote);

        JButton btnSave = new JButton("Lưu");
        btnSave.setFont(new Font("Tahoma", Font.BOLD, 14));
        btnSave.setBackground(new Color(34, 133, 205));
        btnSave.setForeground(Color.WHITE);
        btnSave.setBounds(40, 288, 100, 30);
        btnSave.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                updateTableData();
            }
        });
        contentPanel.add(btnSave);

        JButton btnCancel = new JButton("Hủy");
        btnCancel.setFont(new Font("Tahoma", Font.BOLD, 14));
        btnCancel.setBackground(new Color(255, 69, 0));
        btnCancel.setForeground(Color.WHITE);
        btnCancel.setBounds(160, 289, 100, 30);
        btnCancel.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                dispose();
            }
        });
        contentPanel.add(btnCancel);

        // Nút Xoá Bàn
        JButton btnDelete = new JButton("Xoá bàn");
        btnDelete.setFont(new Font("Tahoma", Font.BOLD, 14));
        btnDelete.setBackground(new Color(204, 0, 0)); // Màu đỏ đậm
        btnDelete.setForeground(Color.WHITE);
        btnDelete.setBounds(282, 289, 100, 30);
        btnDelete.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                deleteTableData();
            }
        });
        contentPanel.add(btnDelete);

        JLabel lblNewLabel = new JLabel("New label");
        lblNewLabel.setIcon(new ImageIcon(EditTableDialog.class.getResource("/images/billardBONG.png")));
        lblNewLabel.setBounds(123, 11, 149, 129);
        contentPanel.add(lblNewLabel);

        thucUong = new JComboBox<>(new String[]{"Không","Trà sữa", "Cà phê", "Nước ngọt", "Nước lọc"});
        thucUong.setBounds(150, 167, 200, 30);
        contentPanel.add(thucUong);

        soLuong = new JComboBox<>(new String[]{"1", "2", "3", "4", "5"});
        soLuong.setEditable(true); // Cho phép nhập tay
        soLuong.setBounds(150, 208, 200, 30);
        contentPanel.add(soLuong);
    }

    private void updateTableData() {
        try {
            String selectedThucUong = (String) thucUong.getSelectedItem();
            String soLuongText = (String) soLuong.getSelectedItem();
            int selectedSoLuong = Integer.parseInt(soLuongText);
            String note = txtnote.getText();

            QLBanController controller = new QLBanController(null);
            controller.updateBanInDatabase(maBan, selectedThucUong, selectedSoLuong, note);

            dispose();
        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Vui lòng nhập số trong ô số lượng.", "Lỗi", JOptionPane.ERROR_MESSAGE);
        }
    }

    // Phương thức xóa bàn
    private void deleteTableData() {
        int confirm = JOptionPane.showConfirmDialog(this, "Bạn có chắc muốn xoá bàn này?", "Xác nhận xóa", JOptionPane.YES_NO_OPTION);

        if (confirm == JOptionPane.YES_OPTION) {
            QLBanController controller = new QLBanController(null);
            controller.deleteBanInDatabase(maBan); // Gọi phương thức deleteBanInDatabase trong controller để xóa bàn

            // Đóng cửa sổ sau khi xóa
            dispose();
        }
    }
}
