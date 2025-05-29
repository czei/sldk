/**
 * THEME PARK WAITS Swarming LED Animation - Arduino C++ Version
 * 
 * Starts with all black LEDs. A swarm of colorful LEDs moves around the screen,
 * with colors changing dynamically over time creating a rainbow effect.
 * When a swarming LED passes over a position that's part of the THEME PARK WAITS
 * text, it gets captured and joins the dynamic rainbow text display.
 * Both the swarm and the captured text continuously cycle through colors,
 * creating a vibrant, ever-changing display.
 */

#include <Arduino.h>
#include <Adafruit_Protomatter.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <vector>
#include <set>
#include <cmath>

// Matrix configuration for MatrixPortal S3
#define HEIGHT 32
#define WIDTH 64
#define MAX_DEPTH 3

uint8_t rgbPins[] = {7, 8, 9, 10, 11, 12};
uint8_t addrPins[] = {17, 18, 19, 20};
uint8_t clockPin = 14;
uint8_t latchPin = 15;
uint8_t oePin = 16;

Adafruit_Protomatter matrix(
    WIDTH, HEIGHT, MAX_DEPTH, rgbPins, 4, addrPins, clockPin, latchPin, oePin, false);

// Color structure
struct Color {
    uint8_t r, g, b;
    Color(uint8_t red = 0, uint8_t green = 0, uint8_t blue = 0) : r(red), g(green), b(blue) {}
};

// Position structure
struct Position {
    int x, y;
    Position(int px = 0, int py = 0) : x(px), y(py) {}
    bool operator<(const Position& other) const {
        return (x < other.x) || (x == other.x && y < other.y);
    }
    bool operator==(const Position& other) const {
        return x == other.x && y == other.y;
    }
};

// Vector2D for velocity and forces
struct Vector2D {
    float x, y;
    Vector2D(float px = 0.0f, float py = 0.0f) : x(px), y(py) {}
    Vector2D operator+(const Vector2D& other) const { return Vector2D(x + other.x, y + other.y); }
    Vector2D operator-(const Vector2D& other) const { return Vector2D(x - other.x, y - other.y); }
    Vector2D operator*(float scalar) const { return Vector2D(x * scalar, y * scalar); }
    Vector2D operator/(float scalar) const { return Vector2D(x / scalar, y / scalar); }
    float magnitude() const { return sqrt(x * x + y * y); }
    Vector2D normalize() const { 
        float mag = magnitude();
        return mag > 0 ? Vector2D(x / mag, y / mag) : Vector2D(0, 0);
    }
};

/**
 * Convert HSV color to RGB
 */
Color hsvToRgb(float h, float s, float v) {
    h = fmod(h, 1.0f);
    float c = v * s;
    float x = c * (1.0f - fabs(fmod(h * 6.0f, 2.0f) - 1.0f));
    float m = v - c;
    
    float r, g, b;
    if (h < 1.0f/6.0f) {
        r = c; g = x; b = 0;
    } else if (h < 2.0f/6.0f) {
        r = x; g = c; b = 0;
    } else if (h < 3.0f/6.0f) {
        r = 0; g = c; b = x;
    } else if (h < 4.0f/6.0f) {
        r = 0; g = x; b = c;
    } else if (h < 5.0f/6.0f) {
        r = x; g = 0; b = c;
    } else {
        r = c; g = 0; b = x;
    }
    
    return Color(
        (uint8_t)((r + m) * 255),
        (uint8_t)((g + m) * 255),
        (uint8_t)((b + m) * 255)
    );
}

/**
 * Generate dynamic colors for the bird flock based on time and position
 */
Color getDynamicFlockColor(float timeElapsed, int birdIndex = 0) {
    // Create a rainbow effect that cycles over time
    // Different birds get slightly offset colors for variety
    float hueOffset = fmod(timeElapsed * 0.5f + birdIndex * 0.1f, 1.0f);
    
    // Create a vibrant rainbow effect
    return hsvToRgb(hueOffset, 0.9f, 0.8f);
}

