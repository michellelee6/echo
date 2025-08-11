//
//  FacesView.swift
//  EchoApp
//
//  Created by Michelle Lee on 7/24/25.
//

import SwiftUI
import PhotosUI // For PhotosPicker if you prefer gallery access, but UIImagePickerController for camera

// MARK: - Person Model
// Represents a person with an ID, name, and optional image data.
struct Person: Identifiable {
    let id = UUID()
    var name: String
    var imageData: Data? // Stores image data for persistence
}

// MARK: - ImagePicker (UIImagePickerControllerRepresentable)
// This bridges UIKit's UIImagePickerController to SwiftUI to access the camera.
struct ImagePicker: UIViewControllerRepresentable {
    @Environment(\.presentationMode) var presentationMode
    var sourceType: UIImagePickerController.SourceType
    @Binding var selectedImage: UIImage?

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = sourceType
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, UINavigationControllerDelegate, UIImagePickerControllerDelegate {
        var parent: ImagePicker

        init(_ parent: ImagePicker) {
            self.parent = parent
        }

        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            if let uiImage = info[.originalImage] as? UIImage {
                parent.selectedImage = uiImage
            }
            parent.presentationMode.wrappedValue.dismiss()
        }

        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.presentationMode.wrappedValue.dismiss()
        }
    }
}

// MARK: - PersonCardView
// A reusable view to display an individual person's image and name.
struct PersonCardView: View {
    let person: Person
    var onEdit: () -> Void // Action for the edit button

    var body: some View {
        VStack {
            ZStack(alignment: .topTrailing) {
                // Person's Image
                if let imageData = person.imageData, let uiImage = UIImage(data: imageData) {
                    Image(uiImage: uiImage)
                        .resizable()
                        .scaledToFill()
                        .frame(width: 100, height: 100)
                        .clipShape(Circle()) // Make it circular
                        .overlay(Circle().stroke(Color.gray.opacity(0.3), lineWidth: 1))
                } else {
                    // Placeholder image if no image data
                    Image(systemName: "person.circle.fill")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 100, height: 100)
                        .foregroundColor(.gray)
                }

                // Edit Button
                Button(action: onEdit) {
                    Image(systemName: "square.and.pencil")
                        .font(.title2)
                        .foregroundColor(.black)
                        .background(Circle().fill(Color.white))
                        .offset(x: 15, y: -20) // Position outside the circle
                }
            }

            // Person's Name
            Text(person.name)
                .font(.headline)
                .foregroundColor(.primary)
                .padding(.top, 5)
        }
        .padding()
        .frame(width: 150, height: 180) // Fixed size for the card
        .background(Color.white)
        .cornerRadius(15)
        .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
    }
}

// MARK: - PeopleView (Main Page)
// The main view for displaying and managing people.
struct PeopleView: View {
    @State private var people: [Person] = [
        Person(name: "Alice", imageData: UIImage(named: "placeholder_alice")?.pngData()),
        Person(name: "Bob", imageData: UIImage(named: "placeholder_bob")?.pngData()),
        Person(name: "Carol", imageData: UIImage(named: "placeholder_carol")?.pngData()),
        Person(name: "David", imageData: UIImage(named: "placeholder_david")?.pngData()),
        Person(name: "Eve", imageData: UIImage(named: "placeholder_eve")?.pngData()),
        Person(name: "Frank", imageData: UIImage(named: "placeholder_frank")?.pngData())
    ] // Example data

    @State private var showingImagePicker = false
    @State private var inputImage: UIImage?
    @State private var newPersonName: String = ""
    @State private var showingAddPersonAlert = false
    @State private var personToEdit: Person? = nil
    @State private var showingEditPersonAlert = false

    var body: some View {
        VStack(alignment: .leading) { // Align content to leading
            // Top Navigation Bar
            HStack(alignment: .center) { // Explicitly set alignment to center
                Text("My People")
                    // .font(.largeTitle)
                    .font(.system(size: 35, weight: .bold))
                    .fontWeight(.bold)
                    .foregroundColor(.black)
                    .padding(.leading, 16.0)
                    // Removed specific top/leading padding from here
                Spacer()

                Button(action: {
                    showingAddPersonAlert = true // Show alert to get name before camera
                }) {
                    Label("Add Person", systemImage: "person.badge.plus")
                        .font(.headline)
                        .padding(.vertical, 12.0) // Adjusted padding to align better
                        .padding(.horizontal, 12)
                        .background(Capsule().fill(Color(red: 0.0, green: 0.39215686274509803, blue: 0.5803921568627451, opacity: 0.5)))
                        .foregroundColor(.black)
                }
            }
            .padding(.horizontal) // Apply horizontal padding to the HStack
            .padding(.top, 40.0) // Apply top padding to the entire HStack

            ScrollView {
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 15) {
                    ForEach(people) { person in
                        PersonCardView(person: person) {
                            personToEdit = person
                            newPersonName = person.name // Pre-fill with current name
                            showingEditPersonAlert = true
                        }
                    }
                }
                .padding(.horizontal) // Apply horizontal padding to the grid
            }
            .padding(.bottom) // Add some padding at the bottom of the scroll view

            Spacer() // Pushes content to the top
        }
        .padding(.top, 70.0)
        .background(
            Image("EchoBackground")
                .resizable()
                .scaledToFill()
        )
        .ignoresSafeArea()
        
        .navigationBarHidden(true) // Hide default navigation bar if this view is presented in a NavigationView
        .sheet(isPresented: $showingImagePicker) {
            ImagePicker(sourceType: .camera, selectedImage: $inputImage)
        }
        .onChange(of: inputImage) { newImage in
            if let newImage = newImage, let imageData = newImage.pngData() {
                if let index = people.firstIndex(where: { $0.id == personToEdit?.id }) {
                    // Editing existing person
                    people[index].imageData = imageData
                } else {
                    // Adding new person
                    people.append(Person(name: newPersonName, imageData: imageData))
                }
                inputImage = nil // Clear the image
                newPersonName = "" // Clear the name
                personToEdit = nil // Clear person being edited
            }
        }
        .alert("Add New Person", isPresented: $showingAddPersonAlert) {
            TextField("Enter name", text: $newPersonName)
            Button("Add") {
                if !newPersonName.isEmpty {
                    // Proceed to camera only if name is provided
                    showingImagePicker = true
                }
            }
            Button("Cancel", role: .cancel) {
                newPersonName = "" // Clear name on cancel
            }
        } message: {
            Text("Please enter the name of the new person.")
        }
        .alert("Edit Person", isPresented: $showingEditPersonAlert) {
            TextField("Edit name", text: $newPersonName)
            Button("Update Name") {
                if let index = people.firstIndex(where: { $0.id == personToEdit?.id }) {
                    people[index].name = newPersonName
                }
                newPersonName = ""
                personToEdit = nil
            }
            Button("Change Photo") {
                showingImagePicker = true // Open camera to change photo
            }
            Button("Delete Person", role: .destructive) {
                if let index = people.firstIndex(where: { $0.id == personToEdit?.id }) {
                    people.remove(at: index)
                }
                newPersonName = ""
                personToEdit = nil
            }
            Button("Cancel", role: .cancel) {
                newPersonName = ""
                personToEdit = nil
            }
        } message: {
            Text("Edit the person's details.")
        }
    }
}

// MARK: - Preview Provider
struct PeopleView_Previews: PreviewProvider {
    static var previews: some View {
        PeopleView()
            // .background(Image("EchoBackground"))
    }
}

