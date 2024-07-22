package com.elavirint.pipoprint.printer;

import java.lang.System;

public class PrinterCommand {
	/* 1.打印命令 */

	/**
	 * @brief 打印行缓冲器里的内容并向前走纸一行。当行缓冲器为空时只向前走纸一行。
	 *
	 * @return 
	 */
	static public byte[] cmdLF() {
		return new byte[] { (byte) 0x0A };
	}

	/**
	 * @brief 打印位置跳到下一个制表位,制表位为 8 个字符的起始位置
	 * 
	 * @return
	 */
	static public byte[] cmdHT() {
		return new byte[] { (byte) 0x09 };
	}

	/**
	 * @brief 打印缓冲区里的数据,如果有黑标功能,打印后进纸到下一个黑标位置(部分控制板支持)
	 * 
	 * @return
	 */
	static public byte[] cmdFF() {
		return new byte[] { (byte) 0x0C };
	}

	/**
	 * @brief 打印缓冲区里的数据,如果有黑标功能,打印后进纸到下一个黑标位置(部分控制板支持)
	 * 
	 * @return
	 */
	static public byte[] cmdESCFF() {
		return new byte[] { (byte) 0x1B, (byte) 0x0C };
	}

	/**
	 * 
	 * @brief 打印行缓冲区里的内容,并向前走纸 n 点行。 该命令只对本行有效,不改变 ESC 2,ESC 3 命令设置的行间距值。
	 * 
	 * @param n 0-255
	 *
	 * @return
	 */
	static public byte[] cmdESCjn(int n) {
		return new byte[] { (byte) 0x1B, (byte) 0x4A, (byte) n };
	}

	/**
	 * @brief 打印行缓冲区里的内容,并向前走纸 n 行。 行高为 ESC 2,ESC 3 设定的值
	 *
	 * @param n 0-255
	 *
	 * @return 
	 */
	static public byte[] cmdESCdn(int n) {
		return new byte[] { (byte) 0x1B, (byte) 0x64, (byte) n };
	}

	/**
	 * @brief ESC=n 1:打印机处于连线模式,接受打印数据并打印
	 *              0:打印机处于离线模式,不接受打印数据
	 *
	 * @param n 0,1 最低位有效
	 *
	 * @return 
	 */
	static public byte[] cmdESCequalN(int n) {
		return new byte[] { (byte) 0x1B, (byte) 0x3D, (byte) n };
	}

	/* 2.格式设置命令 */

	/**
	 * @brief 设置行间距为 4 毫米,32 点(1/6 英寸)
	 * 
	 * @return
	 */
	static public byte[] cmdESC2() {
		return new byte[] { (byte) 0x1B, (byte) 0x32 };
	}

	/**
	 * @brief 设置行间距为 n 点行。 默认值行间距是 32 点。
	 *
	 * @param n 0-255
	 *
	 * @return 
	 */
	static public byte[] cmdESC3n(int n) {
		return new byte[] { (byte) 0x1B, (byte) 0x33, (byte) n };
	}

	/**
	 * @brief 设置打印行的对齐方式,缺省:左对齐
	 *        0 ≤ n ≤ 2 或 48 ≤ n ≤ 50
	 *        左对齐: n=0,48
	 *        居中对齐: n=1,49
	 *        右对齐:n=2,50
	 *
	 * @param n 0 ≤ n ≤ 2 或 48 ≤ n ≤ 50
	 *
	 * @return 
	 */
	static public byte[] cmdESCan(int n) {
		return new byte[] { (byte) 0x1B, (byte) 0x61, (byte) n };
	}

	/**
	 * @brief 设置绝对打印位置
	 *        缺省为 0, n为双字节整数 横向或纵向 nL+nH*256,单位 0.125mm
	 * 
	 * @param nL low byte of n
	 * @param nH high byte of n
	 * @return
	 */
	static public byte[] cmdESCnLnH(int nL, int nH) {
		return new byte[] { (byte) 0x1B, (byte) 0x24, (byte) nL, (byte) nH };
	}

	/* 3.字符设置命令 */