/**
 * Generate dynamic colors for the captured text based on time and position
 */
Color getDynamicTextColor(float timeElapsed, Position pixelPos) {
    // Create a wave effect across the text
    // Color changes based on position and time for a flowing rainbow
    float positionOffset = (pixelPos.x / 64.0f + pixelPos.y / 32.0f) * 0.3f;
    
    // Slower color cycle for text (0.2x speed) with position-based offset
    float hue = fmod(timeElapsed * 0.2f + positionOffset, 1.0f);
    
    // Full saturation and brightness for vibrant text
    return hsvToRgb(hue, 1.0f, 1.0f);
}

/**
 * Get all pixel positions for THEME PARK WAITS text
 */
std::set<Position> getThemeParkWaitsPixels() {
    std::set<Position> pixels;
    
    // THEME PARK - First line (8 pixels tall)
    // T (x=4, y=3) - 8 LEDs tall
    for (int x = 4; x <= 8; x++) pixels.insert(Position(x, 3));
    for (int y = 4; y <= 10; y++) pixels.insert(Position(6, y));
    
    // H (x=10, y=3) - 8 LEDs tall
    for (int y = 3; y <= 10; y++) pixels.insert(Position(10, y));
    for (int y = 3; y <= 10; y++) pixels.insert(Position(14, y));
    for (int x = 11; x <= 13; x++) pixels.insert(Position(x, 6));
    
    // E (x=16, y=3) - 8 LEDs tall
    for (int y = 3; y <= 10; y++) pixels.insert(Position(16, y));
    for (int x = 16; x <= 19; x++) pixels.insert(Position(x, 3));
    for (int x = 16; x <= 18; x++) pixels.insert(Position(x, 6));
    for (int x = 16; x <= 19; x++) pixels.insert(Position(x, 10));
    
    // M (x=22, y=3) - 8 LEDs tall
    for (int y = 3; y <= 10; y++) pixels.insert(Position(22, y));
    for (int y = 3; y <= 10; y++) pixels.insert(Position(27, y));
    pixels.insert(Position(23, 4));
    pixels.insert(Position(24, 5));
    pixels.insert(Position(25, 5));
    pixels.insert(Position(26, 4));
    
    // E (x=29, y=3) - 8 LEDs tall
    for (int y = 3; y <= 10; y++) pixels.insert(Position(29, y));
    for (int x = 29; x <= 32; x++) pixels.insert(Position(x, 3));
    for (int x = 29; x <= 31; x++) pixels.insert(Position(x, 6));
    for (int x = 29; x <= 32; x++) pixels.insert(Position(x, 10));
    
    // P (x=36, y=3) - 8 LEDs tall
    for (int y = 3; y <= 10; y++) pixels.insert(Position(36, y));
    for (int x = 36; x <= 39; x++) pixels.insert(Position(x, 3));
    for (int x = 36; x <= 39; x++) pixels.insert(Position(x, 6));
    pixels.insert(Position(39, 4));
    pixels.insert(Position(39, 5));
    
    // A (x=42, y=3) - 8 LEDs tall
    for (int y = 4; y <= 10; y++) pixels.insert(Position(42, y));
    for (int y = 4; y <= 10; y++) pixels.insert(Position(46, y));
    for (int x = 43; x <= 45; x++) pixels.insert(Position(x, 3));
    for (int x = 42; x <= 46; x++) pixels.insert(Position(x, 6));
    
    // R (x=48, y=3) - 8 LEDs tall
    for (int y = 3; y <= 10; y++) pixels.insert(Position(48, y));
    for (int x = 48; x <= 51; x++) pixels.insert(Position(x, 3));
    for (int x = 48; x <= 51; x++) pixels.insert(Position(x, 6));
    pixels.insert(Position(51, 4));
    pixels.insert(Position(51, 5));
    pixels.insert(Position(50, 7));
    pixels.insert(Position(51, 8));
    pixels.insert(Position(52, 9));
    pixels.insert(Position(53, 10));
    
    // K (x=54, y=3) - 8 LEDs tall
    for (int y = 3; y <= 10; y++) pixels.insert(Position(54, y));
    pixels.insert(Position(57, 3));
    pixels.insert(Position(56, 4));
    pixels.insert(Position(55, 5));
    pixels.insert(Position(55, 6));
    pixels.insert(Position(56, 7));
    pixels.insert(Position(57, 8));
    pixels.insert(Position(58, 9));
    pixels.insert(Position(59, 10));
    
    // WAITS - Second line (16 pixels tall, moved right by 3 LEDs)
    // W (x=5, y=15) - exact pattern from screenshot
    // Left outer edge
    for (int y = 15; y <= 30; y++) {
        pixels.insert(Position(5, y));
        pixels.insert(Position(6, y));
    }
    // Right outer edge
    for (int y = 15; y <= 30; y++) {
        pixels.insert(Position(13, y));
        pixels.insert(Position(14, y));
    }
    // Middle V of W
    for (int x = 7; x <= 8; x++) pixels.insert(Position(x, 28));
    for (int x = 7; x <= 8; x++) pixels.insert(Position(x, 27));
    for (int x = 11; x <= 12; x++) pixels.insert(Position(x, 28));
    for (int x = 11; x <= 12; x++) pixels.insert(Position(x, 27));
    for (int y = 23; y <= 26; y++) pixels.insert(Position(9, y));
    for (int y = 23; y <= 26; y++) pixels.insert(Position(10, y));
    
    // A (x=16, y=15) - 10 LEDs wide, 16 pixels tall
    for (int y = 17; y <= 30; y++) pixels.insert(Position(16, y));
    for (int y = 17; y <= 30; y++) pixels.insert(Position(17, y));
    for (int y = 17; y <= 30; y++) pixels.insert(Position(24, y));
    for (int y = 17; y <= 30; y++) pixels.insert(Position(25, y));
    for (int x = 18; x <= 23; x++) pixels.insert(Position(x, 15));
    for (int x = 18; x <= 23; x++) pixels.insert(Position(x, 16));
    for (int x = 16; x <= 25; x++) pixels.insert(Position(x, 22));
    for (int x = 16; x <= 25; x++) pixels.insert(Position(x, 23));
    
    // I (x=27, y=15) - 10 LEDs wide, 16 pixels tall
    for (int x = 27; x <= 36; x++) pixels.insert(Position(x, 15));
    for (int x = 27; x <= 36; x++) pixels.insert(Position(x, 16));
    for (int x = 27; x <= 36; x++) pixels.insert(Position(x, 29));
    for (int x = 27; x <= 36; x++) pixels.insert(Position(x, 30));
    for (int y = 15; y <= 30; y++) pixels.insert(Position(31, y));
    for (int y = 15; y <= 30; y++) pixels.insert(Position(32, y));
    
    // T (x=38, y=15) - 10 LEDs wide, 16 pixels tall
    for (int x = 38; x <= 47; x++) pixels.insert(Position(x, 15));
    for (int x = 38; x <= 47; x++) pixels.insert(Position(x, 16));
    for (int y = 15; y <= 30; y++) pixels.insert(Position(42, y));
    for (int y = 15; y <= 30; y++) pixels.insert(Position(43, y));
    
    // S (x=49, y=15) - 10 LEDs wide, 16 pixels tall
    for (int x = 49; x <= 58; x++) pixels.insert(Position(x, 15));
    for (int x = 49; x <= 58; x++) pixels.insert(Position(x, 16));
    for (int y = 17; y <= 21; y++) pixels.insert(Position(49, y));
    for (int y = 17; y <= 21; y++) pixels.insert(Position(50, y));
    for (int x = 49; x <= 58; x++) pixels.insert(Position(x, 22));
    for (int x = 49; x <= 58; x++) pixels.insert(Position(x, 23));
    for (int y = 24; y <= 28; y++) pixels.insert(Position(57, y));
    for (int y = 24; y <= 28; y++) pixels.insert(Position(58, y));
    for (int x = 49; x <= 58; x++) pixels.insert(Position(x, 29));
    for (int x = 49; x <= 58; x++) pixels.insert(Position(x, 30));
    
    return pixels;
}

