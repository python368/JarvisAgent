import Foundation

/// ModelManager orchestrates the selection, configuration, and invocation of both local and cloud AI models.
/// It supports standard OpenAI, Google Gemini, Groq, and custom OpenAI-compatible endpoints.
public final class ModelManager: Sendable {
    
    private let activeConfig: ModelConfig
    
    public init(config: ModelConfig) {
        self.activeConfig = config
    }
    
    /// Requests the next action from the AI model based on the current objective, screen state, and history.
    /// - Parameters:
    ///   - objective: The overarching user objective (e.g. "Open Safari and search for Swift news").
    ///   - screenBase64: Optional base64-encoded image of the screen.
    ///   - history: The list of actions taken so far in this session.
    /// - Returns: An `AgentDecision` detailing the thought and the action to perform.
    public func fetchNextDecision(objective: String, screenBase64: String?, history: [AgentDecision]) async throws -> AgentDecision {
        print("[ModelManager] Dispatching reasoning task to model '\(activeConfig.modelName)' via provider '\(activeConfig.providerName)'...")
        
        // If API key is not configured or set to mock, return a mock action for demonstration/testing.
        if activeConfig.apiKey.isEmpty || activeConfig.apiKey == "mock" || activeConfig.apiKey == "PLACEHOLDER" {
            return try generateMockDecision(objective: objective, history: history)
        }
        
        let systemPrompt = """
        You are Jarvis V4, an AI computer use agent operating on macOS.
        Analyze the current screen and user objective, and return your next action as a valid JSON matching this exact structure:
        {
          "thought": "Your reasoning about the current screen layout and task status.",
          "action": {
            "type": "mouseMove" | "mouseClick" | "mouseDrag" | "mouseScroll" | "keyPress" | "textInput" | "wait" | "complete" | "abort",
            "x": 100.0,
            "y": 200.0,
            "clickCount": 1,
            "fromX": 100.0,
            "fromY": 200.0,
            "toX": 300.0,
            "toY": 400.0,
            "deltaX": 0,
            "deltaY": -10,
            "keyCode": 36,
            "isCommandDown": false,
            "isShiftDown": false,
            "isOptionDown": false,
            "isControlDown": false,
            "text": "Hello world",
            "ms": 1000,
            "summary": "Completed successfully",
            "reason": "Failed to locate window"
          }
        }
        Provide ONLY valid, raw JSON, conforming exactly to standard Swift Codable specifications for AgentDecision and AgentAction.
        """
        
        // Set up the API endpoint and request
        guard let url = URL(string: activeConfig.apiEndpoint) else {
            throw JarvisError.apiRequestFailed("Invalid API endpoint URL: \(activeConfig.apiEndpoint)")
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Add auth headers depending on provider
        if activeConfig.providerName.lowercased() == "google" {
            request.setValue(activeConfig.apiKey, forHTTPHeaderField: "x-goog-api-key")
        } else {
            request.setValue("Bearer \(activeConfig.apiKey)", forHTTPHeaderField: "Authorization")
        }
        
        // Construct the messages payload
        var messages: [[String: Any]] = []
        messages.append(["role": "system", "content": systemPrompt])
        
        // Construct content array for multimodal user message
        var userContent: [[String: Any]] = []
        
        // Add textual instructions
        var textPrompt = "Objective: \(objective)\n"
        if !history.isEmpty {
            textPrompt += "\nPrevious action history:\n"
            for (index, decision) in history.enumerated() {
                textPrompt += "\(index + 1). Thought: \(decision.thought) -> Action: \(decision.action)\n"
            }
        }
        userContent.append(["type": "text", "text": textPrompt])
        
        // Add visual screen state if available
        if let base64 = screenBase64 {
            userContent.append([
                "type": "image_url",
                "image_url": [
                    "url": "data:image/jpeg;base64,\(base64)"
                ]
            ])
        }
        
        messages.append(["role": "user", "content": userContent])
        
        let requestBody: [String: Any] = [
            "model": activeConfig.modelName,
            "messages": messages,
            "temperature": activeConfig.temperature,
            "response_format": ["type": "json_object"]
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, (200...299).contains(httpResponse.statusCode) else {
            let errorString = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw JarvisError.apiRequestFailed("API returned non-success response: \(errorString)")
        }
        
        // Parse response JSON
        guard let jsonResult = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let choices = jsonResult["choices"] as? [[String: Any]],
              let firstChoice = choices.first,
              let message = firstChoice["message"] as? [String: Any],
              let rawContent = message["content"] as? String else {
            throw JarvisError.apiRequestFailed("Failed to parse standard chat completion response structure.")
        }
        
        guard let contentData = rawContent.data(using: .utf8) else {
            throw JarvisError.apiRequestFailed("Model returned content that could not be read as UTF-8.")
        }
        
        // Decode to our AgentDecision
        do {
            let decision = try JSONDecoder().decode(AgentDecision.self, from: contentData)
            return decision
        } catch {
            print("[ModelManager] Error parsing model decision JSON: \(error)")
            print("[ModelManager] Raw output was: \(rawContent)")
            throw JarvisError.apiRequestFailed("JSON structure did not match AgentDecision: \(error.localizedDescription)")
        }
    }
    
    /// Generates structured deterministic decisions for mock runs or standard verification tests.
    private func generateMockDecision(objective: String, history: [AgentDecision]) throws -> AgentDecision {
        print("[ModelManager] API key is empty/mock. Emulating model decision...")
        
        let step = history.count
        
        if step == 0 {
            return AgentDecision(
                thought: "We need to begin the objective: '\(objective)'. Let's first move the cursor to a safe starting area on the screen.",
                action: .mouseMove(x: 500, y: 400)
            )
        } else if step == 1 {
            return AgentDecision(
                thought: "Now that we moved the cursor to the starting area, let's click to focus.",
                action: .mouseClick(x: 500, y: 400, clickCount: 1)
            )
        } else if step == 2 {
            return AgentDecision(
                thought: "Let's input a test query to confirm the keyboard is working.",
                action: .textInput(text: "Jarvis v4 initialized")
            )
        } else if step == 3 {
            return AgentDecision(
                thought: "Let's press 'Enter' (virtual key code 36) to submit the input.",
                action: .keyPress(keyCode: 36, isCommandDown: false, isShiftDown: false, isOptionDown: false, isControlDown: false)
            )
        } else {
            return AgentDecision(
                thought: "We have finished all verification steps for objective: '\(objective)'.",
                action: .complete(summary: "Successfully verified core loop in Mock Mode.")
            )
        }
    }
}
