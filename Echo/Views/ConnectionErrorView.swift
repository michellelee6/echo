//
//  ConnectionErrorView.swift
//  EchoApp
//
//  Created by Michelle Lee on 7/24/25.
//

// MARK: - ConnectionErrorView.swift
// This file defines the UI for the connection error screen.
import SwiftUI

struct ConnectionErrorView: View {
    var body: some View {
        VStack {
            Spacer()

            Image(systemName: "antenna.radiowaves.left.and.right.slash")
                .resizable()
                .frame(width: 50, height: 50)
                .foregroundColor(Color(red: 0.07450980392156863, green: 0.1607843137254902, blue: 0.23921568627450981))
                .padding(.top, 200.0)

            Text("Your belt was unable to connect.")
                .font(.largeTitle)
                .fontWeight(.regular)
                .foregroundColor(Color(red: 0.07450980392156863, green: 0.1607843137254902, blue: 0.23921568627450981))
                .multilineTextAlignment(.center)
                .padding(.horizontal)
                .padding(.bottom, 10)

            Text("Ensure that Bluetooth \n is enabled on your device.")
                .font(.callout)
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
                .padding(.bottom, 100)

            Button(action: {
               // Go back to the pairing stage to try again
            }) {
                Text("Try Again")
                    .font(.headline)
                    .fontWeight(.regular)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color(red: 0.0, green: 0.39215686274509803, blue: 0.5803921568627451, opacity: 0.5))
                    .cornerRadius(26)
            }
            .frame(width: 328.0, height: 50)
            .cornerRadius(12)
            .padding(.horizontal)
            .padding(.top, 200.0)

            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(
            Image("EchoBackground")
                .resizable()
                .scaledToFill()
        )
        .ignoresSafeArea()
    }
}

struct ConnectionErrorView_Previews: PreviewProvider {
    static var previews: some View {
        ConnectionErrorView()
    }
}
