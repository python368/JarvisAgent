import Foundation
import CoreGraphics
import ImageIO

/// VisionSystem is responsible for capturing screen state, display characteristics,
/// and preparing visual representations for multimodal AI model processing.
public final class VisionSystem: Sendable {
    
    public init() {}
    
    /// Captures the primary display of the macOS device.
    /// - Returns: A `CGImage` representing the current screen.
    public func captureMainDisplay() throws -> CGImage {
        print("[VisionSystem] Capturing main display...")
        
        // CGMainDisplayID returns the display ID of the primary screen
        let displayID = CGMainDisplayID()
        
        guard let image = CGDisplayCreateImage(displayID) else {
            throw JarvisError.visionCaptureFailed("Failed to capture main display using CGDisplayCreateImage.")
        }
        
        return image
    }
    
    /// Converts a `CGImage` to binary `Data` in the specified format.
    /// - Parameters:
    ///   - image: The `CGImage` to convert.
    ///   - isPNG: If true, formats as PNG; otherwise, formats as JPEG.
    ///   - compressionQuality: A value between 0.0 and 1.0 (for JPEG).
    /// - Returns: Binary representation of the image.
    public func convertToData(image: CGImage, isPNG: Bool = false, compressionQuality: Double = 0.7) throws -> Data {
        let data = NSMutableData()
        let typeIdentifier = isPNG ? "public.png" as CFString : "public.jpeg" as CFString
        
        guard let destination = CGImageDestinationCreateWithData(data, typeIdentifier, 1, nil) else {
            throw JarvisError.visionCaptureFailed("Failed to initialize CGImageDestination.")
        }
        
        let options: [CFString: Any] = isPNG ? [:] : [
            kCGImageDestinationLossyCompressionQuality: compressionQuality
        ]
        
        CGImageDestinationAddImage(destination, image, options as CFDictionary)
        
        guard CGImageDestinationFinalize(destination) else {
            throw JarvisError.visionCaptureFailed("Failed to finalize image destination serialization.")
        }
        
        return data as Data
    }
    
    /// Captures the screen and encodes it directly as a Base64-encoded string.
    /// Useful for immediate inclusion in AI multimodal requests.
    /// - Returns: Base64 string of the screen image.
    public func captureMainDisplayAsBase64(isPNG: Bool = false, compressionQuality: Double = 0.6) throws -> String {
        let image = try captureMainDisplay()
        let data = try convertToData(image: image, isPNG: isPNG, compressionQuality: compressionQuality)
        return data.base64EncodedString()
    }
    
    /// Saves the current display screenshot to a local file.
    /// - Parameter destinationURL: The local URL path where the image should be saved.
    public func saveScreenshot(to destinationURL: URL, isPNG: Bool = false) throws {
        let image = try captureMainDisplay()
        let data = try convertToData(image: image, isPNG: isPNG, compressionQuality: 0.9)
        try data.write(to: destinationURL)
        print("[VisionSystem] Screenshot saved successfully to: \(destinationURL.path)")
    }
}
