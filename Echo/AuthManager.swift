//
//  AuthManager.swift
//  EchoApp
//
//  Created by Michelle Lee on 7/26/25.
//

import Foundation
import AuthenticationServices

class AuthManager: NSObject, ObservableObject {
    @Published var isSignedIn = false
    @Published var userIdentifier: String?

    private var currentNonce: String?

    func startSignInWithAppleFlow() {
        let request = ASAuthorizationAppleIDProvider().createRequest()
        request.requestedScopes = [.fullName, .email]

        let controller = ASAuthorizationController(authorizationRequests: [request])
        controller.delegate = self
        controller.presentationContextProvider = self
        controller.performRequests()
    }
}

extension AuthManager: ASAuthorizationControllerDelegate {
    func authorizationController(controller: ASAuthorizationController, didCompleteWithAuthorization authorization: ASAuthorization) {
        if let appleIDCredential = authorization.credential as? ASAuthorizationAppleIDCredential {
            let userID = appleIDCredential.user
            self.userIdentifier = userID
            self.isSignedIn = true

            // You can also extract: fullName, email, identityToken, etc.
            print("Apple ID Credential Authorized: \(userID)")
        }
    }

    func authorizationController(controller: ASAuthorizationController, didCompleteWithError error: Error) {
        print("Authorization failed: \(error.localizedDescription)")
        self.isSignedIn = false
    }
}

extension AuthManager: ASAuthorizationControllerPresentationContextProviding {
    func presentationAnchor(for controller: ASAuthorizationController) -> ASPresentationAnchor {
        return UIApplication.shared.windows.first { $0.isKeyWindow }!
    }
}
