//
//  RootView.swift
//  EchoApp
//
//  Created by Michelle Lee on 7/26/25.
//

import SwiftUI

struct RootView: View {
    @EnvironmentObject var authManager: AuthManager
    @EnvironmentObject var accessorySessionManager: AccessorySessionManager

    var body: some View {
        if !accessorySessionManager.accessoryPaired {
            WelcomePageView()
        } else if !authManager.isSignedIn {
            SignInView()
        } else {
            HomePage()
        }
    }
}

#Preview {
    RootView()
}