	/**
	 * @brief ESC!n 用于设置打印字符的方式。默认值是 0
	 *
	 * @param n 位 0:(0-12x24,1-9x17)
	 *          1,2,6:保留
	 *          位 3:1:字体加粗
	 *          位 4:1:双倍高度
	 *          位 5:1:双倍宽度
	 * @return 
	 */
	static public byte[] cmdESCexclamationN(int n) {
		return new byte[] { (byte) 0x1B, (byte) 0x21, (byte) n };
	}

	/**
	 * @brief GS!n n 的低 4 位表示高度是否放大,等于 0 表示不放大
	 *             n 的高 4 位表示宽度是否放大,等于 0 表示不放大
	 * 
	 * @param n
	 * @return
	 */
	static public byte[] cmdGSexclamationN(int n) {
		return new byte[] { (byte) 0x1D, (byte) 0x21, (byte) n };
	}

	/**
	 * @brief 等于 0 时取消字体加粗 非 0 时设置字体加粗
	 * 
	 * @param n 最低位有效
	 *
	 * @return
	 */
	static public byte[] cmdESCEn(int n) {
		return new byte[] { (byte) 0x1B, (byte) 0x45, (byte) n };
	}

	/**
	 * @brief 默认值:0
	 * 
	 * @param n :表示两个字符之间的间距
	 *
	 * @return
	 */
	static public byte[] cmdESCSPn(int n) {
		return new byte[] { (byte) 0x1B, (byte) 0x20, (byte) n };
	}

	/**
	 * @brief 该命令之后所有字符均以正常宽度的 2 倍打印; 该命令可以用LF或者DC4命令删除。
	 * 
	 * @return
	 */
	static public byte[] cmdESCS0() {
		return new byte[] { (byte) 0x1B, (byte) 0x0E };
	}

	/**
	 * @brief 命令执行后,字符恢复正常宽度打印
	 * 
	 * @return
	 */
	static public byte[] cmdESCDC4() {
		return new byte[] { (byte) 0x1B, (byte) 0x14 };
	}

	/**
	 * @brief ESC\{n 设置/取消字符上下倒置 默认:0
	 * 
	 * @param n 1:设置字符上下倒置 0:取消字符上下倒置
	 *
	 * @return
	 */
	static public byte[] cmdESCbracketN(int n) {
		return new byte[] { (byte) 0x1B, (byte) 0x7B, (byte) n };
	}

	/**
	 * @brief 设置/取消字符反白打印 默认:0
	 * 
	 * @param n n=1:设置字符反白打印 n=0:取消字符反白打印
	 *
	 * @return
	 */
	static public byte[] cmdGSBn(int n) {
		return new byte[] { (byte) 0x1D, (byte) 0x42, (byte) n };
	}

	/**
	 * @brief ESC-n 设置下划线的高度 默认:0
	 * 
	 * @param n n=0-2,下划线的高度
	 *
	 * @return
	 */
	static public byte[] cmdESCminusN(int n) {
		return new byte[] { (byte) 0x1B, (byte) 0x2D, (byte) n };
	}

	/**
	 * @brief ESC%n 允许/禁止用户自定义字符
	 * @param n n=1:选择用户自定义字符集; n=0:选择内部字符集(默认)
	 * @return
	 */
	static public byte[] cmdESCpercentN(int n) {
		return new byte[] { (byte) 0x1B, (byte) 0x25, (byte) n };
	}

	/**
	 * @brief ESC&snmw 用于设置用户自定义字符,最多可设置 32 个用户自定义字符。
	 *                 s: 表示纵向字节数,必须等于 3(高度 24 点)
	 *                 w: 字符宽度 0~12(s=3)
	 *                 n: 表示自定义字符的起始 ASCII
	 *                 m: 表示自定义字符的终止 ASCII
	 *                 dx:字符点阵数据,x=s*w
	 *
	 * @param s 3,32   32 ≤ n ≤ m < 127
	 * @param n
	 * @param w
	 * @param m
	 * @param byte[] d
	 * @return
	 */
	static public byte[] cmdESC_SNMW(int s, int n, int w, int m, byte[] d) {
		int i;
		byte[] cmd = new byte[d.length+7];
		cmd [0] =  (byte) 0x1B;
		cmd [1] =  (byte) 0x26;
		cmd [2] =  (byte) s;
		cmd [3] =  (byte) n;
		cmd [5] =  (byte) w;
		cmd [6] =  (byte) m;
		System.arraycopy(d, 0, cmd, 7, d.length);
		return cmd;
	}

