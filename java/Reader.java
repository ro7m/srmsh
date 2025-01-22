import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

public class EnhancedImageProcessor {
    
    public static void main(String[] args) {
        try {
            BufferedImage image = ImageIO.read(new File("input_image.jpg"));
            String result = processImageWithEnhancements(image);
            
            saveToFile(result, "enhanced_output.txt");
            System.out.println("Enhanced processed matrix:");
            System.out.println(result);
            
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
    public static String processImageWithEnhancements(BufferedImage image) {
        // Scale image for better processing
        BufferedImage scaled = scaleImage(image, 2.0);
        
        // Apply preprocessing
        BufferedImage processed = enhancedPreprocess(scaled);
        
        // Convert to enhanced character matrix
        return convertToEnhancedMatrix(processed);
    }
    
    private static BufferedImage scaleImage(BufferedImage original, double scale) {
        int newWidth = (int) (original.getWidth() * scale);
        int newHeight = (int) (original.getHeight() * scale);
        
        BufferedImage scaled = new BufferedImage(newWidth, newHeight, original.getType());
        Graphics2D g2d = scaled.createGraphics();
        
        g2d.setRenderingHint(RenderingHints.KEY_INTERPOLATION,
                            RenderingHints.VALUE_INTERPOLATION_BILINEAR);
        g2d.drawImage(original, 0, 0, newWidth, newHeight, null);
        g2d.dispose();
        
        return scaled;
    }
    
    private static BufferedImage enhancedPreprocess(BufferedImage original) {
        int width = original.getWidth();
        int height = original.getHeight();
        
        BufferedImage processed = new BufferedImage(
            width, height, BufferedImage.TYPE_BYTE_GRAY);
        
        // Apply adaptive thresholding
        int windowSize = 15;
        double c = 0.1; // threshold adjustment constant
        
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                // Calculate local mean
                int sum = 0;
                int count = 0;
                
                for (int wy = Math.max(0, y - windowSize/2); 
                     wy < Math.min(height, y + windowSize/2); wy++) {
                    for (int wx = Math.max(0, x - windowSize/2); 
                         wx < Math.min(width, x + windowSize/2); wx++) {
                        Color color = new Color(original.getRGB(wx, wy));
                        sum += (color.getRed() + color.getGreen() + color.getBlue()) / 3;
                        count++;
                    }
                }
                
                double mean = sum / (double) count;
                
                // Get current pixel value
                Color color = new Color(original.getRGB(x, y));
                int gray = (color.getRed() + color.getGreen() + color.getBlue()) / 3;
                
                // Apply adaptive threshold
                int newPixel = gray < (mean * (1.0 - c)) ? 0 : 255;
                processed.setRGB(x, y, new Color(newPixel, newPixel, newPixel).getRGB());
            }
        }
        
        return processed;
    }
    
    private static String convertToEnhancedMatrix(BufferedImage image) {
        StringBuilder matrix = new StringBuilder();
        int width = image.getWidth();
        int height = image.getHeight();
        
        // Improved sampling rates
        int sampleX = 3;
        int sampleY = 6;
        
        // Enhanced character set for better detail
        char[] chars = {' ', '░', '▒', '▓', '█'};
        
        for (int y = 0; y < height; y += sampleY) {
            for (int x = 0; x < width; x += sampleX) {
                // Calculate average intensity for the sample area
                int totalIntensity = 0;
                int samples = 0;
                
                for (int sy = y; sy < Math.min(y + sampleY, height); sy++) {
                    for (int sx = x; sx < Math.min(x + sampleX, width); sx++) {
                        Color color = new Color(image.getRGB(sx, sy));
                        totalIntensity += (color.getRed() + color.getGreen() + color.getBlue()) / 3;
                        samples++;
                    }
                }
                
                int avgIntensity = totalIntensity / samples;
                
                // Map intensity to character
                int charIndex = (int) ((255 - avgIntensity) * (chars.length - 1) / 255.0);
                matrix.append(chars[charIndex]);
            }
            matrix.append('\n');
        }
        
        return matrix.toString();
    }
    
    private static void saveToFile(String content, String filename) throws IOException {
        try (FileWriter writer = new FileWriter(filename)) {
            writer.write(content);
        }
    }
                                   }
