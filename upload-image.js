function getFileName() {
  var x = document.getElementById('fileInput');
  document.getElementById('fileName').innerHTML = x.value.split('\\').pop();
}

function uploadImage() {
  var fileInput = document.getElementById('fileInput');
  var file = fileInput.files[0];

  if (file) {
    var formData = new FormData();
    formData.append('file', file);

    var xhr = new XMLHttpRequest();
    xhr.open('POST', baseUrl + 'upload', true);
    xhr.onload = function () {
      if (xhr.status === 200) {
        var response = JSON.parse(xhr.responseText);
        if (response.status === 'duplicate') {
          // Handle duplicate image case
          Toastify({
            text: 'Image already uploaded',
            duration: 3000,
            gravity: 'top',
            position: 'left',
            backgroundColor: 'linear-gradient(to right, #ff4b1f, #ff9068)',
          }).showToast();

        } else if (response.status === 'success') {
          // Show success message using Toastify
          Toastify({
            text: 'File uploaded successfully',
            duration: 3000,
            gravity: 'top',
            position: 'left',
            backgroundColor: 'linear-gradient(to right, #00b09b, #96c93d)',
          }).showToast();
        }
            // Reset file input
            fileInput.value = null;
            document.getElementById('fileName').innerHTML = '';
            
      } else {
        // Handle upload error
        console.error('Error uploading file');
      }
    };
    xhr.onerror = function () {
      console.error('Error uploading file');
    };
    xhr.send(formData);
  } else {
    console.log('No file selected');
  }
}
