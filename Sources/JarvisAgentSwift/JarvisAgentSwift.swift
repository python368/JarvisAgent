import Foundation
import ArgumentParser

@main
struct JarvisAgentSwift: AsyncParsableCommand {
    
    @Option(name: .shortAndLong, help: "The AI provider (openai, google, groq, local).")
    var provider: String = "openai"
    
    @Option(name: .shortAndLong, help: "The model name to use.")
    var model: String = "gpt-4o"
    
    @Option(name: .shortAndLong, help: "API Key for the provider.")
    var apiKey: String?
    
    @Option(name: .shortAndLong, help: "API Endpoint URL.")
    var endpoint: String?
    
    @Argument(help: "The objective you want Jarvis to accomplish.")
    var objective: String?

    static let configuration = CommandConfiguration(
        commandName: "jarvis",
        abstract: "Jarvis V4 - AI Computer Use Agent for macOS",
        version: "4.0.0"
    )

    func run() async throws {
        print("--- Jarvis V4: AI Computer Use Agent ---")
        
        let targetObjective: String
        if let obj = objective {
            targetObjective = obj
        } else {
            print("Please enter your objective: ", terminator: "")
            fflush(stdout)
            guard let input = readLine(), !input.isEmpty else {
                print("No objective provided. Exiting.")
                return
            }
            targetObjective = input
        }
        
        // Configuration resolution
        let resolvedEndpoint = endpoint ?? defaultEndpoint(for: provider)
        let resolvedKey = apiKey ?? "mock" // Default to mock if not provided for safety/demo
        
        let config = ModelConfig(
            providerName: provider,
            apiEndpoint: resolvedEndpoint,
            apiKey: resolvedKey,
            modelName: model
        )
        
        // Initialize Subsystems
        let vision = VisionSystem()
        let action = ActionSystem()
        let safety = SafetyController()
        let memory = MemorySystem()
        let modelManager = ModelManager(config: config)
        
        // Initialize Core
        let core = AgentCore(
            visionSystem: vision,
            actionSystem: action,
            safetyController: safety,
            modelManager: modelManager,
            memorySystem: memory
        )
        
        // Execute Loop
        await core.run(objective: targetObjective)
        
        print("\n[Jarvis] Session ended. Thank you for using Jarvis V4.")
    }
    
    private func defaultEndpoint(for provider: String) -> String {
        switch provider.lowercased() {
        case "openai": return "https://api.openai.com/v1/chat/completions"
        case "google": return "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        case "groq": return "https://api.groq.com/openai/v1/chat/completions"
        default: return "http://localhost:11434/v1/chat/completions" // Default local Ollama
        }
    }
}
