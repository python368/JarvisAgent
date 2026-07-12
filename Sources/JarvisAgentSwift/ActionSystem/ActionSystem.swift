import Foundation
import CoreGraphics

/// ActionSystem simulates physical keyboard and mouse events natively on macOS using CoreGraphics APIs.
public final class ActionSystem: Sendable {
    
    public init() {}
    
    /// Executes the specified action on the macOS desktop.
    /// - Parameter action: The `AgentAction` to be executed.
    public func execute(_ action: AgentAction) async throws {
        print("[ActionSystem] Executing action: \(action)")
        
        switch action {
        case .mouseMove(let x, let y):
            try moveMouse(to: CGPoint(x: x, y: y))
            
        case .mouseClick(let x, let y, let clickCount):
            try clickMouse(at: CGPoint(x: x, y: y), clickCount: clickCount)
            
        case .mouseDrag(let fromX, let fromY, let toX, let toY):
            try dragMouse(from: CGPoint(x: fromX, y: fromY), to: CGPoint(x: toX, y: toY))
            
        case .mouseScroll(let x, let y, let deltaX, let deltaY):
            try scrollMouse(at: CGPoint(x: x, y: y), deltaX: deltaX, deltaY: deltaY)
            
        case .keyPress(let keyCode, let cmd, let shift, let opt, let ctrl):
            try pressKey(keyCode: keyCode, isCommandDown: cmd, isShiftDown: shift, isOptionDown: opt, isControlDown: ctrl)
            
        case .textInput(let text):
            try typeText(text)
            
        case .wait(let ms):
            try await Task.sleep(nanoseconds: UInt64(ms) * 1_000_000)
            
        case .complete(let summary):
            print("[ActionSystem] Goal completed: \(summary)")
            
        case .abort(let reason):
            print("[ActionSystem] Execution aborted: \(reason)")
        }
    }
    
    private func moveMouse(to point: CGPoint) throws {
        guard let moveEvent = CGEvent(mouseEventSource: nil, mouseType: .mouseMoved, mouseCursorPosition: point, mouseButton: .left) else {
            throw JarvisError.executionFailed("Failed to create mouse move event")
        }
        moveEvent.post(tap: .cghidEventTap)
    }
    
    private func clickMouse(at point: CGPoint, clickCount: Int) throws {
        let source = CGEventSource(stateID: .combinedSessionState)
        
        // Move to position first
        try moveMouse(to: point)
        usleep(50000) // 50ms delay to let system register movement
        
        guard let mouseDown = CGEvent(mouseEventSource: source, mouseType: .leftMouseDown, mouseCursorPosition: point, mouseButton: .left) else {
            throw JarvisError.executionFailed("Failed to create mouse down event")
        }
        mouseDown.setIntegerValueField(.mouseEventClickState, value: Int64(clickCount))
        mouseDown.post(tap: .cghidEventTap)
        
        usleep(50000) // 50ms hold
        
        guard let mouseUp = CGEvent(mouseEventSource: source, mouseType: .leftMouseUp, mouseCursorPosition: point, mouseButton: .left) else {
            throw JarvisError.executionFailed("Failed to create mouse up event")
        }
        mouseUp.setIntegerValueField(.mouseEventClickState, value: Int64(clickCount))
        mouseUp.post(tap: .cghidEventTap)
    }
    
    private func dragMouse(from startPoint: CGPoint, to endPoint: CGPoint) throws {
        let source = CGEventSource(stateID: .combinedSessionState)
        
        // Move to start and press down
        try moveMouse(to: startPoint)
        usleep(100000)
        
        guard let mouseDown = CGEvent(mouseEventSource: source, mouseType: .leftMouseDown, mouseCursorPosition: startPoint, mouseButton: .left) else {
            throw JarvisError.executionFailed("Failed to create mouse down event for drag")
        }
        mouseDown.post(tap: .cghidEventTap)
        usleep(100000)
        
        // Drag to destination
        guard let mouseDrag = CGEvent(mouseEventSource: source, mouseType: .leftMouseDragged, mouseCursorPosition: endPoint, mouseButton: .left) else {
            throw JarvisError.executionFailed("Failed to create mouse drag event")
        }
        mouseDrag.post(tap: .cghidEventTap)
        usleep(100000)
        
        // Release at destination
        guard let mouseUp = CGEvent(mouseEventSource: source, mouseType: .leftMouseUp, mouseCursorPosition: endPoint, mouseButton: .left) else {
            throw JarvisError.executionFailed("Failed to create mouse up event for drag")
        }
        mouseUp.post(tap: .cghidEventTap)
    }
    
    private func scrollMouse(at point: CGPoint, deltaX: Int, deltaY: Int) throws {
        try moveMouse(to: point)
        usleep(50000)
        
        // Units: .pixel (0) or .line (1). Standard is line, but CoreGraphics uses scrollWheelEvent2Source
        guard let scrollEvent = CGEvent(scrollWheelEvent2Source: nil, units: .pixel, wheelCount: 2, wheel1: Int32(deltaY), wheel2: Int32(deltaX), wheel3: 0) else {
            throw JarvisError.executionFailed("Failed to create scroll wheel event")
        }
        scrollEvent.post(tap: .cghidEventTap)
    }
    
    private func pressKey(keyCode: UInt16, isCommandDown: Bool, isShiftDown: Bool, isOptionDown: Bool, isControlDown: Bool) throws {
        let source = CGEventSource(stateID: .combinedSessionState)
        
        guard let keyDown = CGEvent(keyboardEventSource: source, virtualKey: keyCode, keyDown: true) else {
            throw JarvisError.executionFailed("Failed to create key down event")
        }
        guard let keyUp = CGEvent(keyboardEventSource: source, virtualKey: keyCode, keyDown: false) else {
            throw JarvisError.executionFailed("Failed to create key up event")
        }
        
        var flags: CGEventFlags = []
        if isCommandDown { flags.insert(.maskCommand) }
        if isShiftDown { flags.insert(.maskShift) }
        if isOptionDown { flags.insert(.maskAlternate) }
        if isControlDown { flags.insert(.maskControl) }
        
        keyDown.flags = flags
        keyUp.flags = flags
        
        keyDown.post(tap: .cghidEventTap)
        usleep(20000) // 20ms delay
        keyUp.post(tap: .cghidEventTap)
    }
    
    private func typeText(_ text: String) throws {
        let source = CGEventSource(stateID: .combinedSessionState)
        
        for char in text.utf16 {
            var code = char
            guard let keyDown = CGEvent(keyboardEventSource: source, virtualKey: 0, keyDown: true),
                  let keyUp = CGEvent(keyboardEventSource: source, virtualKey: 0, keyDown: false) else {
                throw JarvisError.executionFailed("Failed to create keyboard events for typing")
            }
            
            // Put the unicode character inside the events
            keyDown.keyboardSetUnicodeString(stringLength: 1, unicodeString: &code)
            keyUp.keyboardSetUnicodeString(stringLength: 1, unicodeString: &code)
            
            keyDown.post(tap: .cghidEventTap)
            usleep(10000) // 10ms delay between key strokes to ensure accuracy
            keyUp.post(tap: .cghidEventTap)
            usleep(10000)
        }
    }
}
