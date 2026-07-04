import SwiftUI
import AppKit

struct ContentView: View {
    @State private var prompt: String = "请描述你要我在屏幕上完成的任务。"
    @State private var base64Preview: String? = nil
    @State private var isCapturing = false
    @State private var isInferencing = false
    @State private var plan: ControlPlan? = nil
    @State private var showAPIConfig = false

    @State private var endpointText: String = "https://api.example.com/v1/multimodal"
    @State private var apiKey: String = ""
    @State private var model: String = "gpt-vision-pro"

    var body: some View {
        ZStack {
            // Liquid Glass style background
            Rectangle()
                .fill(.ultraThinMaterial)
                .background(.clear)
                .ignoresSafeArea()
                .overlay(
                    AnimatedGlassGradient()
                        .blendMode(.plusLighter)
                        .opacity(0.45)
                )

            mainPanel
                .padding(20)
                .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
                .overlay(
                    RoundedRectangle(cornerRadius: 24, style: .continuous)
                        .strokeBorder(.white.opacity(0.15), lineWidth: 1)
                )
                .shadow(color: .black.opacity(0.25), radius: 30, x: 0, y: 20)
                .padding()
        }
        .sheet(isPresented: $showAPIConfig) { apiConfigSheet }
        .toolbar { toolbar }
    }

    private var mainPanel: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack(alignment: .center) {
                Text("Jarvis Agent V3")
                    .font(.system(size: 22, weight: .semibold, design: .rounded))
                    .foregroundStyle(.primary)
                Spacer()
                Button {
                    showAPIConfig = true
                } label: {
                    Label("配置 API", systemImage: "key.fill")
                }
                .buttonStyle(.borderedProminent)
            }

            screenshotPreview
                .frame(height: 220)
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))

            TextEditor(text: $prompt)
                .font(.system(size: 14))
                .scrollContentBackground(.hidden)
                .padding(12)
                .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
                .overlay(
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .strokeBorder(.white.opacity(0.12), lineWidth: 1)
                )

            HStack(spacing: 12) {
                Button(action: captureNow) {
                    Label(isCapturing ? "正在截图…" : "截图", systemImage: isCapturing ? "camera.metering.center.weighted" : "camera.fill")
                }
                .buttonStyle(.borderedProminent)
                .disabled(isCapturing)

                Button(action: inferNow) {
                    Label(isInferencing ? "分析中…" : "分析屏幕", systemImage: isInferencing ? "brain.head.profile" : "sparkles")
                }
                .buttonStyle(.bordered)
                .disabled(isInferencing)

                Button(action: executePlan) {
                    Label("执行计划", systemImage: "play.fill")
                }
                .buttonStyle(.bordered)
                .disabled(plan == nil)

                Spacer()

                if let plan {
                    Text("动作数: \(plan.actions.count)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        }
    }

    private var screenshotPreview: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(.thinMaterial)
            if let base64 = base64Preview, let img = NSImage.fromBase64(base64) {
                Image(nsImage: img)
                    .resizable()
                    .scaledToFit()
                    .overlay(alignment: .topTrailing) {
                        Text("预览")
                            .font(.caption2)
                            .padding(6)
                            .background(.ultraThinMaterial, in: Capsule())
                            .padding(6)
                    }
            } else {
                VStack(spacing: 8) {
                    Image(systemName: "display")
                        .font(.system(size: 32))
                        .foregroundStyle(.secondary)
                    Text("暂无截图")
                        .foregroundStyle(.secondary)
                }
            }
        }
    }

    private var apiConfigSheet: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("多模态 API 配置")
                .font(.title3.bold())
            TextField("Endpoint", text: $endpointText)
                .textFieldStyle(.roundedBorder)
            SecureField("API Key", text: $apiKey)
                .textFieldStyle(.roundedBorder)
            TextField("Model", text: $model)
                .textFieldStyle(.roundedBorder)
            HStack {
                Spacer()
                Button("保存") {
                    if let url = URL(string: endpointText) {
                        AgentCore.shared.configureAPI(endpoint: url, apiKey: apiKey, model: model)
                    }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(20)
        .frame(minWidth: 420)
        .background(.ultraThinMaterial)
    }

    @ToolbarContentBuilder
    private var toolbar: some ToolbarContent {
        ToolbarItem(placement: .automatic) {
            Button {
                requestPermissions()
            } label: {
                Label("权限", systemImage: "lock.open.display")
            }
        }
    }

    private func captureNow() {
        isCapturing = true
        Task { @MainActor in
            defer { isCapturing = false }
            do {
                let b64 = try await AgentCore.shared.captureScreenBase64()
                base64Preview = b64
            } catch {
                presentError(error)
            }
        }
    }

    private func inferNow() {
        isInferencing = true
        Task { @MainActor in
            defer { isInferencing = false }
            do {
                let plan = try await AgentCore.shared.analyzeScreen(prompt: prompt)
                withAnimation { self.plan = plan }
            } catch {
                presentError(error)
            }
        }
    }

    private func executePlan() {
        guard let plan else { return }
        Task { @MainActor in
            do {
                try AgentCore.shared.execute(plan: plan)
            } catch {
                presentError(error)
            }
        }
    }

    private func requestPermissions() {
        // Screen recording permission is managed by the system when SC is first used.
        // Accessibility permission (for CGEvent post) needs user to enable in System Settings.
        // Provide a helper jump to settings URL if available, else show instructions.
        if let url = URL(string: "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility") {
            NSWorkspace.shared.open(url)
        }
    }

    private func presentError(_ error: Error) {
        let alert = NSAlert()
        alert.messageText = "错误"
        alert.informativeText = error.localizedDescription
        alert.alertStyle = .warning
        alert.runModal()
    }
}

// MARK: - Animated Glass Gradient

fileprivate struct AnimatedGlassGradient: View {
    @State private var phase: CGFloat = 0
    var body: some View {
        TimelineView(.animation) { timeline in
            let t = timeline.date.timeIntervalSinceReferenceDate
            Canvas { ctx, size in
                var gradient = Gradient(colors: [
                    Color.cyan.opacity(0.35),
                    Color.purple.opacity(0.25),
                    Color.blue.opacity(0.25),
                    Color.indigo.opacity(0.3)
                ])
                let start = CGPoint(x: 0, y: 0)
                let end = CGPoint(x: size.width, y: size.height)
                let rect = CGRect(origin: .zero, size: size)
                let angle = Angle(degrees: (sin(t/3) + 1) * 90)
                ctx.fill(Path(rect), with: .conicGradient(gradient, center: CGPoint(x: size.width/2, y: size.height/2), angle: angle))
            }
        }
        .blur(radius: 24)
    }
}

// MARK: - Helpers

extension NSImage {
    static func fromBase64(_ base64: String) -> NSImage? {
        guard let data = Data(base64Encoded: base64) else { return nil }
        return NSImage(data: data)
    }
}

#Preview {
    ContentView()
}
