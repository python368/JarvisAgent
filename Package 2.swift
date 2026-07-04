// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "JarvisAgentSwift",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(name: "JarvisAgentSwiftApp", targets: ["JarvisAgentSwift"])
    ],
    targets: [
        .executableTarget(
            name: "JarvisAgentSwift",
            path: "Sources/JarvisAgentSwift"
        )
    ]
)
