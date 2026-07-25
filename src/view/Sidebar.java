package view;

import javax.swing.*;
import java.awt.Color;
import java.awt.Font;
import javax.swing.SwingConstants;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

public class Sidebar extends JPanel {
    private Body body;

    public Sidebar(Body body) {
        this.body = body;

        // Thiết lập chung cho Sidebar
        setBackground(new Color(74, 170, 239));
        setSize(220, 680);
        setLayout(null);

        // Thêm logo và tiêu đề
        addLogoAndTitle();

        // Thêm các nút chức năng
        addMenuButtons();
    }

    /**
     * Thêm logo và tiêu đề lên Sidebar.
     */
    private void addLogoAndTitle() {
        // Logo
        JLabel lblLogo = new JLabel("");
        lblLogo.setIcon(new ImageIcon(Sidebar.class.getResource("/images/billardBONG.png")));
        lblLogo.setHorizontalAlignment(SwingConstants.CENTER);
        lblLogo.setBounds(0, 0, 220, 156);
        add(lblLogo);

        // Tiêu đề
        JLabel lblTitle = new JLabel("BILLARD");
        lblTitle.setForeground(new Color(139, 0, 0));
        lblTitle.setHorizontalAlignment(SwingConstants.CENTER);
        lblTitle.setFont(new Font("Tahoma", Font.BOLD, 25));
        lblTitle.setBounds(0, 167, 220, 29);
        add(lblTitle);
    }

    /**
     * Thêm các nút chức năng lên Sidebar.
     */
    private void addMenuButtons() {
        // Nút Quản lý bàn
        JLabel lb_QL_Ban = createMenuButton("QUẢN LÝ BÀN", 216);
        lb_QL_Ban.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseEntered(MouseEvent e) {
                lb_QL_Ban.setBackground(new Color(34, 133, 205));
            }

            @Override
            public void mouseExited(MouseEvent e) {
                lb_QL_Ban.setBackground(new Color(173, 216, 230));
            }

            @Override
            public void mouseClicked(MouseEvent e) {
                // Hiển thị tab Quản lý bàn trong Body
                body.showTab("Quản lý bàn");
            }
        });
        add(lb_QL_Ban);

        // Nút Thông tin bàn
        JLabel lb_SOT = createMenuButton("THÔNG TIN BÀN", 280);
        lb_SOT.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseEntered(MouseEvent e) {
                lb_SOT.setBackground(new Color(34, 133, 205));
            }

            @Override
            public void mouseExited(MouseEvent e) {
                lb_SOT.setBackground(new Color(173, 216, 230));
            }

            @Override
            public void mouseClicked(MouseEvent e) {
                // Hiển thị tab Thông tin bàn trong Body
                body.showTab("Thông tin bàn");
                body.getInfo().refreshTableData();
            }
        });
        add(lb_SOT);
    }

    /**
     * Tạo một nút menu với văn bản và vị trí.
     *
     * @param text Văn bản hiển thị trên nút.
     * @param y    Tọa độ Y của nút.
     * @return JLabel được thiết lập như một nút menu.
     */
    private JLabel createMenuButton(String text, int y) {
        JLabel menuButton = new JLabel(text);
        menuButton.setForeground(new Color(255, 255, 255));
        menuButton.setHorizontalAlignment(SwingConstants.CENTER);
        menuButton.setFont(new Font("Tahoma", Font.BOLD, 20));
        menuButton.setBackground(new Color(173, 216, 230));
        menuButton.setOpaque(true);
        menuButton.setBounds(0, y, 220, 53);
        return menuButton;
    }
}
