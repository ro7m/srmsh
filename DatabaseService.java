package org.voice.service;

import com.sun.jdi.connect.spi.Connection;

public class DatabaseService {
//    private static final String DB_URL = "jdbc:h2:file:./database";
//    private Connection connection;
//
//    public DatabaseService() {
//        try {
//            connection = DriverManager.getConnection(DB_URL);
//            createTemplatesTable();
//        } catch (SQLException e) {
//            e.printStackTrace();
//        }
//    }
//
//    private void createTemplatesTable() throws SQLException {
//        String sql = "CREATE TABLE IF NOT EXISTS templates (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR, content TEXT)";
//        try (Statement statement = connection.createStatement()) {
//            statement.executeUpdate(sql);
//        }
//    }
//
//    public List<Template> getTemplates() {
//        List<Template> templates = new ArrayList<>();
//        try (Statement statement = connection.createStatement();
//             ResultSet resultSet = statement.executeQuery("SELECT * FROM templates")) {
//            while (resultSet.next()) {
//                int id = resultSet.getInt("id");
//                String name = resultSet.getString("name");
//                String content = resultSet.getString("content");
//                templates.add(new Template(id, name, content));
//            }
//        } catch (SQLException e) {
//            e.printStackTrace();
//        }
//        return templates;
//    }
//
//    public Template getTemplateByName(String name) {
//        try (PreparedStatement statement = connection.prepareStatement("SELECT * FROM templates WHERE name = ?")) {
//            statement.setString(1, name);
//            try (ResultSet resultSet = statement.executeQuery()) {
//                if (resultSet.next()) {
//                    int id = resultSet.getInt("id");
//                    String content = resultSet.getString("content");
//                    return new Template(id, name, content);
//                }
//            }
//        } catch (SQLException e) {
//            e.printStackTrace();
//        }
//        return null;
//    }
//
//    public void saveTemplate(String name, String content) {
//        try (PreparedStatement statement = connection.prepareStatement("INSERT INTO templates (name, content) VALUES (?, ?)")) {
//            statement.setString(1, name);
//            statement.setString(2, content);
//            statement.executeUpdate();
//        } catch (SQLException e) {
//            e.printStackTrace();
//        }
//    }
}