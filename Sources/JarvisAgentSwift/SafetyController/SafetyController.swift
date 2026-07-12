import Foundation

/// SafetyController enforces permission scopes, prompt-to-confirm rules for hazardous actions,
/// audit logging, and the core emergency abort kill-switch.
public final class SafetyController: Sendable {
    
    private let auditLogURL: URL
    
    public init() {
        // Set up an audit log file under user's home or local temp folder
        let homeDir = FileManager.default.homeDirectoryForCurrentUser
        self.auditLogURL = homeDir.appendingPathComponent(".jarvis_audit.log")
        setupAuditLog()
    }
    
    /// Checks if an action is high-risk and requires manual confirmation.
    /// Aligns strictly with Section 8 of the Product Whitepaper.
    public func isHighRiskAction(_ action: AgentAction) -> Bool {
        switch action {
        case .keyPress(let keyCode, let isCmd, _, _, _):
            // Cmd+Backspace is delete (KeyCode 51)
            if isCmd && keyCode == 51 { return true }
            // Cmd+Q or other system triggers could be added here
            return false
            
        case .textInput(let text):
            let lowercasedText = text.lowercased()
            
            // 1. File Deletion (Section 8.1)
            let deletePatterns = ["rm ", "delete ", "erase ", "format ", "unlink "]
            
            // 2. Modify System Settings (Section 8.2)
            let systemPatterns = ["defaults write", "networksetup", "scutil", "systemsetup", "pmset", "nvram"]
            
            // 3. Send Important Information (Section 8.3)
            let communicationPatterns = ["curl ", "ssh ", "scp ", "ftp ", "mail ", "send "]
            
            // 4. Sensitive Operations (Section 8.4)
            let sensitivePatterns = ["sudo ", "chmod ", "chown ", "passwd ", "kill ", "reboot", "shutdown", "mkfs"]
            
            let allPatterns = deletePatterns + systemPatterns + communicationPatterns + sensitivePatterns
            
            for pattern in allPatterns {
                if lowercasedText.contains(pattern) {
                    return true
                }
            }
            return false
            
        case .mouseClick:
            // Mouse clicks on specific system areas could be high-risk, 
            // but usually require vision-level context to confirm.
            // For now, we trust the Agent reasoning but confirm the physical execution if it's text-based.
            return false
            
        case .abort, .complete, .mouseMove, .mouseDrag, .mouseScroll, .wait:
            return false
        }
    }
    
    /// Validates whether an action can proceed, prompting the user if it's high risk.
    /// - Parameter action: The action to perform.
    /// - Returns: True if authorized, false if blocked.
    public func authorizeAction(_ action: AgentAction) async -> Bool {
        // Log action to audit trail first
        logToAudit(action)
        
        guard isHighRiskAction(action) else {
            return true
        }
        
        print("\n⚠️ [SAFETY WARNING] Jarvis is about to perform a HIGH-RISK action:")
        print("➡️ Action Details: \(action)")
        print("Do you authorize this action? (yes/no): ", terminator: "")
        fflush(stdout)
        
        guard let response = readLine()?.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() else {
            return false
        }
        
        let authorized = (response == "y" || response == "yes")
        if authorized {
            print("✅ Action authorized by user.")
        } else {
            print("❌ Action blocked by user.")
        }
        return authorized
    }
    
    private func setupAuditLog() {
        if !FileManager.default.fileExists(atPath: auditLogURL.path) {
            FileManager.default.createFile(atPath: auditLogURL.path, contents: nil, attributes: nil)
        }
    }
    
    private func logToAudit(_ action: AgentAction) {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
        let timestamp = formatter.string(from: Date())
        let logEntry = "[\(timestamp)] \(action)\n"
        
        if let data = logEntry.data(using: .utf8) {
            if let fileHandle = try? FileHandle(forWritingTo: auditLogURL) {
                fileHandle.seekToEndOfFile()
                fileHandle.write(data)
                try? fileHandle.close()
            }
        }
    }
}
