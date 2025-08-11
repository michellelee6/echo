//
//  SignInView.swift
//  EchoApp
//
//  Created by Michelle Lee on 7/24/25.
//

// MARK: - SignInView.swift
// This file defines the UI for the Sign In screen.

import SwiftUI
import AuthenticationServices

struct SignInView: View {
    @EnvironmentObject var authManager: AuthManager
    @State private var selectedTab: appTab = .home

    var body: some View {
        ZStack {
            Image("EchoBackground")
                .resizable()
                .aspectRatio(contentMode: .fill)
                .ignoresSafeArea()
            
            VStack {
                Spacer()
                
                Image(systemName: "person.fill")
                    .resizable()
                    .frame(width: 50, height: 50)
                    .foregroundColor(Color(red: 0.0745, green: 0.1608, blue: 0.2392))
                    .padding(.top, 160.0)
                    .padding(.bottom, 10)
                
                Text("Sign In")
                    .font(.largeTitle)
                    .fontWeight(.medium)
                    .foregroundColor(Color(red: 0.0745, green: 0.1608, blue: 0.2392))
                    .padding(.bottom, 8)
                
                Text("Customize your navigation \n experience.")
                    .font(.body)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
                    .padding(.bottom, 40)
                
                Spacer()
                
                SignInWithAppleButton(.continue) { request in
                    request.requestedScopes = [.fullName, .email]
                } onCompletion: { result in
                    switch result {
                    case .success(let authResults):
                        // Process authorization directly here
                        if let appleIDCredential = authResults.credential as? ASAuthorizationAppleIDCredential {
                            // Handle user ID, name, etc.
                            print("Apple Sign In success! UserID: \(appleIDCredential.user)")
                            DispatchQueue.main.async {
                                authManager.isSignedIn = true
                            }
                        }
                    case .failure(let error):
                        print("Apple Sign In failed: \(error.localizedDescription)")
                    }
                }
                .signInWithAppleButtonStyle(.white)
                .frame(width: 328.0, height: 50)
                .cornerRadius(26)
                .padding(.horizontal)
                .padding(.top, 190.0)
                
                Button("Use a passkey") {
                    print("Use a passkey tapped")
                }
                .font(.headline)
                .foregroundColor(Color(red: 0.0, green: 0.3921, blue: 0.5804))
                .frame(width: 328.0, height: 50)
                .background(Color(red: 0.0, green: 0.3921, blue: 0.5804, opacity: 0.5))
                .cornerRadius(26)
                .padding(.horizontal)
                .padding(.top, 10)
                
                Spacer()
            }
        }
    }
}

struct SignInView_Previews: PreviewProvider {
    static var previews: some View {
        SignInView()
    }
}
