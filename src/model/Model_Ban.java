package model;

import java.util.Date;

public class Model_Ban {
	private int maBan;
	private Date batDau;
	private Date ketThuc;
	public Model_Ban(int maBan, Date batDau, Date ketThuc, String luaChon) {
		super();
		this.maBan = maBan;
		this.batDau = batDau;
		this.ketThuc = ketThuc;
	}

	public int getMaBan() {
		return maBan;
	}
	public void setMaBan(int maBan) {
		this.maBan = maBan;
	}
	public Date getBatDau() {
		return batDau;
	}
	public void setBatDau(Date batDau) {
		this.batDau = batDau;
	}
	public Date getKetThuc() {
		return ketThuc;
	}
	public void setKetThuc(Date ketThuc) {
		this.ketThuc = ketThuc;
	}
	
	

}
