import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.GridPane;
import javafx.stage.FileChooser;
import javafx.stage.PrinterJob;
import javafx.stage.Stage;

import java.io.File;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class PTApp extends Application {

    private TextField nameField, addressField;
    private ComboBox<String> procedureComboBox;
    private ImageView imageView;
    private Button captureButton, saveButton, printButton;
    private String imagePath = null;

    @Override
    public void start(Stage primaryStage) {
        GridPane grid = new GridPane();
        grid.setPadding(new Insets(10));
        grid.setVgap(8);
        grid.setHgap(10);

        Label nameLabel = new Label("Name:");
        nameField = new TextField();
        Label addressLabel = new Label("Address:");
        addressField = new TextField();

        Label procedureLabel = new Label("Procedure Template:");
        procedureComboBox = new ComboBox<>();
        loadProcedures();

        imageView = new ImageView();
        imageView.setFitWidth(200);
        imageView.setFitHeight(200);

        captureButton = new Button("Capture Image");
        captureButton.setOnAction(e -> captureImage());

        saveButton = new Button("Save Treatment Summary");
        saveButton.setOnAction(e -> saveTreatmentSummary(primaryStage));

        printButton = new Button("Print Treatment Summary");
        printButton.setOnAction(e -> printTreatmentSummary(primaryStage));

        grid.add(nameLabel, 0, 0);
        grid.add(nameField, 1, 0);
        grid.add(addressLabel, 0, 1);
        grid.add(addressField, 1, 1);
        grid.add(procedureLabel, 0, 2);
        grid.add(procedureComboBox, 1, 2);
        grid.add(imageView, 0, 3, 2, 1);
        grid.add(captureButton, 0, 4);
        grid.add(saveButton, 1, 4);
        grid.add(printButton, 2, 4);

        Scene scene = new Scene(grid, 400, 350);
        primaryStage.setTitle("Patient Treatment App");
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    private void loadProcedures() {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:path_to_your_database.db")) {
            PreparedStatement stmt = conn.prepareStatement("SELECT template FROM procedures");
            ResultSet rs = stmt.executeQuery();
            while (rs.next()) {
                procedureComboBox.getItems().add(rs.getString("template"));
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    private void captureImage() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.getExtensionFilters().addAll(
                new FileChooser.ExtensionFilter("Image Files", "*.png", "*.jpg", "*.jpeg")
        );
        File selectedFile = fileChooser.showOpenDialog(null);
        if (selectedFile != null) {
            imagePath = selectedFile.getAbsolutePath();
            imageView.setImage(new Image(selectedFile.toURI().toString()));
        }
    }

    private void saveTreatmentSummary(Stage stage) {
        String name = nameField.getText();
        String address = addressField.getText();
        String procedureTemplate = procedureComboBox.getValue();
        String imageBase64 = null; // Convert image to base64 if needed

        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:path_to_your_database.db")) {
            String sql = "INSERT INTO treatment_summaries (name, address, procedure_template, image_base64) VALUES (?, ?, ?, ?)";
            PreparedStatement pstmt = conn.prepareStatement(sql);
            pstmt.setString(1, name);
            pstmt.setString(2, address);
            pstmt.setString(3, procedureTemplate);
            pstmt.setString(4, imageBase64); // Save image as base64 if needed
            pstmt.executeUpdate();
        } catch (SQLException e) {
            e.printStackTrace();
        }

        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("Success");
        alert.setHeaderText(null);
        alert.setContentText("Treatment summary saved successfully!");
        alert.showAndWait();
    }

    private void printTreatmentSummary(Stage stage) {
        PrinterJob job = PrinterJob.createPrinterJob();
        if (job != null) {
            boolean doPrint = job.showPrintDialog(stage);
            if (doPrint) {
                // Assuming you want to print the entire scene
                job.printPage(getScene());
                job.endJob();
            }
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
}
