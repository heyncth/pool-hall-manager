package view;

import javax.swing.*;
import java.awt.*;
import view.pages.QL_Ban;
import view.pages.StatusOfTable;

public class Body extends JPanel {
    private CardLayout cardLayout;
    private JPanel cardPanel;
    private QL_Ban ban;
    private StatusOfTable info;

    public Body() {
        setBackground(new Color(255, 255, 255));
        setSize(1050, 660);
        setLayout(new BorderLayout());

        cardLayout = new CardLayout();
        cardPanel = new JPanel(cardLayout);

        ban = new QL_Ban();
        info = new StatusOfTable();

        cardPanel.add(ban, "Quản lý bàn");
        cardPanel.add(info, "Thông tin bàn");

        add(cardPanel, BorderLayout.CENTER);

        cardLayout.show(cardPanel, "Quản lý bàn");
    }

    // Phương thức để chuyển đổi giữa các tab
    public void showTab(String tabName) {
        cardLayout.show(cardPanel, tabName);
    }

    // Getter để truy cập tab "Thông tin bàn"
    public StatusOfTable getInfo() {
        return info;
    }
}
