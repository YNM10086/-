package function;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.Statement;

public class One {
    // 全局固定数据库信息，只在这里改一次
    private static final String URL = "jdbc:mysql://localhost:3306/Cost_system?useSSL=false&serverTimezone=UTC";
    private static final String USER = "root";
    private static final String PWD = "274823137";
    // 获取数据库连接 方法
    public static Connection getConn() {
        Connection conn = null;
        try {
            conn = DriverManager.getConnection(URL, USER, PWD);
        } catch (Exception e) {
            // 统一全局报错
            System.out.println("数据库连接失败！");
            e.printStackTrace();
        }
        return conn;
    }

    // 获取 Statement 对象 适合简单查询、固定SQL
    public static Statement getStatement(Connection conn) {
        Statement stmt = null;
        try {
            stmt = conn.createStatement();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return stmt;
    }

    // 获取 PreparedStatement 对象 适合增删改、带参数
    public static PreparedStatement getPreparedStmt(Connection conn, String sql) {
        PreparedStatement pstmt = null;
        try {
            pstmt = conn.prepareStatement(sql);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return pstmt;
    }
}