	/**
	 * @brief ESC?n 命令用于取消用户自定义的字符,字符取消后,使用系统的字符。
	 * 
	 * @param n
	 * @return
	 */
	static public byte[] cmdESCquestionN(int n) {
		return new byte[] { (byte) 0x1B, (byte) 0x25, (byte) n };
	}

	/**
	 * @brief 选择国际字符集。中文版本不支持该命令。
	 * 
	 * @param n 国际字符集设置如下:
	 *          0:USA
	 *          1:France
	 *          2:Germany
	 *          3:U.K.
	 *          4:Denmark 1
	 *          5:Sweden
	 *          6:Italy
	 *          7:Spain1
	 *          8:Japan
	 *          9:Norway
	 *          10:Denmark II
	 *          11:Spain II
	 *          12:Latin America
	 *          13:Korea
	 *          14:Slovenia/Croatia
	 *          15:China
	 * @return
	 */
	static public byte[] cmdESCRn(int n) {
		return new byte[] { (byte) 0x1B, (byte) 0x52, (byte) n };
	}

	/**
	 * @brief 选择字符代码页,字符代码页用于选择 0x80~0xfe 的打印字符。中文版本不支持该命令
	 * 
	 * @param n 字符代码页参数 0:437 1:850
	 *
	 * @return
	 */
	static public byte[] cmdESCtn(int n) {
		return new byte[] { (byte) 0x1B, (byte) 0x74, (byte) n };
	}

	/* 4.图形打印命令 */

	/**
	 * @brief ESC * m n1 n2 d1 d2...dk 设定打印点图
	 *        k = n1+256*n2 (m=0,1)
	 *        k = (n1+256*n2)*3 (m=32,33)
	 *        m 用于选择点图方式。
	 *          0: 高度 8 点,水平方向需放大一倍
	 *          1: 高度 8 点,水平方向不需放大
	 *          32:高度 24 点,水平方向需放大一倍
	 *          33:高度 24 点,水平方向不需放大
	 *        点图顺序请参照自定义字符命令
	 * @param m 0,1,32,33
	 * @param n1 0-255
	 * @param n2 0-3
	 * @param byte[] d data
	 *
	 * @return 
	 */
	static public byte[] cmdESC_mn1n2d(int m, int n1, int n2, byte[] d) {
		int i;
		byte[] cmd = new byte[d.length+5];
		cmd [0] =  (byte) 0x1B;
		cmd [1] =  (byte) 0x2A;
		cmd [2] =  (byte) m;
		cmd [3] =  (byte) n1;
		cmd [4] =  (byte) n2;
		System.arraycopy(d, 0, cmd, 5, d.length);
		return cmd;
	}

	/**
	 * @brief GS / n 打印点图
	 *               打印点图由 GS * 命令定义
	 *
	 *               命令用于打印下装位图。n=0~3、48~51。
	 *               n 点图方式     纵向点密度 横向点密度
	 *               0 正常方式     203DPI     203DPI
	 *               1 双倍宽度方式 203DPI     101DPI
	 *               2 双倍高度方式 101DPI     203DPI
	 *               3 倍高倍宽方式 101DPI     101DPI
	 *
	 * @param n 0-3,38-51
	 *
	 * @return 
	 */
	static public byte[] cmdGSslashn(int n) {
		return new byte[] { (byte) 0x1D, (byte) 0x2F, (byte) n };
	}

