package System;

import function.Date_time;
import function.Menu;
import function.One;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;
import javax.imageio.ImageIO;

public class The_main {

    // 读取小数，输入quit返回null
    private static Double readDouble(Scanner in, String prompt) {
        while (true) {
            System.out.print(prompt);
            String s = in.nextLine();
            if ("quit".equalsIgnoreCase(s)) return null;
            try {
                return Double.parseDouble(s);
            } catch (NumberFormatException e) {
                System.out.println("格式错误，请输入数字！");
            }
        }
    }

    // ==================== 表名工具 ====================

    // 根据当前月份返回表名：1月→table_01
    private static String getTableName() {
        int m = Date_time.getMonth();
        return String.format("table_%02d", m);
    }

    // ==================== 功能一：存入消费 ====================

    private static void saveConsumption() {
        Scanner in = new Scanner(System.in);
        int day = Date_time.getDay();
        String table = getTableName();
        System.out.printf("当前表: %s | 日期(日): %02d\n", table, day);
        System.out.println("（输入quit可随时退出）");
        while (true) {
            System.out.print("请输入商品名称：");
            String goods = in.nextLine();
            if ("quit".equalsIgnoreCase(goods)) break;
            if (goods.trim().isEmpty()) {
                System.out.println("商品名不能为空！");
                continue;
            }

            Double price = readDouble(in, "请输入价格：");
            if (price == null) break;

            Connection conn = One.getConn();
            if (conn == null) continue;
            try {
                String sql = "INSERT INTO " + table + " (date, goods, price) VALUES (?, ?, ?)";
                PreparedStatement ps = One.getPreparedStmt(conn, sql);
                ps.setInt(1, day);
                ps.setString(2, goods);
                ps.setDouble(3, price);
                int rows = ps.executeUpdate();
                System.out.println(rows > 0 ? "存入成功！" : "存入失败！");
                ps.close();
                conn.close();
            } catch (Exception e) {
                System.out.println("存入异常！");
                e.printStackTrace();
            }
        }
    }

    // ==================== 功能二：查询消费 ====================

    // 进入功能二时先调用子菜单
    private static void queryConsumption() {
        Menu.runQuery(The_main::queryTotal, The_main::queryDaily);
    }

    // 子菜单1：查询总消费与日均消费
    private static void queryTotal() {
        String table = getTableName();
        Connection conn = One.getConn();
        if (conn == null) return;
        try {
            PreparedStatement ps = One.getPreparedStmt(conn,
                "SELECT SUM(price), COUNT(DISTINCT date), COUNT(*), " +
                "SUM(price) / COUNT(DISTINCT date) FROM " + table);
            ResultSet rs = ps.executeQuery();
            if (rs.next()) {
                double total = rs.getDouble(1);
                int days = rs.getInt(2);
                int count = rs.getInt(3);
                double dailyAvg = rs.getDouble(4);
                System.out.printf("总消费: %.2f | 日均消费: %.2f | 天数: %d | 记录数: %d\n",
                    total, dailyAvg, days, count);
            } else {
                System.out.println("暂无消费记录。");
            }
            rs.close();
            ps.close();
            conn.close();
        } catch (Exception e) {
            System.out.println("查询异常！");
            e.printStackTrace();
        }
    }

    // 子菜单2：生成每日消费折线图
    private static void queryDaily() {
        String table = getTableName();
        Connection conn = One.getConn();
        if (conn == null) return;
        try {
            PreparedStatement ps = One.getPreparedStmt(conn,
                "SELECT date, SUM(price) FROM " + table + " GROUP BY date ORDER BY date");
            ResultSet rs = ps.executeQuery();
            List<Integer> days = new ArrayList<>();
            List<Double> totals = new ArrayList<>();
            while (rs.next()) {
                days.add(rs.getInt(1));
                totals.add(rs.getDouble(2));
            }
            rs.close();
            ps.close();
            conn.close();

            if (days.isEmpty()) {
                System.out.println("暂无消费记录。");
                return;
            }
            drawLineChart(days, totals, table);
            System.out.println("折线图已生成：The_Pic/" + table + "_chart.png");
        } catch (Exception e) {
            System.out.println("查询异常！");
            e.printStackTrace();
        }
    }

