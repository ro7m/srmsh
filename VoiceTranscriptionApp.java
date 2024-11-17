package org.voice;

import org.pushingpixels.substance.api.skin.*;
import org.voice.service.DatabaseService;
import org.voice.service.PdfGeneratorService;
import org.voice.service.WhisperService;
import org.voice.ui.AudioRecorderPanel;
import org.voice.ui.TemplateManagerPanel;

import javax.swing.*;
import java.awt.*;

import static javax.swing.SwingUtilities.invokeLater;
import static javax.swing.UIManager.setLookAndFeel;

public class VoiceTranscriptionApp extends JFrame {
    public static DatabaseService databaseService;
    public static WhisperService whisperService;
    public static PdfGeneratorService pdfGeneratorService;

    public VoiceTranscriptionApp() {
        databaseService = new DatabaseService();
        whisperService = new WhisperService();
        pdfGeneratorService = new PdfGeneratorService();
        setTitle("HearMe");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(800, 600);
        setLocationRelativeTo(null);

        JTabbedPane tabbedPane = new JTabbedPane();
        tabbedPane.addTab("Audio Uploader", new AudioRecorderPanel(whisperService));
        tabbedPane.addTab("Template Manager", new TemplateManagerPanel(databaseService));
        tabbedPane.setFont(tabbedPane.getFont().deriveFont(Font.BOLD, 14f));
        tabbedPane.setBackground(new Color(42, 150, 0));
        tabbedPane.setForeground(Color.BLACK);
        add(tabbedPane,BorderLayout.CENTER);
        SwingUtilities.updateComponentTreeUI(this);
    }

    public static void main(String[] args) {
        invokeLater(() -> {
            try {
                setLookAndFeel(new SubstanceBusinessBlackSteelLookAndFeel());
                new VoiceTranscriptionApp().setVisible(true);
            } catch (UnsupportedLookAndFeelException e) {
                e.printStackTrace();
            }
        });

    }
}
