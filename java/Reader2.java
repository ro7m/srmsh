import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.*;

public class EfficientImageToVectors {
    
    static class TextRegion {
        int startX, startY, endX, endY;
        List<Point> points = new ArrayList<>();
        
        TextRegion(int startX, int startY) {
            this.startX = startX;
            this.startY = startY;
            this.endX = startX;
            this.endY = startY;
        }
        
        void addPoint(int x, int y) {
            points.add(new Point(x, y));
            endX = Math.max(endX, x);
            endY = Math.max(endY, y);
        }
    }
    
    public static void main(String[] args) {
        try {
            BufferedImage image = ImageIO.read(new File("input_image.jpg"));
            String vectorData = processImageToVectors(image);
            
            saveToFile(vectorData, "vector_output.txt");
            System.out.println("Vector representation:");
            System.out.println(vectorData);
            
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
    public static String processImageToVectors(BufferedImage image) {
        // Convert to binary and downsample for efficiency
        BufferedImage binary = convertToBinary(image, 2);
        
        // Find text regions
        List<TextRegion> regions = findTextRegions(binary);
        
        // Convert regions to vector representation
        return convertRegionsToVectors(regions);
    }
    
    private static BufferedImage convertToBinary(BufferedImage original, int downsample) {
        int width = original.getWidth() / downsample;
        int height = original.getHeight() / downsample;
        BufferedImage binary = new BufferedImage(width, height, BufferedImage.TYPE_BYTE_BINARY);
        
        int threshold = 180;
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                int avgGray = 0;
                int samples = 0;
                
                // Average over downsampled area
                for (int dy = 0; dy < downsample; dy++) {
                    for (int dx = 0; dx < downsample; dx++) {
                        int origX = x * downsample + dx;
                        int origY = y * downsample + dy;
                        if (origX < original.getWidth() && origY < original.getHeight()) {
                            Color color = new Color(original.getRGB(origX, origY));
                            avgGray += (color.getRed() + color.getGreen() + color.getBlue()) / 3;
                            samples++;
                        }
                    }
                }
                
                avgGray /= samples;
                binary.setRGB(x, y, avgGray < threshold ? Color.BLACK.getRGB() : Color.WHITE.getRGB());
            }
        }
        return binary;
    }
    
    private static List<TextRegion> findTextRegions(BufferedImage binary) {
        List<TextRegion> regions = new ArrayList<>();
        boolean[][] visited = new boolean[binary.getHeight()][binary.getWidth()];
        
        for (int y = 0; y < binary.getHeight(); y++) {
            for (int x = 0; x < binary.getWidth(); x++) {
                if (!visited[y][x] && isBlack(binary, x, y)) {
                    TextRegion region = iterativeFloodFill(binary, x, y, visited);
                    if (region.points.size() > 5) { // Adjusted threshold for downsampled image
                        regions.add(region);
                    }
                }
            }
        }
        
        return regions;
    }
    
    private static TextRegion iterativeFloodFill(BufferedImage image, int startX, int startY, boolean[][] visited) {
        TextRegion region = new TextRegion(startX, startY);
        Stack<Point> stack = new Stack<>();
        stack.push(new Point(startX, startY));
        
        while (!stack.isEmpty()) {
            Point p = stack.pop();
            int x = p.x;
            int y = p.y;
            
            if (x < 0 || x >= image.getWidth() || y < 0 || y >= image.getHeight() 
                || visited[y][x] || !isBlack(image, x, y)) {
                continue;
            }
            
            visited[y][x] = true;
            region.addPoint(x, y);
            
            // Add 4-connected neighbors (using 4-connectivity instead of 8 for efficiency)
            stack.push(new Point(x + 1, y));
            stack.push(new Point(x - 1, y));
            stack.push(new Point(x, y + 1));
            stack.push(new Point(x, y - 1));
        }
        
        return region;
    }
    
    private static boolean isBlack(BufferedImage image, int x, int y) {
        return (image.getRGB(x, y) & 0xFFFFFF) == 0;
    }
    
    private static String convertRegionsToVectors(List<TextRegion> regions) {
        StringBuilder sb = new StringBuilder();
        
        // Sort regions by Y position for natural reading order
        regions.sort((r1, r2) -> {
            if (Math.abs(r1.startY - r2.startY) < 20) { // Group regions in same line
                return r1.startX - r2.startX;
            }
            return r1.startY - r2.startY;
        });
        
        // Group regions into lines
        List<List<TextRegion>> lines = new ArrayList<>();
        List<TextRegion> currentLine = new ArrayList<>();
        int lastY = -100;
        
        for (TextRegion region : regions) {
            if (Math.abs(region.startY - lastY) > 20) {
                if (!currentLine.isEmpty()) {
                    lines.add(currentLine);
                    currentLine = new ArrayList<>();
                }
            }
            currentLine.add(region);
            lastY = region.startY;
        }
        if (!currentLine.isEmpty()) {
            lines.add(currentLine);
        }
        
        // Output vectors by line
        for (int lineNum = 0; lineNum < lines.size(); lineNum++) {
            sb.append(String.format("L%d:", lineNum));
            for (TextRegion region : lines.get(lineNum)) {
                // Output relative positions within line
                sb.append(String.format(" %d,%d,%d,%d", 
                    region.startX, region.startY - lastY,
                    region.endX - region.startX,
                    region.endY - region.startY));
            }
            sb.append("\n");
        }
        
        return sb.toString();
    }
    
    private static void saveToFile(String content, String filename) throws IOException {
        try (FileWriter writer = new FileWriter(filename)) {
            writer.write(content);
        }
    }
}