    // 用Java2D绘制折线图并保存PNG
    private static void drawLineChart(List<Integer> days, List<Double> totals, String table) {
        int w = 800, h = 500;
        int pad = 60;
        int chartW = w - 2 * pad;
        int chartH = h - 2 * pad;
        BufferedImage img = new BufferedImage(w, h, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = img.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g.setColor(Color.WHITE);
        g.fillRect(0, 0, w, h);

        // 数据范围
        double minTotal = totals.stream().min(Double::compare).orElse(0.0);
        double maxTotal = totals.stream().max(Double::compare).orElse(1.0);
        if (maxTotal == 0) maxTotal = 1;
        minTotal = Math.min(minTotal * 0.9, 0);
        maxTotal *= 1.1;
        int minDay = days.stream().min(Integer::compare).orElse(1);
        int maxDay = days.stream().max(Integer::compare).orElse(31);

        // 坐标轴
        g.setColor(Color.BLACK);
        g.setStroke(new BasicStroke(2));
        g.drawLine(pad, h - pad, w - pad, h - pad);
        g.drawLine(pad, pad, pad, h - pad);
        g.setFont(new Font("微软雅黑", Font.PLAIN, 11));

        // Y轴刻度
        int yTicks = 5;
        for (int i = 0; i <= yTicks; i++) {
            double val = minTotal + (maxTotal - minTotal) * i / yTicks;
            int y = h - pad - (int)(chartH * i / yTicks);
            g.setColor(Color.LIGHT_GRAY);
            g.drawLine(pad + 1, y, w - pad, y);
            g.setColor(Color.BLACK);
            g.drawString(String.format("%.0f", val), 2, y + 4);
        }

        // X轴刻度
        for (int d = minDay; d <= maxDay; d++) {
            int x = pad + (int)(chartW * (double)(d - minDay) / (maxDay - minDay + 0.01));
            g.setColor(Color.LIGHT_GRAY);
            g.drawLine(x, h - pad - 1, x, pad);
            g.setColor(Color.BLACK);
            g.drawString(String.valueOf(d), x - 4, h - pad + 16);
        }

        // 数据点坐标
        int n = days.size();
        int[] xs = new int[n], ys = new int[n];
        for (int i = 0; i < n; i++) {
            xs[i] = pad + (int)(chartW * (double)(days.get(i) - minDay) / (maxDay - minDay + 0.01));
            ys[i] = h - pad - (int)(chartH * (totals.get(i) - minTotal) / (maxTotal - minTotal));
        }

        // 折线
        g.setStroke(new BasicStroke(2.5f));
        g.setColor(new Color(220, 50, 50));
        for (int i = 0; i < n - 1; i++) {
            g.drawLine(xs[i], ys[i], xs[i + 1], ys[i + 1]);
        }

        // 数据点
        for (int i = 0; i < n; i++) {
            g.setColor(new Color(220, 50, 50));
            g.fillOval(xs[i] - 5, ys[i] - 5, 10, 10);
            g.setColor(Color.WHITE);
            g.fillOval(xs[i] - 2, ys[i] - 2, 4, 4);
            g.setColor(Color.BLACK);
            g.setFont(new Font("微软雅黑", Font.PLAIN, 10));
            g.drawString(String.format("%.1f", totals.get(i)), xs[i] - 12, ys[i] - 10);
        }

        // 标题
        g.setFont(new Font("微软雅黑", Font.BOLD, 16));
        g.drawString(table + " 每日消费折线图", w / 2 - 80, pad / 2);

        g.dispose();
        try {
            new File("The_Pic").mkdirs();
            ImageIO.write(img, "png", new File("The_Pic/" + table + "_chart.png"));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // ==================== 密码验证 ====================

    private static boolean checkPassword() {
        Scanner in = new Scanner(System.in);
        System.out.println("===== 消费记录系统 =====");
        for (int i = 0; i < 3; i++) {
            System.out.print("请输入密码：");
            String pwd = in.nextLine();
            if ("密码".equals(pwd)) return true;
            int left = 2 - i;
            if (left > 0) System.out.println("密码错误！剩余次数：" + left);
        }
        System.out.println("次数用尽，系统退出。");
        return false;
    }

    // ==================== 主入口 ====================

    public static void main(String[] args) {
        if (!checkPassword()) {
            System.out.println("密码错误，系统退出。");
            return;
        }
        System.out.println("密码正确，欢迎使用！");
        Menu.run(The_main::saveConsumption, The_main::queryConsumption);
    }
}