/**
 * FlockBird class - represents a single bird in the flock
 */
class FlockBird {
public:
    Vector2D position;
    Vector2D velocity;
    float phase;
    float speedMultiplier;
    float separationRadius;
    
    FlockBird(float x, float y, Vector2D direction) 
        : position(x, y), phase(random(0, 628) / 100.0f), 
          speedMultiplier(random(70, 130) / 100.0f),
          separationRadius(random(200, 400) / 100.0f) {
        velocity.x = direction.x * random(80, 120) / 100.0f;
        velocity.y = direction.y * random(80, 120) / 100.0f;
    }
    
    Position getPixelPos() const {
        return Position((int)round(position.x), (int)round(position.y));
    }
    
    bool isOnScreen() const {
        return position.x >= 0 && position.x < WIDTH && position.y >= 0 && position.y < HEIGHT;
    }
    
    void updateFlocking(const std::vector<FlockBird>& flock, 
                       const std::set<Position>& targetPixels,
                       const std::set<Position>& capturedPixels,
                       const Vector2D* attractionCenter) {
        // Flocking rules
        Vector2D separation = separationRule(flock);
        Vector2D alignment = alignmentRule(flock);
        Vector2D cohesion = cohesionRule(flock);
        Vector2D attraction = attractionRule(targetPixels, capturedPixels, attractionCenter);
        
        // Apply flocking forces with weights
        velocity = velocity + separation * 0.15f + alignment * 0.1f + cohesion * 0.05f + attraction * 0.3f;
        
        // Add some wing-flapping motion
        float currentTime = millis() / 1000.0f;
        velocity.x += 0.05f * sin(phase + currentTime * 8.0f) * speedMultiplier;
        velocity.y += 0.03f * cos(phase + currentTime * 6.0f) * speedMultiplier;
        
        // Limit velocity
        float maxVel = 3.0f;
        float velMag = velocity.magnitude();
        if (velMag > maxVel) {
            velocity = velocity.normalize() * maxVel;
        }
        
        // Update position
        position = position + velocity * 0.4f;
    }
    
private:
    Vector2D separationRule(const std::vector<FlockBird>& flock) {
        Vector2D steer(0, 0);
        int count = 0;
        
        for (const auto& other : flock) {
            if (&other == this) continue;
            
            Vector2D diff = position - other.position;
            float distance = diff.magnitude();
            
            if (distance > 0 && distance < separationRadius) {
                steer = steer + diff.normalize() * (1.0f / distance);
                count++;
            }
        }
        
        if (count > 0) {
            steer = steer / (float)count;
        }
        
        return steer;
    }
    
