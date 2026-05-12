document.getElementById("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("fileInput");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    // Basic client-side validation
    if (!fileInput.files[0]) {
        alert("Please select a file to upload.");
        return;
    }
    if (!fileInput.files[0].name.endsWith('.ics')) {
        alert("Please upload a valid .ics file.");
        return;
    }
    const res = await fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Failed to save event');
            });
        }
        alert('Successfully imported calendar!')
    })
    .catch(error => {
        alert('Error importing calendar: ' + error.message);
    });
    // const data = await res.json();
    // console.log(data.events);
});

document.getElementById("exportBtn").addEventListener("click", async () => {
  fetch("/export/ics", {
    method: "GET"
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(data => {
        throw new Error(data.error || "Export failed");
      });
    }

    return response.blob(); // important for file download
  })

  .then(blob => {
    if (!blob || blob.size === 0) {
      throw new Error("Export file is empty");
    }
    
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "calendar.ics";
    document.body.appendChild(a);
    a.click();
    a.remove();

    window.URL.revokeObjectURL(url);
  })
  .catch(error => {
    alert("Error exporting calendar: " + error.message);
  });
});