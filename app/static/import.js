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