    Vector2D alignmentRule(const std::vector<FlockBird>& flock) {
        Vector2D avgVel(0, 0);
        int count = 0;
        float neighborDistance = 8.0f;
        
        for (const auto& other : flock) {
            if (&other == this) continue;
            
            Vector2D diff = position - other.position;
            float distance = diff.magnitude();
            
            if (distance < neighborDistance) {
                avgVel = avgVel + other.velocity;
                count++;
            }
        }
        
        if (count > 0) {
            avgVel = avgVel / (float)count;
            return avgVel - velocity;
        }
        
        return Vector2D(0, 0);
    }
    
    Vector2D cohesionRule(const std::vector<FlockBird>& flock) {
        Vector2D center(0, 0);
        int count = 0;
        float neighborDistance = 12.0f;
        
        for (const auto& other : flock) {
            if (&other == this) continue;
            
            Vector2D diff = position - other.position;
            float distance = diff.magnitude();
            
            if (distance < neighborDistance) {
                center = center + other.position;
                count++;
            }
        }
        
        if (count > 0) {
            center = center / (float)count;
            return (center - position) * 0.01f;
        }
        
        return Vector2D(0, 0);
    }
    
    Vector2D attractionRule(const std::set<Position>& targetPixels,
                           const std::set<Position>& capturedPixels,
                           const Vector2D* attractionCenter) {
        if (attractionCenter == nullptr) {
            return Vector2D(0, 0);
        }
        
        Vector2D diff = *attractionCenter - position;
        float distance = diff.magnitude();
        
        if (distance > 0) {
            float attractionStrength = 0.5f;
            return diff.normalize() * attractionStrength;
        }
        
        return Vector2D(0, 0);
    }
};

