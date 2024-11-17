package org.voice.ui;

import org.voice.service.DatabaseService;

import javax.swing.*;
import java.awt.*;

public class TemplateManagerPanel extends JPanel {
    private DatabaseService databaseService;
    private JComboBox<String> templateDropdown;
    private JTextArea templateTextArea;
    private JButton saveTemplateButton;

    public TemplateManagerPanel(DatabaseService databaseService) {
        this.databaseService = databaseService;
        initComponents();
    }

    private void initComponents() {
        setLayout(new BorderLayout());
        setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        templateDropdown = new JComboBox<>();
        templateDropdown.addActionListener(e -> loadSelectedTemplate());

        templateTextArea = new JTextArea(10, 40);
        templateTextArea.setLineWrap(true);
        templateTextArea.setWrapStyleWord(true);
        JScrollPane scrollPane = new JScrollPane(templateTextArea);

        saveTemplateButton = new JButton("Save Template");
        saveTemplateButton.addActionListener(e -> saveTemplate());
        saveTemplateButton.setFont(saveTemplateButton.getFont().deriveFont(Font.BOLD, 14f));
        saveTemplateButton.setBackground(new Color(0, 33, 150));
        saveTemplateButton.setForeground(Color.BLACK);
        saveTemplateButton.setBorderPainted(false);
        saveTemplateButton.setFocusPainted(false);
        saveTemplateButton.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));

        JPanel topPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 10));
        topPanel.add(new JLabel("Select Template:"));
        topPanel.add(templateDropdown);

        JPanel bottomPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT, 10, 10));
        bottomPanel.add(saveTemplateButton);

        add(topPanel, BorderLayout.NORTH);
        add(scrollPane, BorderLayout.CENTER);
        add(bottomPanel, BorderLayout.SOUTH);

        loadTemplates();
    }

    private void loadTemplates() {
//        List<Template> templates = databaseService.getTemplates();
//        for (Template template : templates) {
//            templateDropdown.addItem(template.getName());
//        }
    }

    private void loadSelectedTemplate() {
        String selectedName = (String) templateDropdown.getSelectedItem();
//        Template template = databaseService.getTemplateByName(selectedName);
//        templateTextArea.setText(template.getContent());
    }

    private void saveTemplate() {
        String name = JOptionPane.showInputDialog("Enter template name:");
        String content = templateTextArea.getText();
//        databaseService.saveTemplate(name, content);
        templateDropdown.addItem(name);
    }
}