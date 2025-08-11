//
//  WelcomePage.swift
//  EchoApp
//
//  Created by Michelle Lee on 7/24/25.
//

import SwiftUI

struct WelcomePageView: View {
    @State var accessorySessionManager = AccessorySessionManager()
    @State private var shouldNavigateToSignIn = false

    var body: some View {
        NavigationStack {
            VStack {
                Text("Welcome to")
                    .font(.title3)
                    .fontWeight(.regular)
                    .foregroundColor(.black)
                    .padding(.top, 120.0)

                Text("Echo")
                    .font(.system(size: 80, weight: .bold, design: .default))
                    .foregroundColor(Color(red: 0.0745, green: 0.1608, blue: 0.2392))
                    .padding(.bottom, 1.0)

                Text("Pair your belt to get started")
                    .font(.subheadline)
                    .foregroundColor(.gray)
                    .padding(.top, 2.0)

                // Pair Button
                Button(action: {
                    Task {
                        await accessorySessionManager.presentPicker()
                    }
                }) {
                    Text("Pair")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .frame(width: 325.0, height: 55.0)
                        .background(Color(red: 0.0, green: 0.3921, blue: 0.5804, opacity: 0.5))
                        .cornerRadius(26)
                }
                .padding(.horizontal)
                .padding(.top, 400.0)

            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(
                Image("EchoBackground")
                    .resizable()
                    .scaledToFill()
            )
            .ignoresSafeArea()
        }
        /*
        NavigationLink(destination: SignInView(), isActive: $accessorySessionManager.accessoryPaired) {
            EmptyView()
        }
         */
        
        /*
        if accessorySessionManager.accessoryPaired {
            SignInView()
        }
         */
    }
}

#Preview {
    WelcomePageView()
}

