function getFileName() {
  var x = document.getElementById('fileInput');
  document.getElementById('fileName').innerHTML = x.value.split('\\').pop();
}

function showGenderForm() {
  var genderForm = document.getElementById('genderForm');
  genderForm.style.display = 'block';
}

function hideGenderForm() {
  var genderForm = document.getElementById('genderForm');
  genderForm.style.display = 'none';
}

function getSelectedGender() {
  var maleGender = document.getElementById('maleGender');
  var femaleGender = document.getElementById('femaleGender');
  var unknownGender = document.getElementById('unknownGender');

  if (maleGender.checked) {
    return 'Male';
  } else if (femaleGender.checked) {
    return 'Female';
  } else if (unknownGender.checked) {
    return 'Unisex';
  }

  return null;
}

function resetGenderSelection() {
  var genderForm = document.getElementById('genderForm');
  var radioInputs = genderForm.getElementsByTagName('input');
  for (var i = 0; i < radioInputs.length; i++) {
    radioInputs[i].checked = false;
  }
  hideGenderForm();
}

function uploadImage() {
  var fileInput = document.getElementById('fileInput');
  var file = fileInput.files[0];

  if (file) {
    var selectedGender = getSelectedGender();

    if (selectedGender) {
      var formData = new FormData();
      formData.append('file', file);
      formData.append('gender', selectedGender);

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

          // Reset file input and gender selection
          fileInput.value = null;
          document.getElementById('fileName').innerHTML = '';
          resetGenderSelection();
        } else {
          // Handle upload error
          console.error('Error uploading file');
        }
      };
      xhr.onerror = function () {
        console.error('Error uploading file');
      };
      xhr.send(formData);
    }
  }
}
