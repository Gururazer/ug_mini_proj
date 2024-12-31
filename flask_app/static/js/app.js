document.addEventListener("DOMContentLoaded", () => {
    const resultContainer = document.getElementById("result-container");
    const resultImage = document.getElementById("result-image");
    const resultVideo = document.getElementById("result-video");

    // Function to display the detection result
    function showResult(resultType, resultPath) {
        resultImage.style.display = "none";
        resultVideo.style.display = "none";

        if (resultType === "image") {
            resultImage.src = resultPath;
            resultImage.style.display = "block";
        } else if (resultType === "video") {
            resultVideo.querySelector("source").src = resultPath;
            resultVideo.load(); // Reload the video
            resultVideo.style.display = "block";
        }

        resultContainer.style.display = "block";
    }

    // Listen for form submissions and handle them via AJAX
    document.querySelectorAll("form").forEach(form => {
        form.addEventListener("submit", event => {
            event.preventDefault(); // Prevent normal form submission
            const formData = new FormData(form);
            const action = form.action;

            fetch(action, {
                method: "POST",
                body: formData,
            })
                .then(response => response.ok ? response.blob() : Promise.reject(response.status))
                .then(blob => {
                    const resultURL = URL.createObjectURL(blob);
                    const isImage = form.id === "image-form"; // Check form type
                    showResult(isImage ? "image" : "video", resultURL);
                })
                .catch(error => {
                    alert(`Error: ${error}`);
                });
        });
    });
});
