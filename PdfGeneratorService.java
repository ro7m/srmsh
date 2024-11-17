package org.voice.service;

import com.itextpdf.text.Document;
import com.itextpdf.text.DocumentException;
import com.itextpdf.text.Paragraph;
import com.itextpdf.text.pdf.PdfWriter;

import java.io.ByteArrayOutputStream;
import java.io.IOException;

public class PdfGeneratorService {
    public byte[] generatePdf(String text) {
        Document document = new Document();
        try {
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            PdfWriter.getInstance(document, outputStream);
            document.open();
            document.add(new Paragraph(text));
            document.close();
            return outputStream.toByteArray();
        } catch (DocumentException e) {
            e.printStackTrace();
        }
        return new byte[0];
    }
}