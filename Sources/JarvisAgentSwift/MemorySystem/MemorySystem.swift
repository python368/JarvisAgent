import Foundation

/// MemorySystem coordinates historical session states, learned user behaviors, and environment persistent preferences.
public final class MemorySystem: @unchecked Sendable {
    
    private let queue = DispatchQueue(label: "com.jarvis.memory")
    private let storageURL: URL
    private var memoryData: MemoryData
    
    private struct MemoryData: Codable {
        var preferences: [String: String]
        var completedSessions: [SessionRecord]
    }
    
    public struct SessionRecord: Codable {
        public let timestamp: Date
        public let objective: String
        public let stepsCount: Int
        public let outcome: String
    }
    
    public init() {
        let fileManager = FileManager.default
        let homeDir = fileManager.homeDirectoryForCurrentUser
        let jarvisFolder = homeDir.appendingPathComponent(".jarvis", isDirectory: true)
        
        // Ensure folder exists
        try? fileManager.createDirectory(at: jarvisFolder, withIntermediateDirectories: true, attributes: nil)
        
        self.storageURL = jarvisFolder.appendingPathComponent("memory.json")
        self.memoryData = MemoryData(preferences: [:], completedSessions: [])
        
        loadMemory()
    }
    
    /// Saves a key-value preference.
    public func savePreference(key: String, value: String) {
        queue.sync {
            memoryData.preferences[key] = value
            persistMemory()
        }
    }
    
    /// Retrieves a key-value preference.
    public func getPreference(key: String) -> String? {
        queue.sync {
            return memoryData.preferences[key]
        }
    }
    
    /// Records a completed task session.
    public func recordSession(objective: String, steps: Int, outcome: String) {
        queue.sync {
            let record = SessionRecord(timestamp: Date(), objective: objective, stepsCount: steps, outcome: outcome)
            memoryData.completedSessions.append(record)
            persistMemory()
        }
    }
    
    /// Retrieves all historical session records.
    public func fetchSessionHistory() -> [SessionRecord] {
        queue.sync {
            return memoryData.completedSessions
        }
    }
    
    /// Resets all memory data.
    public func clearAllMemory() {
        queue.sync {
            memoryData = MemoryData(preferences: [:], completedSessions: [])
            persistMemory()
        }
    }
    
    private func loadMemory() {
        guard FileManager.default.fileExists(atPath: storageURL.path) else {
            return
        }
        
        do {
            let data = try Data(contentsOf: storageURL)
            let decoded = try JSONDecoder().decode(MemoryData.self, from: data)
            self.memoryData = decoded
        } catch {
            print("[MemorySystem] Error reading memory.json: \(error.localizedDescription). Initializing fresh memory.")
        }
    }
    
    private func persistMemory() {
        do {
            let encoder = JSONEncoder()
            encoder.outputFormatting = .prettyPrinted
            let data = try encoder.encode(memoryData)
            try data.write(to: storageURL)
        } catch {
            print("[MemorySystem] Error writing memory.json: \(error.localizedDescription)")
        }
    }
}