	/**
	 * @brief GS * n1 n2 d1...dk 下载位图
	 *
	 *                           该命令将清除用户自定义字符
	 *                           该命令用于定义下装点图
	 *                           n1=1~48(宽度),n2=1~255(高度),n1*n2<2300,k=n1*n2*8
	 *                           下装位图一直有效,直到重新启动或重新定义
	 *                           位图顺序请参照自定义字符
	 *
	 * @param n1 0-255
	 * @param n2 0-3
	 * @param byte[] d data
	 * @return 
	 */

	static public byte[] cmdGS_n1n2d(int n1, int n2, byte[] d) {
		int i;
		byte[] cmd = new byte[d.length+4];
		cmd [0] =  (byte) 0x1D;
		cmd [1] =  (byte) 0x2A;
		cmd [2] =  (byte) n1;
		cmd [3] =  (byte) n2;
		System.arraycopy(d, 0, cmd, 4, d.length);
		return cmd;
	}

	/**
	 * @brief GS v 0 p wL wH hL hH 下载位图
	 *
	 *        p: 打印位图格式。
	 *          位 0:不等于 0 时,位图需要双倍宽度
	 *               等于 0 时,位图不需要双倍宽度
	 *          位 1:不等于 0 时,位图需要双倍高度
	 *               等于 0 时,位图不需要双倍高度
	 *        W=wL+wH*256 表示水平宽度字节数
	 *        H=wL+wH*256 表示垂直高度点数
	 *        位图使用 MSB 格式,最高位在打印位置的左边,先送的数据在打印位置的左边。
	 *
	 * @param p
	 * @param wL	wL=48
	 * @param wH	wH=0
	 * @param hL
	 * @param hH
	 * @param byte[] d
	 *
	 * @return 
	 */
	static public byte[] cmdGSv0pwLwHhLhHd(int p, int wL, int wH, int hL, int hH, byte[] d) {
		int i;
		byte[] cmd = new byte[d.length+8];
		cmd [0] =  (byte) 0x1D;
		cmd [1] =  (byte) 0x76;
		cmd [2] =  (byte) 0x30;
		cmd [3] =  (byte) p;
		cmd [4] =  (byte) wL;
		cmd [5] =  (byte) wH;
		cmd [6] =  (byte) hL;
		cmd [7] =  (byte) hH;
		System.arraycopy(d, 0, cmd, 8, d.length);
		return cmd;
	}

	/**
	 * @brief DC2 * r n [d1...dn] 位图打印
	 *
	 *        该命令用于打印指定高度宽度的位图。
	 *        r :打印位图高度
	 *        n : 打印位图宽度
	 *        位图格式如下:
	 *        d1 d2 ... dn  0
	 *        ...  
	 *        d1 d2 ... dn  r
	 *
	 * @param r
	 * @param n
	 * @param byte[] d
	 *
	 * @return 
	 */
	static public byte[] cmdDC2_rnd(int r, int n, byte[] d) {
		int i;
		byte[] cmd = new byte[d.length+4];
		cmd [0] =  (byte) 0x12;
		cmd [1] =  (byte) 0x2A;
		cmd [2] =  (byte) r;
		cmd [3] =  (byte) n;
		System.arraycopy(d, 0, cmd, 4, d.length);
		return cmd;
	}

	/**
	 * @brief DC2 V nL nH d1...dn 打印MSB位图
	 *
	 *        该命令用于打印 MSB 格式位图。位图宽度为 384 位。
	 *        打印高度: nL+nH*256
	 *        位图格式如下:
	 *        1th byte     2th byte     ... 48th byte
	 *        ...
	 *        (n+1)th byte (n+2)th byte ... (n+48)th byte
	 *
	 *        byte
	 *        | | | | | | | | |
	 *        MSB           LSB
	 * @param nL
	 * @param nH
	 * @param byte[] d
	 *
	 * @return 
	 */
	static public byte[] cmdDC2VnLnHd(int nL, int nH, byte[] d) {
		int i;
		byte[] cmd = new byte[d.length+4];
		cmd [0] =  (byte) 0x12;
		cmd [1] =  (byte) 0x56;
		cmd [2] =  (byte) nL;
		cmd [3] =  (byte) nH;
		System.arraycopy(d, 0, cmd, 4, d.length);
		return cmd;
	}