// Global variables
std::set<Position> targetPixels;
std::set<Position> capturedPixels;
std::vector<FlockBird> flock;
unsigned long startTime;
unsigned long lastUpdate = 0;
unsigned long lastSpawnTime = 0;
int currentDirectionIdx = 0;
bool animationComplete = false;
unsigned long completionTime = 0;

const char* directions[] = {"left", "right", "top", "bottom", "top_left", "top_right", "bottom_left", "bottom_right"};
const int numDirections = 8;
const float spawnInterval = 3.0f; // seconds

/**
 * Create a flock of birds from a specific direction
 */
std::vector<FlockBird> createFlockFromDirection(int numBirds, const char* direction) {
    std::vector<FlockBird> newFlock;
    
    float baseX, baseY;
    Vector2D flightDir;
    
    // Simplified entry points (full implementation would use find_best_entry_point)
    if (strcmp(direction, "left") == 0) {
        baseX = -10; baseY = 16;
        flightDir = Vector2D(2.0f, random(-50, 50) / 100.0f);
    } else if (strcmp(direction, "right") == 0) {
        baseX = 74; baseY = 16;
        flightDir = Vector2D(-2.0f, random(-50, 50) / 100.0f);
    } else if (strcmp(direction, "top") == 0) {
        baseX = 32; baseY = -10;
        flightDir = Vector2D(random(-50, 50) / 100.0f, 2.0f);
    } else if (strcmp(direction, "bottom") == 0) {
        baseX = 32; baseY = 42;
        flightDir = Vector2D(random(-50, 50) / 100.0f, -2.0f);
    } else { // diagonal entries simplified
        baseX = 32; baseY = 16;
        flightDir = Vector2D(1.0f, 1.0f);
    }
    
    // Create formation
    for (int i = 0; i < numBirds; i++) {
        int row = i / 8;
        int col = i % 8;
        float offsetX = (col - 4) * 2 + random(-100, 100) / 100.0f;
        float offsetY = row * 3 + random(-100, 100) / 100.0f;
        
        float birdX = baseX + offsetX;
        float birdY = baseY + offsetY;
        
        newFlock.push_back(FlockBird(birdX, birdY, flightDir));
    }
    
    return newFlock;
}

void setup() {
    Serial.begin(115200);
    
    // Initialize matrix
    ProtomatterStatus status = matrix.begin();
    if (status != PROTOMATTER_OK) {
        Serial.print("Matrix initialization failed: ");
        Serial.println(status);
        for(;;);
    }
    
    matrix.fillScreen(0);
    matrix.show();
    
    // Initialize random seed
    randomSeed(analogRead(0));
    
    // Get target pixels
    targetPixels = getThemeParkWaitsPixels();
    
    startTime = millis();
    lastUpdate = startTime;
    
    Serial.print("Starting bird flock animation with ");
    Serial.print(targetPixels.size());
    Serial.println(" LEDs needed...");
    Serial.println("Watch as flocks of colorful birds build THEME PARK WAITS!");
}

