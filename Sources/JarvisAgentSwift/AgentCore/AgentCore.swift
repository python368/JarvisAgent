import Foundation

/// AgentCore is the intelligence orchestrator of Jarvis. It coordinates Vision, Action,
/// Safety, Model reasoning, and Memory systems inside a standard ReAct-style loop.
public final class AgentCore: Sendable {
    
    private let visionSystem: VisionSystem
    private let actionSystem: ActionSystem
    private let safetyController: SafetyController
    private let modelManager: ModelManager
    private let memorySystem: MemorySystem
    
    private let maxSteps = 15
    
    public init(
        visionSystem: VisionSystem,
        actionSystem: ActionSystem,
        safetyController: SafetyController,
        modelManager: ModelManager,
        memorySystem: MemorySystem
    ) {
        self.visionSystem = visionSystem
        self.actionSystem = actionSystem
        self.safetyController = safetyController
        self.modelManager = modelManager
        self.memorySystem = memorySystem
    }
    
    /// Executes the core loop to achieve the specified natural language goal.
    /// - Parameter objective: The user's target instruction.
    public func run(objective: String) async {
        print("\n🚀 [AgentCore] Starting core reasoning loop for objective: '\(objective)'")
        
        var history: [AgentDecision] = []
        var currentStep = 1
        var finalOutcome = "Incomplete"
        
        while currentStep <= maxSteps {
            print("\n--- [Step \(currentStep)/\(maxSteps)] ---")
            
            // 1. Capture screen for multi-modal analysis
            var screenBase64: String? = nil
            do {
                screenBase64 = try visionSystem.captureMainDisplayAsBase64()
            } catch {
                print("⚠️ [AgentCore] Warning: Failed to capture screen: \(error.localizedDescription). Proceeding with text-only context.")
            }
            
            // 2. Fetch decision from AI Model
            let decision: AgentDecision
            do {
                decision = try await modelManager.fetchNextDecision(
                    objective: objective,
                    screenBase64: screenBase64,
                    history: history
                )
            } catch {
                print("❌ [AgentCore] Error fetching next decision: \(error.localizedDescription)")
                finalOutcome = "Failed during reasoning: \(error.localizedDescription)"
                break
            }
            
            print("🧠 [AgentCore] Thought: \(decision.thought)")
            print("🎯 [AgentCore] Proposed Action: \(decision.action)")
            
            // 3. Safety Clearance
            let authorized = await safetyController.authorizeAction(decision.action)
            guard authorized else {
                print("🛑 [AgentCore] Safety block or user denial. Stopping loop.")
                finalOutcome = "Blocked by Safety / User"
                break
            }
            
            // 4. Handle exit actions
            switch decision.action {
            case .complete(let summary):
                print("🎉 [AgentCore] Goal reached! Summary: \(summary)")
                finalOutcome = "Success: \(summary)"
                history.append(decision)
                
                // Record completion session in memory
                memorySystem.recordSession(objective: objective, steps: currentStep, outcome: finalOutcome)
                return
                
            case .abort(let reason):
                print("🛑 [AgentCore] Agent aborted task. Reason: \(reason)")
                finalOutcome = "Aborted: \(reason)"
                history.append(decision)
                
                // Record aborted session
                memorySystem.recordSession(objective: objective, steps: currentStep, outcome: finalOutcome)
                return
                
            default:
                break
            }
            
            // 5. Execute Action
            do {
                try await actionSystem.execute(decision.action)
            } catch {
                print("❌ [AgentCore] Action execution failed: \(error.localizedDescription)")
                finalOutcome = "Execution Failed: \(error.localizedDescription)"
                break
            }
            
            // 6. Record history and advance step
            history.append(decision)
            currentStep += 1
            
            // Small pause between steps for system stability
            try? await Task.sleep(nanoseconds: 500_000_000) // 500ms
        }
        
        if currentStep > maxSteps {
            finalOutcome = "Timeout: Reached max steps limit (\(maxSteps))"
            print("⚠️ [AgentCore] Loop reached limit without completing.")
        }
        
        // Save overall session trace
        memorySystem.recordSession(objective: objective, steps: currentStep - 1, outcome: finalOutcome)
        print("\n🏁 [AgentCore] Core loop ended. Final Outcome: \(finalOutcome)")
    }
}
