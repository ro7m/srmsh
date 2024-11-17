package org.voice.service;

import javax.sound.sampled.*;
import java.io.File;
import java.io.IOException;

public class AudioConverter {
    private static final int TARGET_SAMPLE_RATE = 16000;
    private static final int TARGET_SAMPLE_SIZE = 16;
    private static final int TARGET_CHANNELS = 1;

    public static void convertAudioFile(File inputFile, File outputFile) throws UnsupportedAudioFileException, IOException {

        // Read the input audio file
        AudioInputStream audioInputStream = AudioSystem.getAudioInputStream(inputFile);
        AudioFormat sourceFormat = audioInputStream.getFormat();

        // Check if conversion is needed
        if (needsConversion(sourceFormat)) {

            System.out.println("Converting audio file to match required specifications...");

            // Create the target audio format
            AudioFormat targetFormat = new AudioFormat(AudioFormat.Encoding.PCM_SIGNED, TARGET_SAMPLE_RATE, TARGET_SAMPLE_SIZE, TARGET_CHANNELS, TARGET_CHANNELS * (TARGET_SAMPLE_SIZE / 8), TARGET_SAMPLE_RATE, false);

            // Convert to the target format
            AudioInputStream convertedStream = AudioSystem.getAudioInputStream(targetFormat, audioInputStream);

            // Write the converted audio to the output file
            AudioSystem.write(convertedStream, AudioFileFormat.Type.WAVE, outputFile);

            // Clean up
            convertedStream.close();
            System.out.println("Conversion completed successfully!");

        } else {

            System.out.println("Audio file already meets specifications. Creating a copy...");
            AudioSystem.write(audioInputStream, AudioFileFormat.Type.WAVE, outputFile);

        }

        audioInputStream.close();
    }

    private static boolean needsConversion(AudioFormat format) {
        return format.getSampleRate() != TARGET_SAMPLE_RATE || format.getSampleSizeInBits() != TARGET_SAMPLE_SIZE || format.getChannels() != TARGET_CHANNELS;
    }
}