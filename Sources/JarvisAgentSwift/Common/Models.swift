import Foundation
import CoreGraphics

/// Custom errors that might occur within the Jarvis system.
public enum JarvisError: Error, LocalizedError {
    case invalidAction(String)
    case executionFailed(String)
    case visionCaptureFailed(String)
    case apiRequestFailed(String)
    case unauthorizedAction(String)
    case safetyBlock(String)

    public var errorDescription: String? {
        switch self {
        case .invalidAction(let msg): return "Invalid Action: \(msg)"
        case .executionFailed(let msg): return "Execution Failed: \(msg)"
        case .visionCaptureFailed(let msg): return "Vision Capture Failed: \(msg)"
        case .apiRequestFailed(let msg): return "API Request Failed: \(msg)"
        case .unauthorizedAction(let msg): return "Unauthorized Action: \(msg)"
        case .safetyBlock(let msg): return "Action Blocked by Safety Controller: \(msg)"
        }
    }
}

/// Represents the physical actions that Jarvis can perform on the macOS system.
public enum AgentAction: Codable, Equatable, Sendable {
    case mouseMove(x: Double, y: Double)
    case mouseClick(x: Double, y: Double, clickCount: Int)
    case mouseDrag(fromX: Double, fromY: Double, toX: Double, toY: Double)
    case mouseScroll(x: Double, y: Double, deltaX: Int, deltaY: Int)
    case keyPress(keyCode: UInt16, isCommandDown: Bool, isShiftDown: Bool, isOptionDown: Bool, isControlDown: Bool)
    case textInput(text: String)
    case wait(ms: Int)
    case complete(summary: String)
    case abort(reason: String)

    private enum CodingKeys: String, CodingKey {
        case type, x, y, clickCount, fromX, fromY, toX, toY, deltaX, deltaY, keyCode, isCommandDown, isShiftDown, isOptionDown, isControlDown, text, ms, summary, reason
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        let type = try container.decode(String.self, forKey: .type)
        switch type {
        case "mouseMove":
            let x = try container.decode(Double.self, forKey: .x)
            let y = try container.decode(Double.self, forKey: .y)
            self = .mouseMove(x: x, y: y)
        case "mouseClick":
            let x = try container.decode(Double.self, forKey: .x)
            let y = try container.decode(Double.self, forKey: .y)
            let clickCount = try container.decode(Int.self, forKey: .clickCount)
            self = .mouseClick(x: x, y: y, clickCount: clickCount)
        case "mouseDrag":
            let fromX = try container.decode(Double.self, forKey: .fromX)
            let fromY = try container.decode(Double.self, forKey: .fromY)
            let toX = try container.decode(Double.self, forKey: .toX)
            let toY = try container.decode(Double.self, forKey: .toY)
            self = .mouseDrag(fromX: fromX, fromY: fromY, toX: toX, toY: toY)
        case "mouseScroll":
            let x = try container.decode(Double.self, forKey: .x)
            let y = try container.decode(Double.self, forKey: .y)
            let deltaX = try container.decode(Int.self, forKey: .deltaX)
            let deltaY = try container.decode(Int.self, forKey: .deltaY)
            self = .mouseScroll(x: x, y: y, deltaX: deltaX, deltaY: deltaY)
        case "keyPress":
            let keyCode = try container.decode(UInt16.self, forKey: .keyCode)
            let cmd = try container.decodeIfPresent(Bool.self, forKey: .isCommandDown) ?? false
            let shift = try container.decodeIfPresent(Bool.self, forKey: .isShiftDown) ?? false
            let opt = try container.decodeIfPresent(Bool.self, forKey: .isOptionDown) ?? false
            let ctrl = try container.decodeIfPresent(Bool.self, forKey: .isControlDown) ?? false
            self = .keyPress(keyCode: keyCode, isCommandDown: cmd, isShiftDown: shift, isOptionDown: opt, isControlDown: ctrl)
        case "textInput":
            let text = try container.decode(String.self, forKey: .text)
            self = .textInput(text: text)
        case "wait":
            let ms = try container.decode(Int.self, forKey: .ms)
            self = .wait(ms: ms)
        case "complete":
            let summary = try container.decode(String.self, forKey: .summary)
            self = .complete(summary: summary)
        case "abort":
            let reason = try container.decode(String.self, forKey: .reason)
            self = .abort(reason: reason)
        default:
            throw DecodingError.dataCorruptedError(forKey: .type, in: container, debugDescription: "Unknown action type: \(type)")
        }
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        switch self {
        case .mouseMove(let x, let y):
            try container.encode("mouseMove", forKey: .type)
            try container.encode(x, forKey: .x)
            try container.encode(y, forKey: .y)
        case .mouseClick(let x, let y, let clickCount):
            try container.encode("mouseClick", forKey: .type)
            try container.encode(x, forKey: .x)
            try container.encode(y, forKey: .y)
            try container.encode(clickCount, forKey: .clickCount)
        case .mouseDrag(let fromX, let fromY, let toX, let toY):
            try container.encode("mouseDrag", forKey: .type)
            try container.encode(fromX, forKey: .fromX)
            try container.encode(fromY, forKey: .fromY)
            try container.encode(toX, forKey: .toX)
            try container.encode(toY, forKey: .toY)
        case .mouseScroll(let x, let y, let deltaX, let deltaY):
            try container.encode("mouseScroll", forKey: .type)
            try container.encode(x, forKey: .x)
            try container.encode(y, forKey: .y)
            try container.encode(deltaX, forKey: .deltaX)
            try container.encode(deltaY, forKey: .deltaY)
        case .keyPress(let keyCode, let cmd, let shift, let opt, let ctrl):
            try container.encode("keyPress", forKey: .type)
            try container.encode(keyCode, forKey: .keyCode)
            try container.encode(cmd, forKey: .isCommandDown)
            try container.encode(shift, forKey: .isShiftDown)
            try container.encode(opt, forKey: .isOptionDown)
            try container.encode(ctrl, forKey: .isControlDown)
        case .textInput(let text):
            try container.encode("textInput", forKey: .type)
            try container.encode(text, forKey: .text)
        case .wait(let ms):
            try container.encode("wait", forKey: .type)
            try container.encode(ms, forKey: .ms)
        case .complete(let summary):
            try container.encode("complete", forKey: .type)
            try container.encode(summary, forKey: .summary)
        case .abort(let reason):
            try container.encode("abort", forKey: .type)
            try container.encode(reason, forKey: .reason)
        }
    }
}

/// A decision produced by the AI Agent Core reasoning.
public struct AgentDecision: Codable, Equatable, Sendable {
    public let thought: String
    public let action: AgentAction

    public init(thought: String, action: AgentAction) {
        self.thought = thought
        self.action = action
    }
}

/// Configuration settings for different AI providers.
public struct ModelConfig: Codable, Equatable, Sendable {
    public var providerName: String
    public var apiEndpoint: String
    public var apiKey: String
    public var modelName: String
    public var temperature: Double

    public init(providerName: String, apiEndpoint: String, apiKey: String, modelName: String, temperature: Double = 0.2) {
        self.providerName = providerName
        self.apiEndpoint = apiEndpoint
        self.apiKey = apiKey
        self.modelName = modelName
        self.temperature = temperature
    }
}
