package org.voice.ui;

import org.voice.service.PdfGeneratorService;
import org.voice.service.WhisperService;

import javax.sound.sampled.UnsupportedAudioFileException;
import javax.swing.*;
import javax.swing.filechooser.FileNameExtensionFilter;
import java.awt.*;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;


public class AudioRecorderPanel extends JPanel {
    private WhisperService whisperService;
    private JButton fileChooserButton;
    private JFileChooser fileChooser;
    private JTextArea transcriptArea;
    private JButton summarizeButton;
    private JButton downloadTextButton;
    private JButton downloadPdfButton;
    private PdfGeneratorService pdfGeneratorService;

    public AudioRecorderPanel(WhisperService whisperService) {
        this.whisperService = whisperService;
        initComponents();
    }

    private void initComponents() {

        pdfGeneratorService = new PdfGeneratorService();
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 20, 10));

        setLayout(new BorderLayout());
        setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));
        fileChooserButton = new JButton("Upload");
        fileChooserButton.setFont(fileChooserButton.getFont().deriveFont(Font.BOLD, 14f));
        fileChooserButton.setBackground(new Color(42, 150, 0));
        fileChooserButton.setForeground(Color.BLACK);
        fileChooserButton.setBorderPainted(false);
        fileChooserButton.setFocusPainted(false);
        fileChooserButton.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
        fileChooserButton.setBounds(100, 50, 200, 30);
        fileChooserButton.addActionListener(e -> {
            fileChooser = new JFileChooser(".");
            fileChooser.setDialogTitle("choose the audio file");
            fileChooser.setFileSelectionMode(JFileChooser.FILES_ONLY);
            fileChooser.setFileFilter(new FileNameExtensionFilter("Audio files (.wav,.mp3) ", "wav", "mp3"));

            int result = fileChooser.showOpenDialog(null);

            if (result == JFileChooser.APPROVE_OPTION) {
                File selectedFile = fileChooser.getSelectedFile();
                System.out.println("selected file " + selectedFile);
                startTranscribing(selectedFile);
            }
        });

        transcriptArea = new JTextArea(5, 40);
        transcriptArea.setEditable(true);
        transcriptArea.setBorder(BorderFactory.createCompoundBorder(BorderFactory.createLineBorder(Color.GRAY, 1), BorderFactory.createEmptyBorder(5, 5, 5, 5)));
        transcriptArea.setLineWrap(true);
        transcriptArea.setWrapStyleWord(true);
        JScrollPane scrollPane = new JScrollPane(transcriptArea);

        buttonPanel.add(fileChooserButton, BorderLayout.CENTER);
        add(buttonPanel, BorderLayout.NORTH);
        add(scrollPane, BorderLayout.CENTER);


        summarizeButton = new JButton("Summarize");
        summarizeButton.addActionListener(e -> generateSummary());
        summarizeButton.setFont(summarizeButton.getFont().deriveFont(Font.BOLD, 14f));
        summarizeButton.setBackground(new Color(42, 150, 0));
        summarizeButton.setForeground(Color.BLACK);
        summarizeButton.setBorderPainted(false);
        summarizeButton.setFocusPainted(false);
        summarizeButton.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));

        downloadTextButton = new JButton("Download Text");
        downloadTextButton.addActionListener(e -> downloadText());
        downloadTextButton.setFont(downloadTextButton.getFont().deriveFont(Font.BOLD, 14f));
        downloadTextButton.setBackground(new Color(42, 150, 0));
        downloadTextButton.setForeground(Color.BLACK);
        downloadTextButton.setBorderPainted(false);
        downloadTextButton.setFocusPainted(false);
        downloadTextButton.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));

        downloadPdfButton = new JButton("Download PDF");
        downloadPdfButton.addActionListener(e -> downloadPdf());
        downloadPdfButton.setFont(downloadPdfButton.getFont().deriveFont(Font.BOLD, 14f));
        downloadPdfButton.setBackground(new Color(42, 150, 0));
        downloadPdfButton.setForeground(Color.BLACK);
        downloadPdfButton.setBorderPainted(false);
        downloadPdfButton.setFocusPainted(false);
        downloadPdfButton.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));

        JPanel summaryButtonPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 20, 10));
        buttonPanel.add(summarizeButton);
        buttonPanel.add(downloadTextButton);
        buttonPanel.add(downloadPdfButton);
        add(summaryButtonPanel, BorderLayout.SOUTH);

    }

    private void startTranscribing(File selectedFile) {
        String transcript = null;
        try {
            transcript = whisperService.transcribe(whisperService.processAudioFile(selectedFile));
        } catch (UnsupportedAudioFileException | IOException e) {
            throw new RuntimeException(e);
        }
        transcriptArea.setText(transcript);
    }

    private byte[] captureAudio() {
        return new byte[0];
    }

    private void generateSummary() {
        String summary = "Summary of the text...";
        JOptionPane.showMessageDialog(this, summary, "Transcript Summary", JOptionPane.INFORMATION_MESSAGE);
    }

    private void downloadText() {
        saveToFile(transcriptArea.getText(), "transcript.txt");
    }

    private void downloadPdf() {
        byte[] pdfData = pdfGeneratorService.generatePdf(transcriptArea.getText());
        saveToFile(pdfData, "transcript.pdf");
    }

    private void saveToFile(Object data, String filename) {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setDialogTitle("Save File");
        fileChooser.setSelectedFile(new File(filename));

        int userSelection = fileChooser.showSaveDialog(this);
        if (userSelection == JFileChooser.APPROVE_OPTION) {
            File fileToSave = fileChooser.getSelectedFile();
            try {
                if (data instanceof String) {
                    writeTextToFile((String) data, fileToSave);
                } else if (data instanceof byte[]) {
                    writeBytesToFile((byte[]) data, fileToSave);
                }
            } catch (IOException e) {
                JOptionPane.showMessageDialog(this, "Error saving file: " + e.getMessage(), "Error", JOptionPane.ERROR_MESSAGE);
            }
        }
    }

    private void writeTextToFile(String text, File file) throws IOException {
        try (FileOutputStream fos = new FileOutputStream(file)) {
            fos.write(text.getBytes());
        }
    }

    private void writeBytesToFile(byte[] data, File file) throws IOException {
        try (FileOutputStream fos = new FileOutputStream(file)) {
            fos.write(data);
        }
    }
}
