//
//  EchoAppApp.swift
//  EchoApp
//
//  Created by Michelle Lee on 7/24/25.
//

import SwiftUI

@main
struct EchoAppApp: App {
    @StateObject var authManager = AuthManager()
    @StateObject var accessorySessionManager = AccessorySessionManager()
    
    var body: some Scene {
        WindowGroup {
            // WelcomePageView()
            RootView()
                .environmentObject(authManager)
                .environmentObject(accessorySessionManager)
        }
    }
}

