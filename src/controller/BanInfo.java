package controller;

import java.sql.Timestamp;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class BanInfo {
    private int maBan;
    private Timestamp thoiGianMoBan;
    private Timestamp thoiGianKetThuc;
    private String thucUong;
    private int soLuong;
    private double tongThanhToan;

    // Getters and setters
        
 // Kết nối đến cơ sở dữ liệu
    private Connection getConnection() throws SQLException {
        String url = "jdbc:mysql://localhost:3306/owner"; // Thay đổi đường dẫn cơ sở dữ liệu
        String username = "root"; // Thay đổi tên người dùng
        String password = "Zettc1702!"; // Thay đổi mật khẩu
        return DriverManager.getConnection(url, username, password);
    }
    
    // Lấy danh sách bàn từ cơ sở dữ liệu
    public List<String[]> getBanStatus() {
        List<String[]> banStatusList = new ArrayList<>();
        
        String query = "SELECT ID_Ban, is_active, name_table, Cost FROM BanInfo"; // Cập nhật tên bảng và cột theo cơ sở dữ liệu của bạn
        
        try (Connection conn = getConnection(); Statement stmt = conn.createStatement(); ResultSet rs = stmt.executeQuery(query)) {
            while (rs.next()) {
            	String status = "";
                String maBan = rs.getString("ID_Ban");
                boolean trangThai = rs.getBoolean("is_active");
                if (trangThai) {
                	status="Đang mở";
                }
                else {
                	status="Đang đóng";
                }
                String loaiBan = rs.getString("name_table");
                String giaTien= rs.getString("Cost");

				banStatusList.add(new String[] {maBan, status, loaiBan, giaTien});
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        
        return banStatusList;
    }
    

    public int getMaBan() {
        return maBan;
    }

    public void setMaBan(int maBan) {
        this.maBan = maBan;
    }

    public Timestamp getThoiGianMoBan() {
        return thoiGianMoBan;
    }

    public void setThoiGianMoBan(Timestamp thoiGianMoBan) {
        this.thoiGianMoBan = thoiGianMoBan;
    }

    public Timestamp getThoiGianKetThuc() {
        return thoiGianKetThuc;
    }

    public void setThoiGianKetThuc(Timestamp thoiGianKetThuc) {
        this.thoiGianKetThuc = thoiGianKetThuc;
    }

    public String getThucUong() {
        return thucUong;
    }

    public void setThucUong(String thucUong) {
        this.thucUong = thucUong;
    }

    public int getSoLuong() {
        return soLuong;
    }

    public void setSoLuong(int soLuong) {
        this.soLuong = soLuong;
    }

    public double getTongThanhToan() {
        return tongThanhToan;
    }

    public void setTongThanhToan(double tongThanhToan) {
        this.tongThanhToan = tongThanhToan;
    }
}
