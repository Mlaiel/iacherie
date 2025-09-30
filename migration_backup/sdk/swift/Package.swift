// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "AinfluenceSDK",
    platforms: [
        .iOS(.v15),
        .macOS(.v12),
        .tvOS(.v15),
        .watchOS(.v8)
    ],
    products: [
        // Products define the executables and libraries a package produces, making them visible to other packages.
        .library(
            name: "AinfluenceSDK",
            targets: ["AinfluenceSDK"]
        ),
        .library(
            name: "AinfluenceCore",
            targets: ["AinfluenceCore"]
        ),
        .library(
            name: "AinfluenceAudio",
            targets: ["AinfluenceAudio"]
        ),
        .library(
            name: "AinfluenceML",
            targets: ["AinfluenceML"]
        ),
        .library(
            name: "AinfluenceSecurity",
            targets: ["AinfluenceSecurity"]
        )
    ],
    dependencies: [
        // Network and HTTP dependencies
        .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.8.0"),
        
        // WebSocket support
        .package(url: "https://github.com/daltoniam/Starscream.git", from: "4.0.6"),
        
        // JSON handling
        .package(url: "https://github.com/Flight-School/AnyCodable.git", from: "0.6.7"),
        
        // Keychain services for secure storage
        .package(url: "https://github.com/evgenyneu/keychain-swift.git", from: "21.0.0"),
        
        // Logging
        .package(url: "https://github.com/apple/swift-log.git", from: "1.5.3"),
        
        // Cryptography
        .package(url: "https://github.com/apple/swift-crypto.git", from: "3.0.0"),
        
        // Audio processing
        .package(url: "https://github.com/AudioKit/AudioKit.git", from: "5.6.2"),
        
        // Testing utilities
        .package(url: "https://github.com/pointfreeco/swift-snapshot-testing.git", from: "1.15.0"),
        
        // Performance monitoring
        .package(url: "https://github.com/apple/swift-metrics.git", from: "2.4.1"),
        
        // Async utilities
        .package(url: "https://github.com/apple/swift-async-algorithms.git", from: "1.0.0"),
        
        // UI components (iOS only)
        .package(url: "https://github.com/SwiftUIX/SwiftUIX.git", from: "0.1.9")
    ],
    targets: [
        // Core SDK target
        .target(
            name: "AinfluenceSDK",
            dependencies: [
                "AinfluenceCore",
                "AinfluenceAudio", 
                "AinfluenceML",
                "AinfluenceSecurity",
                "Alamofire",
                "Starscream",
                "AnyCodable",
                .product(name: "KeychainSwift", package: "keychain-swift"),
                .product(name: "Logging", package: "swift-log"),
                .product(name: "Crypto", package: "swift-crypto"),
                .product(name: "Metrics", package: "swift-metrics"),
                .product(name: "AsyncAlgorithms", package: "swift-async-algorithms"),
                "SwiftUIX"
            ],
            path: "Sources/AinfluenceSDK",
            resources: [
                .process("Resources")
            ]
        ),
        
        // Core functionalities target
        .target(
            name: "AinfluenceCore",
            dependencies: [
                "Alamofire",
                "AnyCodable",
                .product(name: "Logging", package: "swift-log"),
                .product(name: "Metrics", package: "swift-metrics")
            ],
            path: "Sources/AinfluenceCore"
        ),
        
        // Audio processing target
        .target(
            name: "AinfluenceAudio",
            dependencies: [
                "AinfluenceCore",
                "AudioKit",
                .product(name: "Logging", package: "swift-log")
            ],
            path: "Sources/AinfluenceAudio"
        ),
        
        // Machine Learning target
        .target(
            name: "AinfluenceML",
            dependencies: [
                "AinfluenceCore",
                .product(name: "Logging", package: "swift-log")
            ],
            path: "Sources/AinfluenceML"
        ),
        
        // Security target
        .target(
            name: "AinfluenceSecurity",
            dependencies: [
                "AinfluenceCore",
                .product(name: "KeychainSwift", package: "keychain-swift"),
                .product(name: "Crypto", package: "swift-crypto"),
                .product(name: "Logging", package: "swift-log")
            ],
            path: "Sources/AinfluenceSecurity"
        ),
        
        // Test targets
        .testTarget(
            name: "AinfluenceSDKTests",
            dependencies: [
                "AinfluenceSDK",
                .product(name: "SnapshotTesting", package: "swift-snapshot-testing")
            ],
            path: "Tests/AinfluenceSDKTests"
        ),
        
        .testTarget(
            name: "AinfluenceCoreTests", 
            dependencies: [
                "AinfluenceCore",
                .product(name: "SnapshotTesting", package: "swift-snapshot-testing")
            ],
            path: "Tests/AinfluenceCoreTests"
        ),
        
        .testTarget(
            name: "AinfluenceAudioTests",
            dependencies: [
                "AinfluenceAudio",
                .product(name: "SnapshotTesting", package: "swift-snapshot-testing")
            ],
            path: "Tests/AinfluenceAudioTests"
        ),
        
        .testTarget(
            name: "AinfluenceMLTests",
            dependencies: [
                "AinfluenceML",
                .product(name: "SnapshotTesting", package: "swift-snapshot-testing")
            ],
            path: "Tests/AinfluenceMLTests"
        ),
        
        .testTarget(
            name: "AinfluenceSecurityTests",
            dependencies: [
                "AinfluenceSecurity",
                .product(name: "SnapshotTesting", package: "swift-snapshot-testing")
            ],
            path: "Tests/AinfluenceSecurityTests"
        )
    ],
    swiftLanguageVersions: [.v5]
)

// Conditional dependencies based on platform
#if os(iOS)
package.dependencies.append(
    .package(url: "https://github.com/firebase/firebase-ios-sdk.git", from: "10.18.0")
)
#endif

// Development and testing enhancements
#if DEBUG
package.dependencies.append(
    .package(url: "https://github.com/realm/SwiftLint.git", from: "0.54.0")
)
#endif