	/**
	 * @brief DC2 V nL nH d1...dn 打印LSB位图
	 *
	 *        该命令用于打印 LSB 格式位图。位图宽度为 384 位。
	 *        打印高度: nL+nH*256
	 *        位图格式如下:
	 *        1th byte     2th byte     ... 48th byte
	 *        ...
	 *        (n+1)th byte (n+2)th byte ... (n+48)th byte
	 *
	 *        byte
	 *        | | | | | | | | |
	 *        LSB           MSB
	 *
	 * @param nL
	 * @param nH
	 * @param byte[] d
	 *
	 * @return 
	 */
	static public byte[] cmdDC2vnLnHd(int nL, int nH, byte[] d) {
		int i;
		byte[] cmd = new byte[d.length+4];
		cmd [0] =  (byte) 0x12;
		cmd [1] =  (byte) 0x76;
		cmd [2] =  (byte) nL;
		cmd [3] =  (byte) nH;
		System.arraycopy(d, 0, cmd, 4, d.length);
		return cmd;

	}

	/* 5.按键控制命令 */

	/**
	 * @brief 允许/禁止按键开关命令,暂时不支持该命令。
	 * 
	 * @param n n=1,禁止按键 n=0,允许按键(默认)
	 *
	 * @return
	 */
	static public byte[] cmdESCc5n(int n) {
		return new byte[] { (byte) 0x1B, (byte) 0x63, (byte) 0x35, (byte) n };
	}

	/* 6.初始化命令 */

	/**
	 * @brief ESC @ 初始化打印机
	 *              清除打印缓冲区
	 *              恢复默认值
	 *              选择字符打印方式
	 *              删除用户自定义字符
	 * 
	 * @return
	 */
	static public byte[] cmdESCat() {
		return new byte[] { (byte) 0x1B, (byte) 0x40 };
	}

	/* 7.状态传输命令 */

	/**
	 * 向主机传送控制板状态,串口打印机有效
	 * 
	 * @param n 1.纸张状态 打印机返回12缺纸，返回0有纸
	 *          2.钱箱状态 返回1钱箱关，返回0钱箱开
	 * @return
	 */
	static public byte[] cmdGSrn(int n) {
		return new byte[] { (byte) 0x1D, (byte) 0x72, (byte) n };
	}

	/**
	 * @brief 当有效时,打印机发现状态改变,则自动发送状态到主机。详细参照ESC/POS指令集。
	 * 
	 * @param n
	 * @return
	 */
	static public byte[] cmdGSan(int n) {
		return new byte[] { (byte) 0x1D, (byte) 0x61, (byte) n };
	}

	/**
	 * @brief 向主机传送周边设备状态,仅对串口型打印机有效。该命令不支持。详细参照ESC/POS指令集。
	 * 
	 * @param n
	 * @return
	 */
	static public byte[] cmdESCun(int n) {
		return new byte[] { (byte) 0x1B, (byte) 0x75, (byte) n };
	}

	/* 8.条码打印命令 */

	/**
	 * @brief 设定条码对应的字符(HRI)打印方式 0 ≤ n ≤ 255
	 *
	 * @param n 0: 不打印 HRI
	 *          1: HRI 在条码下方
	 *          2: HRI 在条码上方
	 *          3: HRI 在条码上方和下方
	 *
	 * @return 
	 */
	static public byte[] cmdGSHn(int n) {
		return new byte[] { (byte) 0x1D, (byte) 0x48, (byte) n };
	}

	/**
	 * @brief 设置条形码高度,默认50
	 *
	 * @param n 条码垂直方向的点数 1 ≤ n ≤ 255
	 *
	 * @return 
	 */
	static public byte[] cmdGShn(int n) {
		return new byte[] { (byte) 0x1D, (byte) 0x68, (byte) n };
	}

	/**
	 * @brief 设置条形码打印的左边距
	 *
	 * @param n	0-255
	 *
	 * @return 
	 */
	static public byte[] cmdGSxn(int n) {
		return new byte[] { (byte) 0x1D, (byte) 0x78, (byte) n };
	}

