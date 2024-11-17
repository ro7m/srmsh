package org.voice.service;

import io.github.givimad.whisperjni.WhisperContext;
import io.github.givimad.whisperjni.WhisperFullParams;
import io.github.givimad.whisperjni.WhisperJNI;
import io.github.givimad.whisperjni.WhisperSamplingStrategy;

import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.UnsupportedAudioFileException;
import java.io.File;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.file.Path;

public class WhisperService {
    public WhisperJNI whisper;
    public WhisperContext whisperContext;

    public WhisperService() {
        var loadOptions = new WhisperJNI.LoadOptions();
        loadOptions.logger = System.out::println;
        try {
            WhisperJNI.loadLibrary(loadOptions);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        WhisperJNI.setLibraryLogger(null);
        whisper = new WhisperJNI();
        String modelName = "/Users/312609/Downloads/ggml-base.en-q5_0.bin";
        try {
            whisperContext = whisper.init(Path.of(modelName));
        } catch (IOException e) {
            System.out.println("Model " + modelName + " not found");
        }
    }

    public String transcribe(float[] audioData) {

        StringBuilder fulltext = new StringBuilder();
        try (var ctx = whisperContext) {
            var params = new WhisperFullParams(WhisperSamplingStrategy.GREEDY);
            int result = whisper.full(ctx, params, audioData, audioData.length);
            if (result != 0) {
                throw new RuntimeException("Transcription failed with code " + result);
            }
            int numSegments = whisper.fullNSegments(ctx);
            for (int i = 0; i < numSegments; i++) {
                String segmentText = whisper.fullGetSegmentText(ctx, i);
                if (segmentText != null && !segmentText.isEmpty()) {
                    fulltext.append(segmentText).append(" ");
                }
            }
            return fulltext.toString().trim();
        }

    }

    public float[] processAudioFile(File infile) throws UnsupportedAudioFileException, IOException {
        // sample is a 16 bit int 16000hz little endian wav file
        String outputFile = "/tmp/cnv.wav";
        Path samplePath = Path.of(outputFile);
        AudioConverter.convertAudioFile(infile, new File(outputFile));
        AudioInputStream audioInputStream = AudioSystem.getAudioInputStream(samplePath.toFile());
        // read all the available data to a little endian capture buffer
        ByteBuffer captureBuffer = ByteBuffer.allocate(audioInputStream.available());
        captureBuffer.order(ByteOrder.LITTLE_ENDIAN);
        int read = audioInputStream.read(captureBuffer.array());
        if (read == -1) {
            throw new IOException("Empty file");
        }
        // obtain the 16 int audio samples, short type in java
        var shortBuffer = captureBuffer.asShortBuffer();
        // transform the samples to f32 samples
        float[] samples = new float[captureBuffer.capacity() / 2];
        var i = 0;
        while (shortBuffer.hasRemaining()) {
            samples[i++] = Float.max(-1f, Float.min(((float) shortBuffer.get()) / (float) Short.MAX_VALUE, 1f));
        }
        return samples;
    }


}