package controller;

import model.Model_Ban;
import view.pages.QL_Ban;

import javax.swing.Action;
import javax.swing.JOptionPane;
import javax.swing.table.DefaultTableModel;
import java.awt.event.ActionEvent;
import java.beans.PropertyChangeListener;
import java.sql.*;
import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.Date;

public class QLBanController implements Action {

    private QL_Ban ban;
    private static final String DB_URL = "jdbc:mysql://localhost:3306/owner";
    private static final String DB_USER = "root";
    private static final String DB_PASSWORD = "Zettc1702!";

    public QLBanController(QL_Ban ban) {
        this.ban = ban;
    }

    // Tạo kết nối cơ sở dữ liệu
    private Connection getConnection() throws SQLException {
        return DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
    }

    // Cập nhật dữ liệu lên bảng
    public void loadDataForTable(int tableId) {
        List<BanInfo> banData = getBanDataFromDatabase(tableId);
        updateTableWithBanData(banData);
    }

    // Cập nhật dữ liệu vào bảng
    private void updateTableWithBanData(List<BanInfo> banData) {
        DefaultTableModel model = (DefaultTableModel) ban.table.getModel();
        model.setRowCount(0); // Xóa tất cả dòng cũ trong bảng
        SimpleDateFormat sdf = new SimpleDateFormat("HH:mm:ss"); // Định dạng giờ

        // Thêm dữ liệu vào bảng
        for (BanInfo banInfo : banData) {
            Object[] row = new Object[5];
            row[0] = banInfo.getMaBan();
            row[1] = (banInfo.getThoiGianMoBan() != null) ? sdf.format(banInfo.getThoiGianMoBan()) : ""; // Chuyển thành chuỗi giờ
            row[2] = banInfo.getThucUong();
            row[3] = banInfo.getSoLuong();
            model.addRow(row);
        }
    }

    // Phương thức lấy dữ liệu từ cơ sở dữ liệu
    public List<BanInfo> getBanDataFromDatabase(int tableId) {
        List<BanInfo> banData = new ArrayList<>();
        String query = "SELECT * FROM BanInfo WHERE ID_Ban = ?";

        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(query)) {

            stmt.setInt(1, tableId);
            ResultSet rs = stmt.executeQuery();

            while (rs.next()) {
                BanInfo ban = new BanInfo();
                ban.setMaBan(rs.getInt("ID_Ban"));
                ban.setThoiGianMoBan(rs.getTimestamp("DateStart"));
                ban.setThucUong(rs.getString("Food"));
                ban.setSoLuong(rs.getInt("Amount"));
                banData.add(ban);
            }

        } catch (SQLException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(ban, "Lỗi truy vấn dữ liệu.", "Lỗi", JOptionPane.ERROR_MESSAGE);
        }

