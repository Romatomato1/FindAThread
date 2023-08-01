let selectedImage = null;

function handleImageClick(image, gender, color, description) {
    if (selectedImage) {
        selectedImage.classList.remove("selected");
    }
    selectedImage = image;
    selectedImage.classList.add("selected");

}

function hideImageInfo() {
    const itemDetails = document.querySelectorAll(".item-details");
    itemDetails.forEach((item) => {
      item.style.display = "none";
    });
  }
  
  function displayImageInfo(event, itemData) {
    hideImageInfo();
    const itemDetails = event.currentTarget.querySelector(".item-details");
    itemDetails.style.display = "block";
  }

function validateForm() {
    if (!selectedImage) {
    alert("Please select an image.");
     return false;
    }
    return true;
}

function deleteSelectedImage() {
    if (selectedImage) {
    const imageURL = selectedImage.getAttribute("src");
    if (confirm("Are you sure you want to delete this image?")) {
        fetch('/delete_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ imageURL: imageURL })
        })
        .then(response => {
        if (response.ok) {
            selectedImage.parentElement.remove(); // Remove the image container from the page
            selectedImage = null; // Clear the selected image
        } else {
            alert("Failed to delete image.");
        }
        })
        .catch(error => {
        console.error("Error:", error);
        alert("An error occurred. Please try again later.");
        });
    }
    } else {
    alert("Please select an image to delete.");
    }
}