	/**
	 * @brief 设置要打印的条码基本线条宽度,默认2
	 *
	 * @param n n=2,3
	 *
	 * @return 
	 */
	static public byte[] cmdGSwn(int n) {
		return new byte[] { (byte) 0x1D, (byte) 0x77, (byte) n };
	}

	/**
	 * @brief 打印条形码
	 *
	 * @param m	条形码格式
	 * @param n	条形码长度
	 * @param byte[] d 条形码数据
	 *
	 * @return 
	 */

	static public byte[] cmdGSkmnd(int m, int n, byte[] d) {
		int i;
		byte[] cmd = new byte[d.length+4];
		cmd [0] =  (byte) 0x1D;
		cmd [1] =  (byte) 0x6B;
		cmd [2] =  (byte) m;
		cmd [3] =  (byte) n;
		//for(i=0; i<d.length; i++) {
		//	cmd[i+4] = (byte) d[i]; 
		//}
		System.arraycopy(d, 0, cmd, 4, d.length);
		return cmd;
	}

	/* 9.控制板参数命令 */

	/**
	 * @brief 设置打印的最多加热点数、加热时间、间隔时间
	 *        n1 = 0-255 最多加热点数,单位(8dots),默认值 7(64 点)
	 *        n2 = 0-255 加热的时间,单位(10us),默认值 80
	 *        n3 = 0-255 加热间隔时间,单位(10us),默认值 2
	 *        加热点数多,则控制板的最大耗电电流大,打印速度快。最大加热点数为 8*(n1+1)
	 *        加热时间越长,则打印黑度高,打印速度越慢。加热时间过短,则可能
	 *        出现打印空白。
	 *        间隔时间越长,打印越清晰,打印速度变慢
	 *        说明:"加热时间","加热间隔"控制板会根据输入电压而自动调整
	 *
	 * @param n1
	 * @param n2
	 * @param n3
	 *
	 * @return 
	 */
	static public byte[] cmdESC7n1n2n3(int n1, int n2, int n3) {
		return new byte[] { (byte) 0x1B, (byte) 0x37, (byte) n1, (byte) n2, (byte) n3 };
	}

	/**
	 * @brief 设置空闲多少时间后,控制板进入睡眠时间
	 *        n1+n2*256 睡眠等待时间,单位(10 毫秒),默认值 0
	 *        值 0 等于表示不睡眠,不等于 0 时最小值为 200 毫秒。
	 *        进入睡眠后,主机必须先发送一字节数据(0xff)唤醒控制板,等待 50
	 *        毫秒后再开始发送打印命令或数据
	 *        说明:本命令主要用于电池供电系统,需要低功耗的应用
	 *
	 * @param n1
	 * @param n2
	 *
	 * @return 
	 */
	static public byte[] cmdESC8n1n2(int n1, int n2) {
		return new byte[] { (byte) 0x1B, (byte) 0x38, (byte) n1, (byte) n2 };
	}

	/**
	 * @brief DC2 # n 设置打印浓度
	 *              n 的最低 5 位用于设置打印浓度
	 *                  值从 0-31 对应 50%+5%*n(4-0)的打印浓度
	 *              n 的最高 3 位表示打印延迟
	 *                  打印延迟为 n(7-5)*250us
	 *
	 * @param n
	 *
	 * @return 
	 */
	static public byte[] cmdDC2_n(int n) {
		return new byte[] { (byte) 0x12, (byte) 0x23, (byte) n };
	}

	/**
	 * @brief 打印测试页
	 *
	 * @return 
	 */
	static public byte[] cmdDC2T() {
		return new byte[] { (byte) 0x12, (byte) 0x54 };
	}

	/**
	 * @brief 选择切纸模式切纸
	 *
	 * @param m 0,全切,1半切
	 *
	 * @return 
	 */
	static public byte[] cmdGSvm(int m) {
		return new byte[] { (byte) 0x1D, (byte) 0x56 , (byte) m};
	}
}