        return banData;
    }

    // Phương thức cập nhật dữ liệu vào cơ sở dữ liệu
    public void updateBanInDatabase(int tableId, String thucUong, int soLuong, String Note) {
        String query = "UPDATE BanInfo SET Food = ?, Amount = ?, Note = ? WHERE ID_Ban = ?";

        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(query)) {
            
            // Cập nhật các trường cần thiết
            stmt.setString(1, thucUong);
            stmt.setInt(2, soLuong);
            stmt.setString(3, Note);
            stmt.setInt(4, tableId);

            // Thực thi câu lệnh
            stmt.executeUpdate();

        } catch (SQLException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(null, "Lỗi cập nhật cơ sở dữ liệu.", "Lỗi", JOptionPane.ERROR_MESSAGE);
        }
    }
    public void deleteBanInDatabase(int tableId) {
        String resetQuery = "UPDATE BanInfo SET Food = '', Amount = 0, Note = '', is_active = FALSE WHERE ID_Ban = ?";

        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(resetQuery)) {
            stmt.setInt(1, tableId);

            // Thực thi câu lệnh
            stmt.executeUpdate();
            JOptionPane.showMessageDialog(null, "Bàn đã được xoá.", "Thông báo", JOptionPane.INFORMATION_MESSAGE);
        } catch (SQLException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(null, "Lỗi kết nối dữ liệu, vui lòng thử lại.", "Lỗi", JOptionPane.ERROR_MESSAGE);
        }
    }


    public boolean checkDataForTable(int tableId) {
        try {
            // Kết nối đến cơ sở dữ liệu và thực hiện truy vấn
            Connection conn = getConnection();
            String query = "SELECT is_active FROM BanInfo WHERE ID_Ban = ?";
            PreparedStatement stmt = conn.prepareStatement(query);
            stmt.setInt(1, tableId);

            ResultSet rs = stmt.executeQuery();
            if (rs.next()) {
            	boolean isActive = rs.getBoolean("is_active");
            	return isActive; // Nếu có dữ liệu, trả về true
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return false; // Mặc định trả về false nếu có lỗi
    }

    public void addNewBan(int maBan) {
        Timestamp currentTime = new Timestamp(System.currentTimeMillis());  // Lấy thời gian hiện tại

        try (Connection conn = getConnection()) {
            // Kiểm tra xem ID_Ban đã tồn tại chưa (nếu không tồn tại mới thêm mới)
            String checkQuery = "SELECT COUNT(*) FROM BanInfo WHERE ID_Ban = ?";
            PreparedStatement checkStmt = conn.prepareStatement(checkQuery);
            checkStmt.setInt(1, maBan);
            ResultSet rs = checkStmt.executeQuery();

            if (rs.next() && rs.getInt(1) > 0) {
                // Nếu bàn đã tồn tại, chỉ cần cập nhật is_active = TRUE và DateStart
                String updateQuery = "UPDATE BanInfo SET is_active = TRUE, DateStart = ? WHERE ID_Ban = ?";
                PreparedStatement stmt = conn.prepareStatement(updateQuery);
                stmt.setTimestamp(1, currentTime);  // Cập nhật thời gian mở bàn vào DateStart
                stmt.setInt(2, maBan);
                stmt.executeUpdate();
            } else {
                // Nếu bàn chưa tồn tại, thực hiện thêm mới và đánh dấu là hoạt động
                String insertQuery = "INSERT INTO BanInfo (ID_Ban, is_active, DateStart) VALUES (?, TRUE, ?)";
                PreparedStatement stmt = conn.prepareStatement(insertQuery);
                stmt.setInt(1, maBan);
                stmt.setTimestamp(2, currentTime);  // Thêm thời gian hiện tại vào DateStart
                stmt.executeUpdate();
            }
        } catch (SQLException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(null, "Lỗi khi thêm bàn mới.", "Lỗi", JOptionPane.ERROR_MESSAGE);
        }
    }
    public double thanhToanTien(int tableId) {
        double totalCost = 0.0;

        try (Connection conn = getConnection()) {
            // Lấy thông tin bàn từ cơ sở dữ liệu
            String query = "SELECT DateStart, Cost, Amount FROM BanInfo WHERE ID_Ban = ?";
            try (PreparedStatement ps = conn.prepareStatement(query)) {
                ps.setInt(1, tableId);

                try (ResultSet rs = ps.executeQuery()) {
                    if (rs.next()) {
                        // Lấy dữ liệu từ kết quả truy vấn
                        String dateStart = rs.getString("DateStart");
                        double cost = rs.getDouble("Cost");
                        int amount = rs.getInt("Amount");

                        // Tính thời gian chênh lệch (giờ)
                        double hoursElapsed = calculateTimeDifference(dateStart);

                        // Tính tổng tiền thanh toán
                        totalCost = hoursElapsed * cost + amount * 10000; // Giả sử 10000 là giá cho mỗi đồ uống
                    } else {
                        throw new SQLException("Không tìm thấy bàn với mã bàn: " + tableId);
                    }
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }

        return totalCost;
    }

    // Phương thức tính thời gian chênh lệch (giờ)
    public double calculateTimeDifference(String startTime) {
        try {
            // Định dạng thời gian
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

            // Chuyển đổi thời gian bắt đầu từ chuỗi sang đối tượng Date
            Date startDate = sdf.parse(startTime);

            // Lấy thời gian hiện tại
            Date currentDate = new Date();

            // Tính chênh lệch thời gian (ms)
            long differenceInMillis = currentDate.getTime() - startDate.getTime();

            // Chuyển đổi thời gian từ ms sang giờ
            double hours = TimeUnit.MILLISECONDS.toHours(differenceInMillis);

            // Tính phần thập phân (phút chia cho 60 để chuyển thành giờ)
            double minutes = TimeUnit.MILLISECONDS.toMinutes(differenceInMillis) % 60;
            double fractionalHours = hours + (minutes / 60.0);

            // Làm tròn kết quả đến 2 chữ số thập phân
            DecimalFormat df = new DecimalFormat("#.00");
            return Double.parseDouble(df.format(fractionalHours));
        } catch (Exception e) {
            e.printStackTrace();
            return 0; // Trả về 0 nếu xảy ra lỗi
        }
    }
    public String getStartTime(int tableId) {
        String startTime = null;
        String query = "SELECT DateStart FROM BanInfo WHERE ID_Ban = ?";

        try (PreparedStatement preparedStatement = getConnection().prepareStatement(query)) {
            preparedStatement.setInt(1, tableId);

            try (ResultSet resultSet = preparedStatement.executeQuery()) {
                if (resultSet.next()) {
                    startTime = resultSet.getString("DateStart"); // Lấy giá trị của cột start_time
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(null, "Lỗi khi lấy thời gian bắt đầu.", "Lỗi", JOptionPane.ERROR_MESSAGE);
        }

        return startTime;
    }
    public String getDrinksForTable(int tableId) {
        String drinks = null;
        String query = "SELECT Food FROM BanInfo WHERE ID_Ban = ?";

        try (PreparedStatement preparedStatement = getConnection().prepareStatement(query)) {
            preparedStatement.setInt(1, tableId);

            try (ResultSet resultSet = preparedStatement.executeQuery()) {
                if (resultSet.next()) {
                    drinks = resultSet.getString("Food");
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(null, "Lỗi khi lấy dữ liệu đồ uống.", "Lỗi", JOptionPane.ERROR_MESSAGE);
        }

        return drinks;
    }
    public int getDrinkQuantitiesForTable(int tableId) {
        int amount = 0;
        String query = "SELECT Amount FROM BanInfo WHERE ID_Ban = ?";

        try (PreparedStatement preparedStatement = getConnection().prepareStatement(query)) {
            preparedStatement.setInt(1, tableId);

            try (ResultSet resultSet = preparedStatement.executeQuery()) {
                if (resultSet.next()) {
                    amount = resultSet.getInt("Amount");
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(null, "Lỗi khi lấy dữ liệu số lượng đồ uống.", "Lỗi", JOptionPane.ERROR_MESSAGE);
        }

        return amount;
    }
    public void doneBill(int tableId) {
        String resetQuery = "UPDATE BanInfo SET Food = '', Amount = 0, Note = '', is_active = FALSE WHERE ID_Ban = ?";

        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(resetQuery)) {
            stmt.setInt(1, tableId);

            // Thực thi câu lệnh
            stmt.executeUpdate();
        } catch (SQLException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(null, "Lỗi kết nối dữ liệu, vui lòng thử lại.", "Lỗi", JOptionPane.ERROR_MESSAGE);
        }
    }

    @Override
    public void actionPerformed(ActionEvent e) {
        // Xử lý sự kiện hành động nếu cần
    }

    @Override
    public Object getValue(String key) {
        return null;
    }

    @Override
    public void putValue(String key, Object value) {
        // Xử lý nếu cần
    }

    @Override
    public void setEnabled(boolean b) {
        // Xử lý nếu cần
    }

    @Override
    public boolean isEnabled() {
        return false;
    }

    @Override
    public void addPropertyChangeListener(PropertyChangeListener listener) {
        // Xử lý nếu cần
    }

    @Override
    public void removePropertyChangeListener(PropertyChangeListener listener) {
        // Xử lý nếu cần
    }
}
