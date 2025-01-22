import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.*;
import java.util.List;

public class ImageToVectors {
    
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
        
        @Override
        public String toString() {
            return String.format("region[%d,%d,%d,%d]:%d", 
                startX, startY, endX, endY, points.size());
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
        // Convert to binary first
        BufferedImage binary = convertToBinary(image);
        
        // Find text regions
        List<TextRegion> regions = findTextRegions(binary);
        
        // Convert regions to vector representation
        return convertRegionsToVectors(regions);
    }
    
    private static BufferedImage convertToBinary(BufferedImage original) {
        int width = original.getWidth();
        int height = original.getHeight();
        BufferedImage binary = new BufferedImage(width, height, BufferedImage.TYPE_BYTE_BINARY);
        
        int threshold = 180;
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                Color color = new Color(original.getRGB(x, y));
                int gray = (color.getRed() + color.getGreen() + color.getBlue()) / 3;
                binary.setRGB(x, y, gray < threshold ? Color.BLACK.getRGB() : Color.WHITE.getRGB());
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
                    TextRegion region = new TextRegion(x, y);
                    floodFill(binary, x, y, visited, region);
                    if (region.points.size() > 10) { // Filter noise
                        regions.add(region);
                    }
                }
            }
        }
        
        return regions;
    }
    
    private static void floodFill(BufferedImage image, int x, int y, 
                                boolean[][] visited, TextRegion region) {
        if (x < 0 || x >= image.getWidth() || y < 0 || y >= image.getHeight() 
            || visited[y][x] || !isBlack(image, x, y)) {
            return;
        }
        
        visited[y][x] = true;
        region.addPoint(x, y);
        
        // Check 8 directions
        for (int dy = -1; dy <= 1; dy++) {
            for (int dx = -1; dx <= 1; dx++) {
                if (dx != 0 || dy != 0) {
                    floodFill(image, x + dx, y + dy, visited, region);
                }
            }
        }
    }
    
    private static boolean isBlack(BufferedImage image, int x, int y) {
        return (image.getRGB(x, y) & 0xFFFFFF) == 0;
    }
    
    private static String convertRegionsToVectors(List<TextRegion> regions) {
        StringBuilder sb = new StringBuilder();
        
        // Sort regions by Y position for natural reading order
        regions.sort((r1, r2) -> r1.startY - r2.startY);
        
        for (int i = 0; i < regions.size(); i++) {
            TextRegion region = regions.get(i);
            
            // Calculate region properties
            int width = region.endX - region.startX;
            int height = region.endY - region.startY;
            double density = region.points.size() / (double)(width * height);
            
            // Create vector representation
            sb.append(String.format("R%d:%d,%d,%d,%d,%.2f\n", 
                i, region.startX, region.startY, width, height, density));
            
            // Add significant point patterns
            List<Point> keyPoints = findKeyPoints(region.points);
            sb.append("K:");
            for (Point p : keyPoints) {
                sb.append(String.format("%d,%d;", p.x - region.startX, p.y - region.startY));
            }
            sb.append("\n");
        }
        
        return sb.toString();
    }
    
    private static List<Point> findKeyPoints(List<Point> points) {
        // Find significant points that define the shape
        List<Point> keyPoints = new ArrayList<>();
        if (points.isEmpty()) return keyPoints;
        
        // Sort points by X coordinate
        points.sort((p1, p2) -> p1.x - p2.x);
        
        // Add extremes and some intermediate points
        keyPoints.add(points.get(0)); // leftmost
        keyPoints.add(points.get(points.size() - 1)); // rightmost
        
        // Add some intermediate points
        int step = points.size() / 5;
        if (step > 0) {
            for (int i = step; i < points.size() - step; i += step) {
                keyPoints.add(points.get(i));
            }
        }
        
        return keyPoints;
    }
    
    private static void saveToFile(String content, String filename) throws IOException {
        try (FileWriter writer = new FileWriter(filename)) {
            writer.write(content);
        }
    }
}