void loop() {
    unsigned long currentTime = millis();
    
    // Update every ~50ms for smooth movement
    if (currentTime - lastUpdate < 50) {
        return;
    }
    
    float timeElapsed = (currentTime - startTime) / 1000.0f;
    lastUpdate = currentTime;
    
    // Check if all text is complete
    bool textComplete = capturedPixels.size() >= targetPixels.size();
    
    if (textComplete && completionTime == 0) {
        completionTime = currentTime;
        Serial.print("THEME PARK WAITS completed in ");
        Serial.print(timeElapsed);
        Serial.println(" seconds!");
        Serial.println("Program will end in 1 second...");
    }
    
    // End program 1 second after completion
    if (completionTime != 0 && currentTime - completionTime >= 1000) {
        Serial.println("Animation complete!");
        animationComplete = true;
        matrix.fillScreen(0);
        matrix.show();
        return;
    }
    
    // Normal flocking behavior when text is not complete
    if (!textComplete) {
        int remainingLeds = targetPixels.size() - capturedPixels.size();
        
        // Spawn new flock if needed
        float spawnIntervalMs = spawnInterval * 1000;
        if (remainingLeds > 0 && 
            (currentTime - startTime) - lastSpawnTime > spawnIntervalMs &&
            flock.size() < 200) {
            
            int birdsToSpawn = min(50, remainingLeds);
            const char* direction = directions[currentDirectionIdx];
            
            std::vector<FlockBird> newFlock = createFlockFromDirection(birdsToSpawn, direction);
            flock.insert(flock.end(), newFlock.begin(), newFlock.end());
            
            Serial.print("Flock of ");
            Serial.print(birdsToSpawn);
            Serial.print(" birds flying in from ");
            Serial.println(direction);
            
            currentDirectionIdx = (currentDirectionIdx + 1) % numDirections;
            lastSpawnTime = currentTime - startTime;
        }
        
        // Update bird positions with simplified flocking
        for (auto& bird : flock) {
            bird.updateFlocking(flock, targetPixels, capturedPixels, nullptr);
        }
        
        // Check for LED lighting
        for (const auto& bird : flock) {
            if (bird.isOnScreen()) {
                Position pixelPos = bird.getPixelPos();
                if (targetPixels.count(pixelPos) && !capturedPixels.count(pixelPos)) {
                    capturedPixels.insert(pixelPos);
                    Serial.print("LED lit at (");
                    Serial.print(pixelPos.x);
                    Serial.print(",");
                    Serial.print(pixelPos.y);
                    Serial.print(") ");
                    Serial.print(capturedPixels.size());
                    Serial.print("/");
                    Serial.println(targetPixels.size());
                }
            }
        }
        
        // Remove birds that have flown off screen
        flock.erase(std::remove_if(flock.begin(), flock.end(), 
            [](const FlockBird& bird) {
                return bird.position.x < -25 || bird.position.x > 89 || 
                       bird.position.y < -25 || bird.position.y > 57;
            }), flock.end());
    }
    
    // Update display
    matrix.fillScreen(0);
    
    // Draw captured text pixels with dynamic colors
    for (const auto& pixel : capturedPixels) {
        Color textColor = getDynamicTextColor(timeElapsed, pixel);
        uint16_t color = matrix.color565(textColor.r, textColor.g, textColor.b);
        matrix.drawPixel(pixel.x, pixel.y, color);
    }
    
    // Draw birds with dynamic colors
    for (size_t i = 0; i < flock.size(); i++) {
        const auto& bird = flock[i];
        if (bird.isOnScreen()) {
            Position birdPos = bird.getPixelPos();
            Color birdColor = getDynamicFlockColor(timeElapsed, i);
            uint16_t color = matrix.color565(birdColor.r, birdColor.g, birdColor.b);
            matrix.drawPixel(birdPos.x, birdPos.y, color);
        }
    }
    
    matrix.show();
}